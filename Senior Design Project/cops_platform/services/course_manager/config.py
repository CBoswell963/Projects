"""
Course Manager Config

Responsible for configuring the static settings for the course manager app when it is initialized.
Sets these values based on the corresponding OS environment variables.

"""

import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base class for Config.
    """
    # The role of the user for this instance of the running application
    # Defaults to 'student' (least privilege) if no ROLE env is provided
    ROLE = os.environ.get('ROLE') or 'student'
    # Does not track modifications in SQLALCHEMY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Does not refresh a session each request in order to track inactivity
    SESSION_REFRESH_EACH_REQUEST = False
    # The permanent lifetime of a session; used to track inactivity of a user
    # Defaults to 20 minutes if no corresponding env is provided
    PERMANENT_SESSION_LIFETIME = os.environ.get('SESSION_LIFETIME') or timedelta(minutes=20)

    @staticmethod
    def init_app(app):
        pass


class PostgresConfig(Config):
    """
    Sets the SQLALCHEMY_DATABASE_URI to the postgres database based on the four required environment variables.
    """
    POSTGRES_URL = os.environ.get("POSTGRES_URL")  # uses the default port 5432
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PW = os.environ.get("POSTGRES_PW")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")

    DB_URL = None

    # Checks if all the environment variables have been set for the Postgres DB connection
    if POSTGRES_URL is None or POSTGRES_USER is None or POSTGRES_PW is None or POSTGRES_DB is None:
        pass
    else:
        DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PW,
                                                                       url=POSTGRES_URL, db=POSTGRES_DB)

    # Uses sqlite test DB instead if variables needed for Postgres have not been set
    SQLALCHEMY_DATABASE_URI = DB_URL or \
        'sqlite:///' + os.path.join(basedir, 'test.db')


class SqliteConfig(Config):
    """
    Sets the SQLALCHEMY_DATABASE_URI to the sqlite testing database.
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test.db')


"""
Each config string key and the corresponding Config class it will create.
"""
config = {
    'development': PostgresConfig,
    'testing': SqliteConfig,
    'default': SqliteConfig
}
