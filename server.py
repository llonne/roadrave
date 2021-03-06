"""Roadrave site allows users to post comments to vehicle license plates."""

from passlib.hash import argon2
from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Post, Vehicle, Comment
import json
# from sqlalchemy.sql import and_
# from sqlalchemy import Date, cast
# from datetime import date, datetime

# TODO: ? install pycipher 0.5.2


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

# Create instance of argon2 password hasher
# ph = PasswordHasher()


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    # TODO: check if user logged in, redirect to profile. flash message

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    username = request.form["username"]
    passwd = request.form["password"]

    if not email:
        flash("Missing email. Please try again.")
        return redirect("/register")

    if not passwd:
        flash("Missing password. Please try again.")
        return redirect("/register")

    if not username:
        flash("Missing username. Please try again.")
        return redirect("/register")

    # hashed = ph.hash(passwd)
    hashed = argon2.hash(passwd)
    del passwd

    # TODO: check fields and db without reloading page. Ajax. Keep filled fields.
    # TODO: if user exists, offer forgot password, pwd hint, etc.
    existing_uname = User.query.filter_by(username=username).first()
    if existing_uname:
        flash("Username already exists. Please try again.")
        return redirect("/register")

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        flash("Email already exists. Please try again.")
        return redirect("/register")

    # Add the new user to the database
    new_user = User(email=email, password=hashed, username=username)
    db.session.add(new_user)
    db.session.commit()

    # get the newly added user's generated user_id from the database to set session cookie
    user = User.query.filter_by(email=email, password=hashed).first()

    # set session cookie for newly added user
    session['user_id'] = user.user_id
    flash("User %s added." % email)

    return redirect("/profile/%s" % user.user_id)


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    passwd = request.form["password"]

    if not email:
        flash("Missing email. Please try again.")
        return redirect("/login")

    if not passwd:
        flash("Missing password. Please try again.")
        return redirect("/login")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No user found with that email. Please try again.")
        return redirect("/login")
    else:
        # hashed = argon2.hash(passwd)
        # del passwd
        if (argon2.verify(passwd, user.password)):
            session["user_id"] = user.user_id
            # TODO: add username or email to flash message.
            flash("Logged in successfully.")
            return redirect("/profile/%s" % user.user_id)
        else:
            flash("Password does not match.")
            return redirect("/login")


@app.route('/logout')
def logout():
    """Log out."""

    if (session["user_id"]):
        del session["user_id"]
    flash("Logged Out.")
    return redirect("/login")


@app.route("/profile/<int:user_id>", methods=['GET'])
def show_user_detail(user_id):
    """Show info about user."""

    # user_id = session.get("user_id")

    # TODO: add security to redirct to login if no user session
    # TODO: check for userid and add to return if exists
    user = User.query.get(user_id)
    return render_template("profile.html", email=user.email, username=user.username)


@app.route("/profile/edit/<int:user_id>", methods=['GET'])
def show_user_profile_for_edit(user_id):
    """Show info about user for editing."""

    # user_id = session.get("user_id")
    # TODO: add security to redirct to login if no user session
    # TODO: check for userid and add to return if exists
    user = User.query.get(user_id)

    return render_template("profile_edit.html", email=user.email, username=user.username)


@app.route("/profile/edit/<int:user_id>", methods=['POST'])
def edit_user_detail(user_id):
    """Edit info about user."""

    # user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")
        # raise Exception("No user logged in.")

    # Get form variables
    email = request.form["email"]
    # old_pwd = request.form["old_pwd"]
    username = request.form["username"]
    new_pwd = request.form["new_pwd"]

    user = User.query.get(user_id)
    # TODO: iterate through form variables to eliminate blanks
    # TODO: make sure old_pwd matches one in DB
    # TODO: secure pwds
    # TODO: only change variables that have changed
    # if (user.password == old_pwd):

    if user:
        user.email = email
        if (new_pwd):
            user.password = new_pwd
        user.username = username
        flash("Profile updated.")
    else:
        flash("Error updating profile.")
        return redirect("/profile/edit/%s" % user_id)

    # else:
    #     flash("Current password doesnt match. Try again.")
    #     return redirect("/profile/edit/%s" % user_id)

    db.session.commit()

    return redirect("/profile/%s" % user_id)


@app.route("/posts", methods=['GET'])
def posts_list():
    """Show list of all posts for all users."""

    posts = Post.query.order_by(Post.event_date.desc()).all()
    for post in posts:
        post.event_date = post.event_date.strftime('%m/%d/%Y %I:%M %P')
        user = User.query.filter_by(user_id=post.user_id).first()
        post.username = user.username
    # TODO: add username to posts db so we do not double query?

    return render_template("post_list.html", posts=posts)


@app.route("/posts/<int:user_id>", methods=['GET'])
def user_posts_list(user_id):
    """Show list of all posts by specified user."""

    # user_id = session.get("user_id")

    # if user_id:
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.event_date.desc()).all()
    for post in posts:
        post.event_date = post.event_date.strftime('%m/%d/%Y %I:%M %P')
        user = User.query.filter_by(user_id=post.user_id).first()
        post.username = user.username
    # else:
    #     flash("Please log in to access posts.")
    #     return redirect("/login")

    return render_template("post_list.html", posts=posts)


@app.route("/posts/detail/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    """Show details about a post."""

    # user_id = session.get("user_id")

    # if user_id:
    user_post = Post.query.filter_by(post_id=post_id).first()
    user_post.event_date = user_post.event_date.strftime('%m/%d/%Y %I:%M %P')
    user = User.query.filter_by(user_id=user_post.user_id).first()
    user_post.username = user.username
    # print user_post
    # TODO: <Roadrate post_id=2 user_id=2 vehicle_plate=plate2 event_date=2017-01-01 00:00:00 ptype=ptype2 location=location2 topic=subj2>
    # else:
    #     flash("Please log in to access posts.")
    #     return redirect("/login")

    return render_template("post.html", user_post=user_post)


@app.route("/post_comments.json", methods=['GET'])
def post_detail_comments_json():
    """Show details about a post including comments."""

# TODO: enable upvoting in jquery_comments and modify db model to handle userHasUpvoted data
# set these vars for jquery_comments...

    user_id = session.get("user_id")
    post_id = int(request.args.get("post_id"))

    if user_id:
        # get post data
        user_post = Post.query.filter_by(post_id=post_id).first()
        user_post.event_date = user_post.event_date.strftime('%m/%d/%Y %I:%M %P')
        user = User.query.filter_by(user_id=user_post.user_id).first()
        user_post.username = user.username
        # get comments
        post_comments = Comment.query.filter_by(post_id=post_id).all()
        for comment in post_comments:
            # comment.date_created = comment.date_created.strftime('%Y-%m-%d')
            comment.date_created = comment.date_created.strftime('%Y, %m, %d %H:%M:%S')
            # comment.date_created = comment.date_created.strftime('%Y-%m-%dT%H:%M:%f+00:00')
            # comment.date_modified = comment.date_modified.strftime('%Y-%m-%d')
            comment.date_modified = comment.date_modified.strftime('%Y, %m, %d %H:%M:%S')
            # comment.date_modified = comment.date_modified.strftime('%Y-%m-%dT%H:%M:%f+00:00')
            if (user_id == comment.user_id):
                comment.created_by_current_user = True
            else:
                comment.created_by_current_user = False
            # remove from beginnso can be converted to json
            del comment._sa_instance_state
    else:
        flash("Please log in to access posts.")
        return redirect("/login")

    # convert to dictionary format
    post_comments = [comment.__dict__ for comment in post_comments]

    # convert to json format
    post_comments = json.dumps(post_comments)

    return jsonify({'comments': post_comments})


@app.route("/posts/detail/comments/<int:post_id>", methods=['GET'])
def post_detail_comments(post_id):
    """Show details about a post including comments."""

# TODO: enable upvoting in jquery_comments and modify db model to handle userHasUpvoted data
# set these vars for jquery_comments...

    user_id = session.get("user_id")

    if user_id:
        # get post data
        user_post = Post.query.filter_by(post_id=post_id).first()
        user_post.event_date = user_post.event_date.strftime('%m/%d/%Y %I:%M %P')
        user = User.query.filter_by(user_id=user_post.user_id).first()
        user_post.username = user.username
        # get comments
        post_comments = Comment.query.filter_by(post_id=post_id).all()
        for comment in post_comments:
            # comment.date_created = comment.date_created.strftime('%Y-%m-%d')
            comment.date_created = comment.date_created.strftime('%Y-%m-%dT%H:%M:%f+00:00')
            # comment.date_modified = comment.date_modified.strftime('%Y-%m-%d')
            comment.date_modified = comment.date_modified.strftime('%Y-%m-%dT%H:%M:%f+00:00')
            if (user_id == comment.user_id):
                comment.created_by_current_user = True
            else:
                comment.created_by_current_user = False
            # remove from beginnso can be converted to json
            del comment._sa_instance_state
    else:
        flash("Please log in to access posts.")
        return redirect("/login")

    # convert to dictionary format
    post_comments = [comment.__dict__ for comment in post_comments]
    # print post_comments
    # convert to json format
    post_comments = json.dumps(post_comments)
    # print post_comments
    return render_template("post_comments.html", user_post=user_post, post_comments=post_comments)


@app.route("/posts/detail/comments/<int:post_id>", methods=['POST'])
def post_detail_comments_form(post_id):
    """Show details about a post and save comments."""

    # Get variables
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")

    comment_id = request.form["comment_id"]
    parent = request.form["parent"]
    date_created = request.form["date_created"]
    # TODO: check if date_modified should be in another function or if loop
    # date_modified = request.form["date_modified"]
    content = request.form["content"]
    upvotes = request.form["upvote_count"]

    # TODO: iterate through form variables to eliminate blanks
    # TODO: iterate through form variables to verify data formats

    # comment = Comment(comment_id=comment_id, user_id=user_id, post_id=post_id, parent=parent,
    #                   date_created=date_created, date_modified=date_modified, content=content,
    #                   upvotes=upvote_count)
    comment = Comment(comment_id=comment_id, user_id=user_id, post_id=post_id, parent=parent,
                      date_created=date_created, content=content, upvotes=upvotes)
    db.session.add(comment)
    db.session.commit()
    flash("Comment added.")

    # return redirect("/posts/detail/%s" % post.post_id)

    # return render_template("post_comments.html", user_post=user_post, post_comments=post_comments)
    return jsonify({'status': 'success'})


@app.route("/posts/add", methods=['GET'])
def post_add_form():
    """Form to add a post."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to add posts.")
        return redirect("/login")

    return render_template("post_add.html")


@app.route("/posts/add", methods=['POST'])
def post_add():
    """Add a post."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")
        # raise Exception("No user logged in.")

    # Get form variables
    event_date = request.form["event_date"]
    ptype = request.form["ptype"]
    topic = request.form["topic"]
    location = request.form["location"]
    vehicle_plate = request.form["vehicle_plate"]
    vehicle_plate = vehicle_plate.upper()
    # vtype = request.form["vtype"]
    # make = request.form["make"]
    # model = request.form["model"]
    # color = request.form["color"]

    # TODO: iterate through form variables to eliminate blanks

    # TODO: iterate through form variables to verify data formats
    # TODO: check if vehicle exists in DB, present user with choice, allow modification
    vehicle_check = Vehicle.query.filter_by(vehicle_plate=vehicle_plate).first()

    # vehicle must exist in db before post can be added
    # vehicle = Vehicle(vehicle_plate=vehicle_plate, vtype=vtype, make=make, model=model, color=color)
    if not (vehicle_check):
        vehicle = Vehicle(vehicle_plate=vehicle_plate, user_id_adder=user_id)
        db.session.add(vehicle)
        db.session.commit()

    post = Post(event_date=event_date, ptype=ptype, topic=topic, vehicle_plate=vehicle_plate, location=location, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    flash("Post added.")

    return redirect("/posts/detail/%s" % post.post_id)


@app.route("/posts/edit/<int:post_id>", methods=['GET'])
def post_edit_form(post_id):
    """Render form to edit a post."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")
        # raise Exception("No user logged in.")

    user_post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()
    # user_post.event_date = user_post.event_date.strftime('%Y-%m-%d %I:%M %P')
    user_post.event_date = user_post.event_date.strftime('%Y-%m-%dT%H:%M')

    # vehicle = Vehicle.query.filter_by(vehicle_plate=user_post.vehicle_plate).first()

    # return render_template("post_edit.html", user_post=user_post, vehicle=vehicle)
    return render_template("post_edit.html", user_post=user_post)


@app.route("/posts/edit/<int:post_id>", methods=['POST'])
def post_edit(post_id):
    """Submit edits to a post."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")
        # raise Exception("No user logged in.")

    # Get form variables
    event_date = request.form["event_date"]
    ptype = request.form["ptype"]
    topic = request.form["topic"]
    # vehicle_plate = request.form["vehicle_plate"]
    location = request.form["location"]

    # TODO: iterate through form variables to eliminate blanks
    # TODO: add ability to delete posts
    # TODO: fix ability to edit vehicle_plate
    post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()

    if post:
        post.event_date = event_date
        post.ptype = ptype
        post.topic = topic
        # post.vehicle_plate = vehicle_plate
        post.location = location
        flash("Post updated.")
    else:
        # post = Post(event_date=event_date, ptype=ptype, topic=topic, vehicle_plate=vehicle_plate, location=location, user_id=user_id)
        flash("Error updating post.")
        # db.session.add(post)

    db.session.commit()

    return redirect("/posts/detail/%s" % post_id)


@app.route("/posts/vehicle/<vehicle_plate>", methods=['GET'])
def posts_by_vehicle(vehicle_plate):
    """Show posts for a vehicle."""

    posts = Post.query.filter_by(vehicle_plate=vehicle_plate).order_by(Post.event_date.desc()).all()
    for post in posts:
        post.event_date = post.event_date.strftime('%m/%d/%Y %I:%M %P')
        user = User.query.filter_by(user_id=post.user_id).first()
        post.username = user.username

    return render_template("post_list.html", posts=posts)


@app.route("/posts/search", methods=['GET'])
def post_search_form():
    """Form to search for posts."""

    return render_template("post_search.html")


@app.route("/posts/search", methods=['POST'])
def post_search():
    """Search for posts."""

    terms = []
    # terms = ""

    # Get form variables and store for query
    # event_date = request.form["event_date"]
    ptype = request.form["ptype"]
    topic = request.form["topic"]
    location = request.form["location"]
    vehicle_plate = request.form["vehicle_plate"]
    # vtype = request.form["vtype"]
    # make = request.form["make"]
    # model = request.form["model"]
    # color = request.form["color"]

    # if items added to search form, store in query format
    # TODO: fix issues searching db for datetime
    # if (event_date):
    #     event_date = str(event_date)
    #     event_date = event_date[:10]
    #     print event_date
    #     event_date = datetime.strptime(event_date, "%Y-%m-%d")
    #     print event_date
    #     # event_date = datetime.strptime(event_date, "%Y-%m-%dT%H:%M")
    #     event_date = str(event_date)
    #     event_date = event_date[:10]
    #     print event_date
    #     event_date = "(Post.event_date.like('%" + event_date + "%'))"
    #     # event_date = "(Post.event_date.like('%(cast(" + event_date + ", Date)%'))"
    #     # event_date = "(Post.event_date.like('%(cast(" + event_date + ", Date))%'))"
    #     print event_date
    #     terms.append(event_date)

    if (ptype):
        ptype = "(Post.ptype.like('%" + ptype + "%'))"
        terms.append(ptype)

    if (topic):
        topic = "(Post.topic.like('%" + topic + "%'))"
        terms.append(topic)

    if (location):
        location = "(Post.location.like('%" + location + "%'))"
        terms.append(location)

    if (vehicle_plate):
        vehicle_plate = vehicle_plate.upper()
        vehicle_plate = "(Post.vehicle_plate.like('%" + vehicle_plate + "%'))"
        terms.append(vehicle_plate)

    # terms is the list of filters
    term_filter = eval('and_(%s)' % ','.join(terms))
    posts = Post.query.filter(term_filter)

    for post in posts:
        post.event_date = post.event_date.strftime('%m/%d/%Y %I:%M %P')
        user = User.query.filter_by(user_id=post.user_id).first()
        post.username = user.username

    # return redirect("/posts/search/result")
    return render_template("post_search_result.html", posts=posts)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    # app.run()
    app.run(port=5000, host='0.0.0.0')
