FROM ubuntu:14.04
MAINTAINER pmverdugo "pmverdugo at dit.upm.es"
ENV DEBIAN_FRONTEND noninteractive

# update packages
RUN ulimit -n 1000 && \
    echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu trusty-updates/juno main" > /etc/apt/sources.list.d/juno.list &&\
    apt-get update -yqq && \
    apt-get install -yq software-properties-common

# install packages
RUN apt-get -y install \
	    ubuntu-cloud-keyring \
		mysql-client \
		keystone \
		python-keystoneclient \
		python-mysqldb &&\
    apt-get clean && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -f /var/lib/keystone/keystone.db

VOLUME /etc/keystone
EXPOSE 5000 35357

# copy sql script
COPY keystone.sql /root/keystone.sql

# copy keystone config file
COPY keystone.conf /etc/keystone/keystone.conf

# add bootstrap script and make it executable
COPY bootstrap.sh /etc/bootstrap.sh
RUN chown root.root /etc/bootstrap.sh && chmod a+x /etc/bootstrap.sh
ENTRYPOINT ["/etc/bootstrap.sh"]
