#encoding=utf8 
from flask import render_template
from flask import Flask, request
from flask_pymongo import PyMongo
from werkzeug import redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


import logging
from logging.handlers import RotatingFileHandler

import datetime
import click

from .expirator import Expirator
from .ep import EtherpadLiteClient, EtherpadException

app = Flask(__name__, static_url_path='/hpstatic')
app.config.update(
    TESTING=True,
    EP_API_KEY="test",
    EP_URL="https://yourpart.eu",
    EXPIRES_IN_DAYS=31,
    DELETER_USER="deleter",
    DELETER_PW=")(/D)Jbhbdcsb9(Sjhbvjhdgcshf&hvcgdvhsdg) please change"
)
app.config.from_envvar('TIMEDPAD_SETTINGS')

auth = HTTPBasicAuth()
users = {
    app.config['DELETER_USER'] : generate_password_hash(app.config['DELETER_PW']),
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False



epurl = app.config['EP_URL']
apiurl = app.config['EP_URL']+"/api"

mongo = PyMongo(app)
pads = EtherpadLiteClient(base_params = {'apikey': app.config['EP_API_KEY']}, base_url = apiurl)

@app.route('/')
def index(name=None):
    pad = request.args.get("p", "")
    pad = pad.strip()
    expires = request.args.get("e", "off")
    if len(pad):
        app.logger.info("trying to create/goto pad %s" %pad)
        try:
            content = pads.getText(padID=pad)
        except EtherpadException as e:
            app.logger.info("pad %s does not exist" %pad)

            # does user want to expire it?
            if expires=="on":
                app.logger.info("pad %s is marked for deletion" %pad)
                mongo.db.pads.save({'_id': pad, 'ts' : datetime.datetime.now(), 'status' : 'live'})

                # create it by going there
                return redirect(epurl+"/p/%s" %pad)
            else:
                # new pad -> redirect
                return redirect(epurl+"/p/%s" %pad)
        else:
            if expires=="on":
                # this is not allowed
                return render_template('index.html', 
                    pad = pad, 
                    error_msg=u"""
                    Dieses Pad existiert bereits und kann daher nicht zur automatischen Löschung markiert werden.<br>
                    This pad already exists and therefore can not be marked for automatic deletion.
                    """,
                    name=name)
            app.logger.info("going to existing pad %s" %pad)
            return redirect(epurl+"/p/%s" %pad)
    else:
        app.logger.info("no pad name was given")

    return render_template('index.html', name=name)

@app.route('/deleter')
@auth.login_required
def deleter(name=None):
    """delete a pad but only if you are allowed to do so"""
    epurl = app.config['EP_URL']
    apiurl = app.config['EP_URL']+"/api"

    pid = request.args.get("p", "")
    pid = pid.strip()

    if len(pid):
        try:
            pads.deletePad(padID=pid)
            print("pad %s deleted" %pid)
        except EtherpadException as e:
            return "Dieses Pad existiert nicht"
        return "Pad %s gelöscht" %pid

    return render_template('deleter.html')



@app.cli.command("expire")
@click.option("-d", "--dry_run", is_flag=True)
def expire(dry_run):
    """run the expiration"""
    exp = Expirator(app)
    exp.expire()

if __name__=="__main__":
    handler = RotatingFileHandler(app.config['LOGFILE'], maxBytes=30000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    app.run(host="0.0.0.0")

