# Dockerfile to deploy a valid puppet self-service container
# tag: pmverdugo/puppet-ubuntu12

FROM ubuntu:12.04
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# environment configuration
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y wget

# Puppet install
RUN wget http://apt.puppetlabs.com/puppetlabs-release-trusty.deb && \
    dpkg -i puppetlabs-release-trusty.deb && \
	apt-get update && \
    apt-get -y install puppetmaster
	
# environment cleanup
RUN rm puppetlabs-release-trusty.deb && \
    apt-get clean

WORKDIR '/etc/puppet'