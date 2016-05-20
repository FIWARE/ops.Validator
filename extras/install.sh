#!/usr/bin/env bash
# install dependencies
apt-get update -y
apt-get install -y wget tar git curl nano wget dialog net-tools build-essential subversion python python-dev python-distribute python-pip libffi-dev libssl-dev
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-engine

cd ..
pip install --upgrade pip setuptools
pip install -r requirements.txt