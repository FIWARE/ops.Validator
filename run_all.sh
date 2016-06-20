#!/usr/bin/env bash
PYTHONPATH= "/usr/local/lib/python2.7/site-packages"
PYTHONPATH="$PYTHONPATH:/home/ubuntu/fiware_validator/validator_api"
PYTHONPATH="$PYTHONPATH:/home/ubuntu/fiware_validator/validator_webui"
export $PYTHONPATH

nohup python -u /home/ubuntu/fiware_validator/validator_api/manage.py runserver 0.0.0.0:4042 &
nohup python -u /home/ubuntu/fiware_validator/validator_webui/manage.py runserver 0.0.0.0:4043 &
