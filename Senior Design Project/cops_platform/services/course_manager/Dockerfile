# Based on the official CentOs 7 Docker image
FROM centos:centos7

# Installations needed for OS
RUN yum -y install python3
RUN yum -y install postgresql-server sudo
RUN sudo -u postgres /usr/bin/initdb /var/lib/pgsql/data/
RUN sudo -u postgres /usr/bin/pg_ctl -D /var/lib/pgsql/data start
RUN sudo yum -y install gcc
RUN sudo yum -y install python3-devel
RUN sudo yum -y install postgresql-libs
RUN sudo yum -y install postgresql-devel

# Creates and changes directory to course_manager
WORKDIR /home/course_manager

# Copies the requirements.txt file, creates virtual environment, and installs libraries on virtual environment
COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt

# Copies the required directories to run the Course Manager app
COPY app app
COPY __init__.py config.py course_manager.py ./
COPY boot.sh ./

# Allows user execution for boot.sh
RUN chmod +x boot.sh

# Sets environmental variables
ENV LC_ALL en_US.UTF-8
ENV FLASK_APP course_manager.py
ENV FLASK_CONFIG development
ENV PYTHONUNBUFFERED 0

# Exposes this container on port 5000 for the host
EXPOSE 5000

# Runs the boot.sh script when container launches
ENTRYPOINT ["./boot.sh"]



