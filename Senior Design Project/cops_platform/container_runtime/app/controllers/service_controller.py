from flask_restful import Resource, reqparse, abort
from ...app import get_docker_client
from threading import Thread
import requests
from signal import signal, SIGINT
from sys import exit
import time
from flask import make_response, current_app
from ...app.utils.service_util import services
from ...app import get_enforced_status, db

# For running the ip labeling script
import subprocess

# List of all currently running health check threads
health_check_threads = []


# Clears the ip for the given container
def clear_ip(container):
    docker_client = get_docker_client()
    container = docker_client.containers.get(container.name)
    if get_enforced_status():
        subprocess.call(["./clearlabel", container.attrs['NetworkSettings']['IPAddress']])


def tear_down_handler(signal_received, frame):
    """
    Called when the Container Runtime process is to be stopped running.
    Gracefully closes all currently running health check threads, stops
    any currently containers, and removes the stored container images.
    Closes the connection used for the the Docker client to the Docker daemon.
    :param signal_received: Unused
    :param frame: Unused
    """
    print('SIGINT or CTRL-C detected. Exiting gracefully')

    for thread in health_check_threads:
        thread.join(10)

    docker_client = get_docker_client()
    containers = docker_client.containers.list()

    for container in containers:
        if container.status != 'stopped':
            clear_ip(container)
            print("Stopping container " + container.name)
            container.stop()
            print("Container stopped.")

    docker_client.containers.prune()
    docker_client.close()
    exit(0)


def obtain_authorization_level(username):
    """
    Authenticates and obtains the Authorization level of the user.
    Currently, does this by viewing each database user table in the Postgres DB
    starting from least privilege. If a matching user is found, returns the authorization
    levels based on their role.
    NOTE: In the real COPS Platform a IdAM service will be used instead
    :param username: the username of this user.
    :return: the authorization levels of the user. Currently this is 'student', 'instructor', or 'coordinator'
    If no matching user is found, 'None' is returned.
    """
    results = db.session.execute("""
        SELECT username FROM STUDENT where username=:username LIMIT 1
        """, {'username': username}).first()
    if results and results[0] == username:
        return "student"

    results = db.session.execute("""
        SELECT username FROM INSTRUCTOR where username=:username LIMIT 1
        """, {'username': username}).first()
    if results and results[0] == username:
        return "instructor"

    results = db.session.execute("""
        SELECT username FROM COORDINATOR where username=:username LIMIT 1
        """, {'username': username}).first()
    if results and results[0] == username:
        return "coordinator"
    return None


"""
Signal to call the tear_down_handler function when this running
program is terminated (CTRL-C or SIGINT fired)
"""
signal(SIGINT, tear_down_handler)


class ServiceRequest(Resource):
    """
    Handler for the Service Request to the Container Runtime.
    """

    def post(self):
        """
        - Handles the user's service request.
        - Requires the service and username values as form data in the body of the POST request.
        - Authenticates and gets the user's authorization levels (as SELinux labels) using the IAM system.
         (NOTE: Using a Mock IAM system for now.)
        - Creates the container to run the requested web service with the authorized security labels for this
         user enforced.
        - Logs the user in the web service, and forwards the response (with the session cookie) back to the user,
          along with redirect for the url with port number that the user will need to connect to service.
        - Creates a Health Check Thread to monitor the lifecycle of the running container. Shuts down the container
          once the user logs our or disconnects from the running service.

        :return: Response of whether service request was successful. If successful returns forwarded response from
        connected service (including session cookie), along with the url of the service. If unsuccessful returns error
        message to user.
        """

        # Gets the Docker client
        docker_client = get_docker_client()

        # Retrieves the service and username parameters from the body of the request
        parser = reqparse.RequestParser()
        parser.add_argument('service', location='form')
        parser.add_argument('username', location='form')
        args = parser.parse_args()
        username = args.username
        service = args.service

        # Check if the service requested is valid
        if service not in services:
            abort(400, message="This is not a valid service")

        # Using Mock IAM, authenticate user and retrieve SELinux security labels for this user
        security_label = obtain_authorization_level(username)
        if security_label is None:
            abort(400, message="Given credentials are not valid")

        # Retrieves the service static configuration class for this specific service
        service_class = services[service]

        # Security check, make sure user is not already connected to another running container for the service requested
        for user in service_class.active_users:
            if username == user:
                abort(400, message="User already has an active session for this service")

        # Lock used to prevent conflicting port numbers for running services
        service_class.port_lock.acquire()

        # Get current port for this service
        port = service_class.current_port

        # Creates a service object based on the static config service class
        service_object = service_class(host_port=str(port))

        ports = {service_object.port: port}

        # Increment current port value
        service_class.current_port = port + 1

        # Release lock
        service_class.port_lock.release()

        # Retrieve name of container for this service
        container_name = service_object.container

        # Sets the ROLE environment variable for the Docker Container to the security_label for this user
        # Along with the POSTGRES env for the DB connection.
        # These are using all the same ones from the host machines with the exception of POSTGRES_URL
        # POSTGRES_URL corresponds to the docker0 interface URL the Docker Containers use to connect to the Host
        env = {"ROLE": security_label, "POSTGRES_DB": current_app.config['POSTGRES_DB'],
               "POSTGRES_USER": current_app.config['POSTGRES_USER'],
               "POSTGRES_URL": '172.17.0.1',
               "POSTGRES_PW": current_app.config['POSTGRES_PW']}

        # Start the running container in detached mode at the unique port
        container = docker_client.containers.run(container_name, detach=True, ports=ports, environment=env)

        # TODO: Do this in a way that is generic and not hardcoded
        # Waits until the service running inside the container has been started
        # NOTE: Due to this not being inside an exception, you can occasionally get weird
        # errors where you are constantly waiting for a connection. This normally due
        # the connection not being labeled with SELinux. Due to time constraints we did not have time to fix this.
        # Best solution would to be to try to connect the running application multiple times with successive requests.
        # If it can't reach the connection in a certain time frame, then return an error response back to the user.
        while True:
            logs = docker_client.containers.get(container.name).logs(stream=True)
            found = False
            for log in logs:
                log = str(log)
                if "Running" in log:
                    found = True
                    break
            if found:
                break

        # Retrieves the container's IP address from the the now running container
        container_ip = docker_client.containers.get(container.name).attrs['NetworkSettings']['IPAddress']

        # If running with SELinux, labels this Docker Container's IP connection based on the user's authorization levels
        if get_enforced_status():
            subprocess.check_call(["./iplabel", container_ip, security_label])

        # Attempts to send login request for this user to the now started service
        try:
            login_url = service_object.login_url
            data = {"username": username}

            # Response from the request
            response = requests.post(login_url, data=data)

            # If response is not successful, return an error message to user
            if response.status_code != 200:
                abort(400, message="Service request failed")
                clear_ip(container)
                container.stop()
                exit(1)

            # Create response to forward to client
            client_response = make_response({'message': "Service request was successful",
                                             'url': service_object.base_url})

            # Include session cookie in forwarded response
            client_response.set_cookie("session", response.cookies.get("session"))

        # If any exception occurs (such as cannot connect to this container or service),
        # returns an error message to the user, and shuts down the container.
        except Exception as e:
            print(e)
            abort(400, message="Service request failed")
            clear_ip(container)
            container.stop()
            exit(1)

        # Add user to the list of active sessions for this service
        service_class.active_users.append(username)

        # Initialize and start the health check thread to monitor this running session in the container
        health_check_thread = HealthCheckThread(service_class, username, service_object.health_check_url, container)
        health_check_thread.start()

        # Add to the list of running health check threads
        health_check_threads.append(health_check_thread)

        # Return a forwarded response from the successful connection to the web service.
        return client_response


class HealthCheckThread(Thread):
    """
    A thread used to monitor the health of a running container.
    """

    def __init__(self, service, username, url, container):
        """
        Creates a HealthCheckThread with the passed in parameters.
        :param service: the service class for the service that is running on the container
        :param username: the username of the logged in user for the session of this service
        :param url: the health-check url endpoint for this service
        :param container: the container that is running this service
        """
        Thread.__init__(self)
        self.service = service
        self.username = username
        self.url = url
        self.container = container

    def run(self):
        """
        Runs this health check thread to monitor the container.
        """

        # Checks the health check endpoint every 30 second until the user's session ends
        # or a networking error occurs
        while True:

            time.sleep(30)

            try:
                # Attempt to access the health check endpoint
                response = requests.get(self.url)

            # If can't reach the endpoint, shut down the container
            except Exception as e:
                self.tear_down()
                clear_ip(self.container)
                self.container.stop()
                return

            # This session is longer active for this user
            if response.status_code != 200:
                print('User has disconnected')
                break

        # Stop the running container and tear down the thread
        self.tear_down()
        print("Container is being shut down!")
        clear_ip(self.container)
        self.container.stop()
        return

    def tear_down(self):
        """
        Called before the thread is to be exited.
        """
        # Removes the user for this session from the list of active users for this session
        self.service.active_users.remove(self.username)
        # Removes this thread from the list of health check threads
        health_check_threads.remove(self)
