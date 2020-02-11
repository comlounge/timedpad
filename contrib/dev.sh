#!/bin/sh

export TIMEDPAD_SETTINGS=/home/cs/prj/timedpad/etc/dev.cfg
export FLASK_APP=timedpad.index:app
flask run --reload
