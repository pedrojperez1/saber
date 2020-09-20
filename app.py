
import os
from flask import Flask, request, render_template, redirect, flash, session, g
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Official, Question, City
from forms import LoginForm, UserForm, QuestionForm
from datetime import datetime

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///saber_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'oh-so-secret'

connect_db(app)

#############################################
# Log in and sign up

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def root():
    """root route"""
    if g.user:
        officials = g.user.city.officials
        questions = []
        for o in officials:
            questions.extend(o.questions)
        questions.sort(key=lambda x: x.timestamp, reverse=True)
        user_likes = [l.id for l in g.user.likes]
        return render_template('home.html', questions=questions, user_likes=user_likes)
    
    else:
        return redirect('/signup')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handles user signup"""

    form = UserForm()

    if form.validate_on_submit():
        print(f'form.city.data: {form.city.data}')
        print(f'form.state.data.id: {form.state.data.id}')
        city = City.get_city_from_query(form.city.data, form.state.data.id)
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data,
                city_id=city.id
            )
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already taken", "danger")
            return render_template('users/signup.html', form=form)
        except:
            flash("Unexpected error. Please try again.", "danger")
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('You are now logged out.', 'success')
    return redirect('/login')

#############################################
@app.route('/profile', methods=['GET'])
def show_profile():
    """Show profile for the current user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    return render_template('users/profile.html', user=g.user)

@app.route('/edit_profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserForm(
        username=g.user.username,
        email=g.user.email,
        password=g.user.password,
        image_url=g.user.image_url,
        city=g.user.city.name,
        state=g.user.city.state
    )
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if not user:
            flash('Password was incorrect. Please try again.', 'danger')
            return redirect('/profile')
        else:
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.city_id = City.get_city_from_query(form.city.data, form.state.data.id).id
            db.session.add(user)
            db.session.commit()
            flash('Successfully updated your profile!', 'success')
            return redirect('/profile')
    else:
        return render_template('users/edit_profile.html', form=form)


@app.route('/officials', methods=['GET'])
def show_officials():
    """Show officials for the current user"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    return render_template('users/officials.html', user=g.user)
    
@app.route('/new', methods=['GET', 'POST'])
def new_question():
    """Get user's officials and handle creating new question"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = QuestionForm()
    if form.validate_on_submit():
        new_question = Question(
            user_id=session[CURR_USER_KEY],
            official_id=form.official.data,
            text=form.text.data
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Your question has been asked!", "success")
        return redirect('/')
    
    form.official.choices = [(o.id, f'{o.name} ({o.office})') for o in g.user.city.officials]
    return render_template('questions/new_question.html', form=form)

@app.route('/add_like/<int:question_id>', methods=['POST'])
def add_like(question_id):
    """Creates a like for the current user given a question_id"""
    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')
    liked_question = Question.query.get_or_404(question_id)
    g.user.likes.append(liked_question)
    db.session.commit()

    return redirect('/')

@app.route('/remove_like/<int:question_id>', methods=['POST'])
def remove_like(question_id):
    """Removes a like for the current user given a question_id"""
    if not g.user:
        flash('Access unauthorized.', 'danger')
        return redirect('/')
    liked_question = Question.query.get_or_404(question_id)
    g.user.likes.remove(liked_question)
    db.session.commit()

    return redirect('/')

####### Template filters
@app.template_filter('calc_time_ago')
def calc_time_ago_filter(timestamp):
    tz_info = timestamp.tzinfo
    diff = datetime.now(tz_info) - timestamp
    diff_mins = round(diff.seconds / 60)
    if diff_mins > 1440: # if difference is more than a day return days
        return f'{round(diff_mins / 60*24)} days ago'
    elif diff_mins > 59: # if difference is more than an hour return hours
        return f'{round(diff_mins / 60)} hours ago'
    else:
        return f'{diff_mins} mins ago'
