# Flask Api Template
## Introduction
This project is a Restfull api based on Flask framework using docker.
This Project is a template that will help you to generate an api using flask, python, docker, postgres, MongoDB, and JWT for authentication.

We added uWSGI, Nginx, Certbot for SSL and all this with docker.
So you can use this template application on production env with SSL.
## Docker
we build a flask image based on python 3 alpine with the requirements needed in the requirement.txt file.
### Docker compose
in docker compose we run our architecture with 4 more images than the flask one,
postgres, pgadmin, MongoDB and mongo chart.
Before Runing the compose file you should set the secrets and config file
copy it form .txt.sample to .txt

## Run the project with http (NGINX)
You can run it using the docker compose, and send requests on localhost/api/.../

## Generate Certification for https
we are using letsencrypt to generate the certification.
Run chmod +x init-letsencrypt.sh and sudo ./init-letsencrypt.sh to save the certification in data file and it will be used by certbot in docker.
