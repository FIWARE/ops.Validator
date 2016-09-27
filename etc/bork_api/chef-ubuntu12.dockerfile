# Dockerfile to deploy a valid chef-solo container
# tag: pmverdugo/chef-ubuntu12

FROM ubuntu:12.04
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# Needed for Chef 12
RUN locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8
ENV LC_ALL C
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

# Packages update
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        wget \
        git

# ChefDK install
RUN cd /tmp && \
    wget --no-check-certificate https://packages.chef.io/stable/ubuntu/12.04/chefdk_0.12.0-1_amd64.deb && \
    dpkg -i chefdk_*.deb && \
    echo 'gem: --no-ri --no-rdoc' > ~/.gemrc

# knife github helper gem
RUN /opt/chefdk/embedded/bin/gem install knife-github-cookbooks && \
    mkdir /var/chef && \
    mkdir /etc/chef && \
    mkdir /var/chef/cookbooks  && \
    cd /var/chef/cookbooks && \
    git init && \
    git config user.name "demo" && \
    git config user.email "demo@here" && \
    touch .dummy  && \
    git add .dummy && \
    git commit -a --allow-empty-message -m '' && \
    rm -rf /tmp/*

# Configure Chef-solo
RUN echo 'cookbook_path "/opt/cookbooks"\nlog_level :debug' > /etc/chef/solo.rb

# Set the default directory where CMD will execute
WORKDIR /opt/cookbooks

# Bash command prompt by default
CMD ["/bin/bash"]