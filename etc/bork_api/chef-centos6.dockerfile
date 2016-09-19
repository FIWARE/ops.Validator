# Dockerfile to deploy a valid chef-solo container
# tag: pmverdugo/chef-centos6
FROM centos:centos6
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# Update packages
RUN yum -y update; yum clean all

# ChefDK install
RUN rpm -ivh https://packages.chef.io/stable/el/6/chefdk-0.12.0-1.el6.x86_64.rpm

# Bash command prompt by default
CMD ["/bin/bash"]
