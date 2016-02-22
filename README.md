# J.A.W.S
Just Another Web Service

This is a test project for building 'microservices' in a 'choregraphed' way.

The idea is that a user will input some data into a website and upon submiting that data a sereis of services are executed.  Specifically like this:

The user sends data from app_user to app_external and all the data from app_external (and app_user) gets sent to app_models which calculates a result based on all that data and sends it back to app_user.

The app_user code is primarly for interfacing with the user and serving the relevant html.

The app_external represents 'an external service' (like FaceBook or another third party API) that we don't have 'server side' access to.

The app_models is for calculating (aggregating) the results from app_external as well as some of its own 'secret sauce.'

There are various TODO notes in the code that suggest where code needs to be modified to build out this type of services architecture.

To start the services, from the root of the project simply run:

$ supervisord


Requires:

python3.5

supervisord via:
    sudo apt-get install -y supervisor

commands:
$ supervisord
$ pkill supervisor
