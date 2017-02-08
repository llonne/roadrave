"""Movie roadrave."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Post  # Vehicle


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

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    username = request.form["username"]

    new_user = User(email=email, password=password, username=username)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % email)
    return redirect("/users/%s" % new_user.user_id)


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
    return redirect("/users/%s" % user.user_id)


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route("/profile/<int:user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    return render_template("user_profile.html", user=user)


# @app.route('/posts', methods=['GET'])
# def show_posts():
#     """Show all posts for user."""

#     user_id = session.get("user_id")

#     if user_id:
#         user_posts = Post.query.filter_by(user_id=user_id)
#     else:
#         flash("Please log in to access posts.")
#         return redirect("/login")

#     return render_template("all_posts.html")


@app.route("/posts/<int:post_id>", methods=['GET'])
def post_detail(post_id):
    """Show info about a post.

    If a user is logged in, let them add/edit a post.
    """

    # post = Post.query.get(post_id)

    user_id = session.get("user_id")

    if user_id:
        user_post = Post.query.filter_by(
            post_id=post_id, user_id=user_id).first()
    else:
        flash("Please log in to access posts.")
        return redirect("/login")
        # user_post = None
        # raise Exception("No user logged in.")

    # add form to add post and corresponding route
    # if (not user_post):
    #     flash("You have no posts yet. Please add one:")
    #     event_date = None
    #     ptype = None
    #     subject = None
    #     vehicle_plate = None
    #     location = None

    return render_template(
        "post.html",
        event_date=user_post.event_date,
        ptype=user_post.ptype,
        subject=user_post.subject,
        vehicle_plate=user_post.vehicle_plate,
        location=user_post.location
        )


@app.route("/posts/<int:post_id>", methods=['POST'])
def post_detail_process(post_id):
    """Add/edit a post."""

    # Get form variables
    event_date = request.form["event_date"]
    ptype = request.form["ptype"]
    subject = request.form["subject"]
    vehicle_plate = request.form["vehicle_plate"]
    location = request.form["location"]

    user_id = session.get("user_id")

    if not user_id:
        flash("Please log in to access posts.")
        return redirect("/login")
        # raise Exception("No user logged in.")

    post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()

    if post:
        post.event_date = event_date
        post.ptype = ptype
        post.subject = subject
        post.vehicle_plate = vehicle_plate
        post.location = location
        flash("Post updated.")

    else:
        post = Post(event_date=event_date, ptype=ptype, subject=subject, vehicle_plate=vehicle_plate, location=location, user_id=user_id)
        flash("Post added.")
        db.session.add(post)

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

    app.run()
