# Dockerfile to deploy a valid murano container
# tag: pmverdugo/murano-ubuntu12

FROM ubuntu:12.04
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# environment configuration
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y wget

# Install dependencies
RUN apt-get update && \
    apt-get install -y python-pip python-dev \
    libmysqlclient-dev libpq-dev \
    libxml2-dev libxslt1-dev \
    libffi-dev
RUN pip install tox

# Install Murano
RUN mkdir ~/murano && \
    cd ~/murano && \
    git clone git://git.openstack.org/openstack/murano

# Configure Murano
RUN cd ~/murano/murano && \
    tox -e genconfig && \
    cd ~/murano/murano/etc/murano && \
    ln -s murano.conf.sample murano.conf && \
    tox  && \
    tox -e venv -- murano-db-manage \
    --config-file ./etc/murano/murano.conf upgrade

# Run Murano
RUN tox -e venv -- murano-api --config-file ./etc/murano/murano.conf


WORKDIR '~/murano/murano'