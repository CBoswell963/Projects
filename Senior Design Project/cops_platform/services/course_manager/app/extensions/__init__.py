"""
Contains extension variables to be used statically in the main Flask app.
These must be declared in a separate Python class, otherwise they
cause conflicts with unit tests with Flask.
"""
from flask_restful import Api

# The api object which contains all API endpoints routes for this app
api = Api()
