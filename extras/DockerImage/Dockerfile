############################################################
# Dockerfile for Chef Validator API
# Based on Ubuntu
############################################################

FROM ubuntu:14.04
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# environment configuration
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y wget tar git curl nano wget dialog net-tools build-essential subversion && \
    apt-get install -y python python-dev python-distribute python-pip && \
    apt-get install -y libffi-dev libssl-dev


# Validator install
RUN git clone https://github.com/ging/fiware-validator /opt/fiware-validator && \
    pip install --upgrade pip && \
    pip install -r /opt/fiware-validator/requirements.txt

EXPOSE 4042
WORKDIR /opt/fiware-validator
ENV PYTHONPATH $PYTHONPATH:/opt/fi-ware-validator/bork
CMD ["python", "./bork/command/validator-api.py", "--config-dir=etc/bork"]
