"""Models and database functions for Roadrave project."""
# import heapq
# import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
# from sqlalchemy import Table, Column, Integer, ForeignKey

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

    # TODO: start ids at high number?
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # TODO: add email format check and account verification with email link
    email = db.Column(db.String(64), unique=True, nullable=False)
    # TODO: secure pwd and add min requirements
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_removed = db.Column(db.DateTime)
    profile_url = db.Column(db.String(255))
    profile_picture_url = db.Column(db.String(255))

    # Define relationship to Vehicle db through UserVehicle
    vehicles = relationship("UserVehicle", back_populates="user")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class UserVehicle(db.Model):  # do we need this once users claim vehicles?
    """Association table for users and vehicles on roadrave site because vehicles can exist without user."""

    __tablename__ = "uservehicles"

    # Q: do we need id for association table?
    # A: (yes, there can be multiple usrs per vehicle, and multiple vehicles per user.)
    user_vehicle_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    vehicle_plate = db.Column(db.String(64), db.ForeignKey('vehicles.vehicle_plate'))
    date_linked = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_unlinked = db.Column(db.DateTime)

    # from Association object secion here: http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html
    vehicle = relationship("Vehicle", back_populates="users")
    user = relationship("User", back_populates="vehicles")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<UserVehicle user_vehicle_id=%d user_id=%d vehicle_plate=%d>" % (self.user_vehicle_id, self.user_id, self.vehicle_plate)


class Vehicle(db.Model):
    """Vehicle on roadrave site."""

    __tablename__ = "vehicles"

    # TODO: Beta version, allow users to add more behicle info, incl pics
    vehicle_plate = db.Column(db.String(64), primary_key=True)  # license plate
    # TODO: Beta version, add region and country plate formats including symbols.
    vtype = db.Column(db.String(64))  # car, truck, motorcycle, semi, plane, boat, etc.
    # veh_style = db.Column(db.String(64)) # sedan, coupe, flatbed, hazmat, sport, etc.
    make = db.Column(db.String(64))
    model = db.Column(db.String(64))
    color = db.Column(db.String(64))
    user_id_adder = db.Column(db.Integer, nullable=False)  # user adding car
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    # allow owners, but they will be stored in UserVehicles association table, because not required
    # user_id_owner = db.Column(db.Integer)

    # Define relationship to user db through UserVehicles
    users = relationship("UserVehicle", back_populates="vehicle")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Vehicle vehicle_plate=%d>" % (self.vehicle_plate)


class Post(db.Model):
    """Post on rodarave site by a user about vehicle."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # user posting
    vehicle_plate = db.Column(db.String(64), db.ForeignKey('vehicles.vehicle_plate'))
    event_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    ptype = db.Column(db.String(64), nullable=False)  # set default as comment here?
    # TODO: default get location api, or zip code
    location = db.Column(db.String(64), nullable=False)  # zip code for alpha version
    loc_lat = db.Column(db.Numeric(precision=9, scale=6))
    loc_log = db.Column(db.Numeric(precision=9, scale=6))
    topic = db.Column(db.String(140), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_removed = db.Column(db.DateTime)

    # Define relationship to users db
    user = db.relationship("User", backref=db.backref("roadrave", order_by=user_id))

    # Define relationship to vehicles db
    vehicle = db.relationship("Vehicle", backref=db.backref("roadrave", order_by=vehicle_plate))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Roadrate post_id=%s user_id=%s vehicle_plate=%s event_date=%s ptype=%s location=%s topic=%s>" % (
            self.post_id, self.user_id, self.vehicle_plate, self.event_date, self.ptype, self.location, self.topic)


class Comment(db.Model):
    """Comments on a post on rodarave site by a user about vehicle."""

    # TODO: crate commentPings association table to enable user pings in jquery-comments
    # TODO: create commentUpvotes assoc table to allow upvoting

    __tablename__ = "comments"
    cid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comment_id = db.Column(db.String(64), nullable=False)  # used by jquery-comments for position in thread
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    parent = db.Column(db.String(64), nullable=False)  # null means first comment in thread for jquery-comments
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    # Either content or fileURL must be present for jquery_comments
    content = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255))
    # TODO: allow attachment uploading and add file field in DB
    # pings = db.Column(db.String(255), nullable=False)
    upvotes = db.Column(db.Integer, nullable=False)
    date_removed = db.Column(db.DateTime)

    # Define relationship to posts db
    post = db.relationship("Post", backref=db.backref("roadrave", order_by=post_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Roadrate cid=%d comment_id=%s user_id=%d post_id=%d parent=%s date_created=%s date_modified=%s content=%s upvotes=%d>" % (
            self.cid, self.comment_id, self.user_id, self.post_id, self.parent, self.date_created, self.date_modified, self.content, self.upvotes)


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
