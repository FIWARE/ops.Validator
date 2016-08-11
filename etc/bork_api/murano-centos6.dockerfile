# Dockerfile to deploy a valid murano container
# tag: pmverdugo/murano-centos6

FROM centos:centos6
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# Update packages
RUN yum -y update; yum clean all

# Install dependencies
RUN yum install gcc python-setuptools python-devel; sudo easy_install pip
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

# Bash command prompt by default
CMD ["/bin/bash"]