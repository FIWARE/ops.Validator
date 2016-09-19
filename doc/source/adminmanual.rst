..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

======================================
Installation and Administration manual
======================================

Installation
============

To run the code you can clone the git repo with:

::

    git clone git@github.com:ging/fiware-validator.git


Installing Dependencies
-----------------------

To install package dependencies you must run:

::

    pip install -r requirements.txt


Deployment
==========
The system is deployed as two different projects, that can be installed and run in different locations.
The API and WebUI can be run by executing the following command:

::

    ./run_all.sh

Or separately by running:
::

    /usr/bin/python validator_api/manage.py


for the RESTful API, and
::

    /usr/bin/python validator_webui/manage.py

for the WebUI

Sanity Check Procedures
=======================

Running processes
-----------------

The running processes for the RESTful API should only be
::

    /usr/bin/python validator_api/manage.py

Similarly, the WebUI is contained in the proccess
::

    /usr/bin/python validator_webui/manage.py

Network Interfaces Up and Open
------------------------------

The system only uses a TCP listener port linked on all interfaces.
By default the port number is 4042, but it can be changed via the aforementioned config file.

Databases
---------

The RESTful API uses a minimal sqlite based db for results buffering and storage, contained by default in the file validator.sqlite3

Diagnosis Procedures
====================
The Diagnosis Procedures are the first steps that a System Administrator will take to locate the source of an error in a GE.
Once the nature of the error is identified with these tests, the system admin will very often have to resort to more concrete and specific testing to pinpoint the exact point of error and a possible solution.
Such specific testing is out of the scope of this section.

Resource availability
---------------------

The system requires a functional FIWARE IdM server for authentication, with a valid and updated user list.
The system also requires an accessible docker server.

Remote Service Access
---------------------
The system deployment depends on several external services for successful completion.
The dependency list reads as follows:

- FIWARE IdM server:
    Used for authenticating users

- Docker daemon:
    Used to deploy the test images

Resource consumption
--------------------
The system runs as a couple of lightweigth python processes, so the typical memory usage should not surpass 20MB while running.
The cpu usage should be none while listening, and should behave as a short activy spike when attending/processing.

I/O flows
---------
    - The user accesses the WebUI url
    - The WebUI requests the available images and deployment artifacts for the given user, by connecting to the API via port 4042
    - The API connects to the IdM server for authentication
        - The IdM server responds
    - The API connects to the docker server for deployment
        - The docker server responds
    - The API responds to the WebUI
    - The WebUI shows the results to the user

License
=======

Apache License Version 2.0 http://www.apache.org/licenses/LICENSE-2.0

