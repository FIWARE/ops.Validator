# Dockerfile to deploy a valid chef-solo container
# tag: pmverdugo/puppet-centos6

FROM centos:centos6
MAINTAINER Pedro Verdugo <pmverdugo 'at' dit.upm.es>

# Update packages
RUN yum -y update; yum clean all

# Install puppet
RUN rpm -ivh http://yum.puppetlabs.com/puppetlabs-release-el-6.noarch.rpm

# Bash command prompt by default
CMD ["/bin/bash"]