from flask import Flask, redirect, request, render_template, session, flash, get_flashed_messages
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserRegisterForm, UserLoginForm, FeedbackForm
from keys import secret_key

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = secret_key
debug = DebugToolbarExtension(app)
bcrypt = Bcrypt()


connect_db(app)
db.create_all()

@app.route('/')
def send_to_register():
    "Redirects the user to the register page"
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def process_register_form():
    "Displays/Handles the UserRegister form"

    if "user_name" in session:
        flash('You cannot register while currently logged in')
        return redirect(f"/users/{session['user_name']}")

    form = UserRegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        session['user_name'] = new_user.username
        return redirect(f"/users/{session['user_name']}")

    else:
        return render_template("form.html", form=form, type="Sign Up", submission="Register")

@app.route('/login', methods=['GET', 'POST'])
def process_login_form():
    "Displays/Handles the UserLogin form"

    if "user_name" in session:
        flash('You cannot log in while already logged in')
        return redirect(f"/users/{session['user_name']}")
    
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.authenticate(username, password):
          user = User.query.filter_by(username=username).first()
          session['user_name'] = user.username
          return redirect(f"/users/{session['user_name']}")
        else:
            flash("Incorrect username or password")
            return redirect('/login')

    else:
        return render_template("form.html", form=form, type="Login", submission="Login")

@app.route('/logout', methods=["POST"])
def logout_user():
    """Logs the user out and redirects to `/`"""

    session.pop("user_name")
    return redirect('/')

@app.route('/users/<username>')
def display_user(username):
    """Displays the desired user through HTML (if authorized)"""

    if "user_name" not in session:
        flash('Please login first')
        return redirect('/login')
    if username != session['user_name']:
        flash("You do not have access to that user's page")
        return redirect(f'/users/{session["user_name"]}')
    else:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.filter_by(username=username).all()
        return render_template('user.html', user=user, feedback=feedback)
    
@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Deletes the desired user (if authorized)"""

    if "user_name" not in session:
        flash('Please login first')
        return redirect('/login')
    if username != session['user_name']:
        flash("You do not have access to that user's page")
        return redirect(f'/users/{session["user_name"]}')
    else:
        Feedback.query.filter_by(username=username).delete()
        User.query.filter_by(username=username).delete()
        db.session.commit()

        flash("User has been deleted")
        session.pop("user_name")
        return redirect('/')
    
@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def handle_adding_feedback(username):
    "Handles the creation aspect of the FeedbackForm"

    if "user_name" not in session:
        flash('Please login first')
        return redirect('/login')
    if username != session['user_name']:
            flash("You cannot add feedback as someone other than yourself")
            return redirect(f'/users/{session["user_name"]}')
    
    form = FeedbackForm()
    if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            flash("Feedback successfully added")
            return redirect(f"/users/{username}")
    else:
        return render_template('form.html', form=form, type="New Feedback", submission="Submit")



@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def handle_updating_feedback(feedback_id):
    "Handles the update aspect of the FeedbackForm"

    feedback = Feedback.query.get_or_404(feedback_id)
    if "user_name" not in session:
        flash('Please login first')
        return redirect('/login')
    if feedback.username != session['user_name']:
        flash("You are not the owner of this feedback")
        return redirect(f'/users/{session["user_name"]}')
    
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    else:
        form.content.data = feedback.content
        return render_template('form.html', form=form, type="Update Feedback", submission="Save")

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    "Deletes chosen feedback (if authorized)"

    feedback = Feedback.query.get_or_404(feedback_id)
    if "user_name" not in session:
        flash('Please login first')
        return redirect('/login')
    if feedback.username != session['user_name']:
        flash("You cannot delete someone else's feedback")
        return redirect(f'/users/{session["user_name"]}')
    
    Feedback.query.filter_by(id=feedback_id).delete()
    db.session.commit()

    flash("Feedback successfully deleted")
    return redirect(f"/users/{feedback.username}")