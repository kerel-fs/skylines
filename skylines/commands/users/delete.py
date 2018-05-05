from __future__ import print_function

from flask_script import Command, Option

import sys

from skylines.database import db
from skylines.model import User, Club, IGCFile, Flight, TrackingFix


class Delete(Command):
    """ Delete an user account """

    option_list = (
        Option('user_id', type=int, help='ID of the user account'),
    )

    def run(self, user_id):
        user = db.session.query(User).get(user_id)
        
        if not user:
            print("No such user: %d" % user_id, file=sys.stderr)
            sys.exit(1)

        db.session.query(IGCFile).filter_by(owner_id=user_id).delete()
        db.session.query(Flight).filter_by(pilot_id=user_id).delete()
        db.session.query(TrackingFix).filter_by(pilot_id=user_id).delete()
        db.session.delete(user)
        db.session.flush()
        db.session.commit()
