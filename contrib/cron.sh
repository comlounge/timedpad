#!/bin/sh

cs /home/cs/prj/timedpad/
. /home/cs/prj/timedpad/bin/activate
export FLASK_APP=timedpad.index
export TIMEDPAD_SETTINGS=/home/cs/prj/timedpad/etc/live.cfg

bin/flask expire
