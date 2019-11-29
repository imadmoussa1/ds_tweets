# This template relies on the Python 3 alpine Docker image below
FROM python:3.7
LABEL maintainer="imadmoussa1@gmail.com"
# Create the application folder
RUN mkdir -p /var/app
# Set the application volume
VOLUME ["/var/app"]

WORKDIR /var/app

# Copy the requirements will be using
COPY requirements.txt /var/app
# COPY run.sh /var/app
# Install the libraries
RUN python3 -m pip install -r requirements.txt

# Run the flask dev server
# ENV FLASK_APP=main.py
# CMD flask run -h 0.0.0.0 -p 5000
# Run using uwsgi
# CMD ["uwsgi", "--ini", "uwsgi.ini"]
CMD "./run.sh"