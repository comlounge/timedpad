#!/bin/bash

cd /home/cs/prj/timedpad
source bin/activate
export TIMEDPAD_SETTINGS=/home/cs/timedpad/etc/live.cfg
gunicorn --bind 127.0.0.1:5001 timedpad.wsgi:app
