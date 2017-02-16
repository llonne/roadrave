"""Roadrave site allows users to post comments to vehicle license plates."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Post, Vehicle

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


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
    password = request.form["password"]
    username = request.form["username"]

    new_user = User(email=email, password=password, username=username)

    # TODO: check if user already exists and redirect to login or reset pwd, pwd hint, etc.

    db.session.add(new_user)
    db.session.commit()

    # do we need to get new user from db to get user_id for redirect?
    user = User.query.filter_by(email=email, password=password).first()

    session['user_id'] = user.user_id
    flash("User %s added." % email)
    # return redirect("/profile/%s" % new_user.user_id)
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
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/profile/%s" % user.user_id)


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

    user_id = session.get("user_id")

    # TODO: add security to redirct to login if no user session
    # TODO: check for userid and add to return if exists
    user = User.query.get(user_id)
    return render_template("profile.html", email=user.email, username=user.username)


@app.route("/profile/edit/<int:user_id>", methods=['GET'])
def show_user_profile_for_edit(user_id):
    """Show info about user for editing."""

    user_id = session.get("user_id")
    # TODO: add security to redirct to login if no user session
    # TODO: check for userid and add to return if exists
    user = User.query.get(user_id)
    return render_template("profile_edit.html", email=user.email, username=user.username)


@app.route("/profile/edit/<int:user_id>", methods=['POST'])
def edit_user_detail(user_id):
    """Edit info about user."""

    user_id = session.get("user_id")

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

    return render_template("post_list.html", posts=posts)


@app.route("/posts/<int:user_id>", methods=['GET'])
def user_posts_list(user_id):
    """Show list of all posts by specified user."""

    user_id = session.get("user_id")

    if user_id:
        posts = Post.query.filter_by(user_id=user_id).all()
    else:
        flash("Please log in to access posts.")
        return redirect("/login")

    return render_template("post_list.html", posts=posts)


@app.route("/posts/detail/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    """Show details about a post."""

    # user_id = session.get("user_id")

    # if user_id:
    user_post = Post.query.filter_by(
        post_id=post_id).first()
    # print user_post
    # TODO: <Roadrate post_id=2 user_id=2 vehicle_plate=plate2 event_date=2017-01-01 00:00:00 ptype=ptype2 location=location2 subject=subj2>
    # else:
    #     flash("Please log in to access posts.")
    #     return redirect("/login")

    return render_template("post.html", user_post=user_post)


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
    subject = request.form["subject"]
    location = request.form["location"]
    vehicle_plate = request.form["vehicle_plate"]
    # vtype = request.form["vtype"]
    # make = request.form["make"]
    # model = request.form["model"]
    # color = request.form["color"]

    # TODO: iterate through form variables to eliminate blanks

    # TODO: iterate through form variables to verify data formats
    # TODO: check if vehicle exists in DB, present user with choice, allow modification
    # vehicle_check = Vehicle.query.filter_by(vehicle_plate=vehicle_plate).first()

    # vehicle must exist in db before post can be added
    # vehicle = Vehicle(vehicle_plate=vehicle_plate, vtype=vtype, make=make, model=model, color=color)
    vehicle = Vehicle(vehicle_plate=vehicle_plate)
    db.session.add(vehicle)
    db.session.commit()

    post = Post(event_date=event_date, ptype=ptype, subject=subject, vehicle_plate=vehicle_plate, location=location, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    flash("Post added.")

    return redirect("/posts")


@app.route("/posts/edit/<int:post_id>", methods=['GET'])
def post_edit_form(post_id):
    """Render form to edit a post."""

    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")
        # raise Exception("No user logged in.")

    user_post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()
    user_post.event_date = user_post.event_date.strftime('%Y-%m-%d')

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
    subject = request.form["subject"]
    # vehicle_plate = request.form["vehicle_plate"]
    location = request.form["location"]

    # TODO: iterate through form variables to eliminate blanks

    post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()

    if post:
        post.event_date = event_date
        post.ptype = ptype
        post.subject = subject
        # post.vehicle_plate = vehicle_plate
        post.location = location
        flash("Post updated.")
    else:
        # post = Post(event_date=event_date, ptype=ptype, subject=subject, vehicle_plate=vehicle_plate, location=location, user_id=user_id)
        flash("Error updating post.")
        # db.session.add(post)

    db.session.commit()

    return redirect("/posts/%s" % post_id)


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
