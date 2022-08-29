from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask-feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def show_register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(
            username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(f'/users/{username}')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def show_login():

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome back {user.username}')
            session['username'] = username
            return redirect(f'/users/{username}')

        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('goodbye!')
    return redirect('/')


@app.route('/users/<username>')
def show_secret(username):
    if session.get('username'):
        user = User.query.get(username)
        feedback = Feedback.query.filter(
            Feedback.username == username)
        return render_template('user.html', user=user, feedback=feedback)
    else:
        flash("You are not logged in")
        return redirect('/login')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if session.get('username'):
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted!')
        return redirect('/')

    flash('you must be logged in')
    return redirect(f'/users/{username}')


@app.route('/tweets/<int:id>', methods=['POST'])
def delete_tweet(id):
    """Delete tweet"""
    if 'user_id' not in session:
        flash('Please login first!')
        return redirect('/login')
    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('tweet deleted')
        return redirect('/tweets')
    flash("You don't have permission to do that")
    return redirect('/tweets')

# POST /users/<username>/delete
# Remove the user from the database and make sure to also delete all of their feedback.
# Clear any user information in the session and redirect to /.
#  Make sure that only the user who is logged in can successfully delete their account
