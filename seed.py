"""Utility file to seed roadrant database from text files in seed_data/"""

import datetime
from sqlalchemy import func

from model import User, Vehicle, Post, connect_to_db, db
from server import app


def load_users():
    """Load users from users.txt into database."""

    print "Users"

    for i, row in enumerate(open("seed_data/users.txt")):
        row = row.rstrip()
        email, password, username = row.split("|")

        user = User(email=email,
                    password=password,
                    username=username
                    )

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

        # provide some sense of progress
        if i % 100 == 0:
            print i

    # Once we're done, we should commit our work
    db.session.commit()


def load_vehicles():
    """Load vehicles from vehicles.txt into database."""

    print "Vehicles"

    for i, row in enumerate(open("seed_data/vehicles.txt")):
        row = row.rstrip()

        plate, vtype, make, model, color, user_id_owner, user_id_adder = row.split("|")

        user_id_owner = int(user_id_owner)
        user_id_adder= int(user_id_adder)

        vehicle = Vehicle(plate=plate,
                          vtype=vtype,
                          make=make,
                          model=model,
                          color=color,
                          user_id_owner=user_id_owner,
                          user_id_adder=user_id_adder)

        # We need to add to the session or it won't ever be stored
        db.session.add(vehicle)

        # provide some sense of progress
        if i % 100 == 0:
            print i

    # Once we're done, we should commit our work
    db.session.commit()


def load_posts():
    """Load posts from posts.txt into database."""

    print "Posts"

    for i, row in enumerate(open("seed_data/posts.txt")):
        row = row.rstrip()

        user_id, plate, event_date, ptype, location, subject, date_post_added, date_post_removed = row.split("|")

        user_id = int(user_id)
        event_date = datetime.datetime.strptime(event_date, "%d-%b-%Y")
        # date_post_added = datetime.datetime.strptime(date_post_added, "%d-%b-%Y")
        # date_post_removed = datetime.datetime.strptime(date_post_removed, "%d-%b-%Y")

        post = Post(user_id=user_id,
                    plate=plate,
                    event_date=event_date,
                    ptype=ptype,
                    location=location,
                    subject=subject
                    )

        # We need to add to the session or it won't ever be stored
        db.session.add(post)

        # provide some sense of progress
        if i % 1000 == 0:
            print i

            # An optimization: if we commit after every add, the database
            # will do a lot of work committing each record. However, if we
            # wait until the end, on computers with smaller amounts of
            # memory, it might thrash around. By committing every 1,000th
            # add, we'll strike a good balance.

            db.session.commit()

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_users()
    load_vehicles()
    load_posts()
    set_val_user_id()

    db.session.commit()
