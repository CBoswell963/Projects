from abc import ABC
from threading import Lock


class ServiceConfig(ABC):
    """
    Abstract Config class for a Service.
    """

    def __init__(self, port, host, container, base_url, login_url, health_check_url):
        """
        Initialize the Service Config class with the passed in parameters.
        :param port: the port this service listens on in the container
        :param host: the host for this service
        :param container: the container name for this service
        :param base_url: the base url for this service (host + post)
        :param login_url: the url used for logging in a user for this service
        :param health_check_url: the url used for checking the health of the container running this service
        """
        self.port = port
        self.host = host
        self.container = container
        self.base_url = base_url
        self.login_url = login_url
        self.health_check_url = health_check_url
        super().__init__()


class CourseManagerServiceConfig(ServiceConfig):
    """
    Course Manager Service Config class.
    """
    # Lock used to make sure a unique port is assigned to each running service
    port_lock = Lock()
    # Static value for the current_port number of this service
    current_port = 8000
    # List of active users for this service
    active_users = []

    def __init__(self, host_port):
        """
        Initializes the Course Manager Service Config class.
        :param host_port: the unique port this container service's is mapped to on the host machine
        """
        port = '5000/tcp'
        host = 'http://127.0.0.1'
        container = 'course_manager_test'
        base_url = 'http://127.0.0.1:' + host_port
        login_url = '/api/login'
        health_check_url = '/api/health_check'
        super().__init__(port=port, host=host, container=container, base_url=base_url,
                         login_url=base_url + login_url, health_check_url=base_url + health_check_url)


"""
Each service's string value mapped to the corresponding config class it will create
"""
services = {
    'course_manager': CourseManagerServiceConfig
}
