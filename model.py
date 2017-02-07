"""Models and database functions for Roadrave project."""
# import heapq
# import time
from flask_sqlalchemy import SQLAlchemy

#  Do i need both of these?
# from SQLAlchemy import DateTime
import datetime

# import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of roadrave site."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # TODO: add email format check and account verification with email link
    email = db.Column(db.String(64), nullable=False)
    # TODO: secure pwd and add min requirements
    password = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class UserVehicle(db.Model):
    """Association table for users and vehicles on roadrave site."""

    __tablename__ = "uservehicles"

    # Q: do we need id for association table?
    user_id = db.Column(db.Integer, nullable=False)
    vehicle_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<UserVehicle user_id=%d vehicle_id=%d>" % (self.user_id, self.vehicle_id)


class Vehicle(db.Model):
    """Vehicle on roadrave site."""

    __tablename__ = "vehicles"

    veh_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    plate = db.Column(db.String(64),  nullable=False)  # eventually vehicles can change plates?
    # TODO: restrict to US plates and 7 chars in program input. Future allow EU and symbols.
    vtype = db.Column(db.String(64))  # car, truck, motorcycle, semi, plane, boat, etc.
    # veh_style = db.Column(db.String(64)) # sedan, coupe, flatbed, hazmat, sport, etc.
    make = db.Column(db.String(64))
    model = db.Column(db.String(64))
    color = db.Column(db.String(64))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Vehicle veh_id=%d plate=%s>" % (self.veh_id, self.plate)


class Post(db.Model):
    """Post on rodarave site by a user about vehicle."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # user posting
    plate = db.Column(db.String(64), db.ForeignKey('vehicles.plate'))  # postee
    # TODO: default current, but changeable for post-posting after incident
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    # TODO: program constrain to: comment, compliment, criticism
    ptype = db.Column(db.String(64), nullable=False)  # set default as comment here?
    # TODO: default get location api, or zip code
    location = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.String(140), nullable=False)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("roadrave", order_by=user_id))

    # Define relationship to vehicle
    vehicle = db.relationship("Vehicle",
                              backref=db.backref("roadrave", order_by=plate))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Roadrate post_id=%s user_id=%s plate=%s mood=%s location=%s>" % (
            self.post_id, self.user_id, self.plate, self.mood, self.location)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///roadrave'
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
