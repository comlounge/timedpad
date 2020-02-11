# Timepad installation

This flask app will provide 2 functionalities:

- a timed pad functionality where a pad is automatically deleted after a certain time of inactivity (here 31 days)
- a admin delete function for manually deleting any pad

## Timed pad functionality

The timepad functionality works by replacing the default homepage of etherpad lite with a custom one served by this flask app.
Here a user has the option to mark a new pad as timed etherpad which is deleted automatically after 31 days.


## deleter functionality

In order for an admin to delete etherpads manually (unrestricted by the timed pad functionality) an endpoint `/deleter`
is provided by the flask app protected by a basic auth. 


### Requirements

- MongoDB 4.x
- Python 3.x
- a running etherpad installation
- nginx


### Install a python 3 virtual env

```
mkdir timedenv
cd timeenv
python3 -m venv .
source bin/activate
```

`timedenv` is our main venv directory.

### clone the repository and install dependencies

```
git clone <github repo of timedpad>
cd timedpad
pip install -r requirements.txt
python3 setup.py develop
```


### configure timedpad

For the configuration you create an `etc` directory in the main venv directory (`timedev`)

```
cd ..
mkdir etc
cp timepad/contrib/setup.cfg etc/live.cfg
```

Change `live.cfg` according to your setup.


### run server

copy over `run.sh` from `timedpad/contrib` and adjust it to your paths.

Call it to run the server

You can also create a supervisord config: 

```
[program:timedpad]
command = /path/to/run.sh
process_name = timedpad
directory = /path/to/virtualenv
priority = 10
redirect_stderr = true
user = timedpad
environment = FLASK_APP="/path/to/src/timedpad/timedpad/index.py",TIMEDPAD_SETTINGS="/path/to/etc/live.cfg"
```

Make sure you have the user created.


### adjust the contents of the homepage

You should then adjust the template in `timedpad/templates/index.py`

Then start the flask app which should run on port `5000`. 


## Setup web frontend

The web front end replaces the normal etherpad start screen with the one by timedpad. We assume that the flask app is setup as described above.
We assume that etherpad is running on port 10001.

It is injected by the nginx server like this:


```
    add_header X-Proxy-Cache $upstream_cache_status;

    # this will show the homepage served by the flask app timedpad 
    location ~ (^/$|^/hpstatic|^/deleter) {
            proxy_pass             http://127.0.0.1:5000; # the flask app
    }

    # this will show the normal etherpad pages (except / which is overriden above)
    location / {
            proxy_pass             http://127.0.0.1:10001/;
            proxy_set_header       Host ssl.yourpart.eu;
            proxy_pass_header Server;

            # be carefull, this line doesn't override any proxy_buffering on set in a conf.d/file.conf
            proxy_buffering off;
            proxy_set_header X-Real-IP $remote_addr;  # http://wiki.nginx.org/HttpProxyModule
            proxy_set_header X-Forwarded-For $remote_addr; # EP logs to show the actual remote IP
            proxy_set_header X-Forwarded-Proto $scheme; # for EP to set secure cookie flag when https is used
            proxy_set_header Host $host;  # pass the host header
            proxy_http_version 1.1;  # recommended with keepalive connections

            # WebSocket proxying - from http://nginx.org/en/docs/http/websocket.html
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
    }

```

Now the start screen should show the start screen provided by the flask app. It should automatically redirect to `/p/<padname>` on the same domain. If the checkbox for limiting access is activated the pad should be store in the mongodb collection, too.


# running the expiration script via cron

You can use the `contrib/cron.sh` script as a starting point to setup your environment.
Running it will configure the flask command and will run it. 

You can also run it manually with `flask expire`. 

You can use the `cron.sh` script in your crontab.
