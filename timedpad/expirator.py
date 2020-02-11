import datetime

from flask_pymongo import PyMongo
from .ep import EtherpadLiteClient

class Expirator:
    """expires old pads which are marked in the mongodb"""

    def __init__(self, app, dry_run=False):
        """initialize the expirator"""
        self.app = app
        self.dry_run = dry_run

    def expire(self):
        """expire the actual pads"""

        now = datetime.datetime.now()
        app = self.app
        epurl = app.config['EP_URL']
        apiurl = app.config['EP_URL']+"/api"

        print("deleting pads not touched in %s days" %app.config['EXPIRES_IN_DAYS'])

        with app.app_context():
            mongo = PyMongo(app)

            pads = EtherpadLiteClient(base_params = {'apikey': app.config['EP_API_KEY']}, base_url = apiurl)

            for pad in mongo.db.pads.find({'status' : 'live'}):
                pid = pad['_id']
                try:
                    try:
                        last = pads.getLastEdited(padID=pid)
                    except Exception as e:
                        print("** %s not processing" %pid, e)
                        continue

                    # we get it as milliseconds
                    last_edit = last['lastEdited']/1000

                    # convert it to datetime
                    last_edit = datetime.datetime.utcfromtimestamp(int(last_edit))
                    
                    # add configured days
                    expires = last_edit + datetime.timedelta(days=app.config['EXPIRES_IN_DAYS'])

                    expired = expires < now
                    if expired:
                        print("EXPIRED: %s/p/%s (last edit %s)" %(epurl, pid, last_edit))
                        if not self.dry_run:
                            pads.deletePad(padID=pid)
                            mongo.db.pads.update({'_id' : pid}, {'ts': pad['ts'], 'status' : 'deleted', 'deletedon' : now})
                            print("DELETED")
                    else:
                        print("LIVE: %s/p/%s (last edit %s)" %(epurl, pid, last_edit))

                except ValueError as e: # does not exist
                    print("an error occurred checking or deleting pads:", e)
                    pass
