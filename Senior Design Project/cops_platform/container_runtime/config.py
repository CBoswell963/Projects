"""
Container Runtime Config

Responsible for configuring the static settings for the container runtime app when it is initialized.
Sets these values based on the corresponding OS environment variables.

"""

import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base class for Config.
    """
    # Whether SELinux is enforced or not
    # If this environment variable contains any value (not null) - will run with SELinux enforced
    ENFORCED = os.getenv("ENFORCED")
    # Disables due to significant overhead this adds
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class PostgresConfig(Config):
    """
    Sets the SQLALCHEMY_DATABASE_URI to the Postgres Database connection for the host machine.
    """
    POSTGRES_URL = os.environ.get("POSTGRES_URL")  # uses the default port 5432
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PW = os.environ.get("POSTGRES_PW")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")

    DB_URL = None

    # If all the required env have not been set - exits with a error message
    if POSTGRES_URL is None or POSTGRES_USER is None or POSTGRES_PW is None or POSTGRES_DB is None:
        print("Postgres Connection environment variables have not been set.")
        print("Requires the following envs:")
        print("POSTGRES_USER")
        print("POSTGRES_PW")
        print("POSTGRES_URL")
        print("POSTGRES_DB")
        sys.exit(0)
    else:
        DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PW,
                                                                       url=POSTGRES_URL, db=POSTGRES_DB)

    SQLALCHEMY_DATABASE_URI = DB_URL


"""
Each config string key and the corresponding Config class it will create.
"""
config = {
    'default':  PostgresConfig
}
