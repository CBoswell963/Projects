from flask_restful import Resource
from ...app import get_username


class HealthCheck(Resource):
    """
    Checks the health of the running service.
    Used by the Container Runtime module to know when
    the user has disconnected from the service or an error has occurred.
    """

    def get(self):
        """
        GET request to the health check endpoint: "/api/health_check"
        Returns whether the user is currently still using this service or not.
        :return: Status code and message for whether the user is still in session for this service.
        """
        username = get_username()

        if username is not None:
            return "Success"
        return "Unsuccessful", 400
