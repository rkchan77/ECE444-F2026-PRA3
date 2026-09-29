import re
from datetime import datetime, timezone
from flask import (Flask, render_template, session, redirect, url_for, flash,
                   request)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e0e961f1-56e3-4aa2-bf3e-6951b5c0434d'

bootstrap = Bootstrap(app)
moment = Moment(app)


def is_uoft_email(email):
    return email is not None and 'utoronto' in email.lower()


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField('What is your UofT Email address?',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        old_email = session.get('email')
        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')
        session['name'] = form.name.data
        session['email'] = form.email.data
        if is_uoft_email(form.email.data):
            return redirect(url_for('chatbot'))
        return redirect(url_for('index'))
    email = session.get('email')
    is_uoft = is_uoft_email(email)
    return render_template('index.html', form=form, name=session.get('name'),
                           email=email, is_uoft=is_uoft,
                           current_time=datetime.now(timezone.utc))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/chatbot')
def chatbot():
    # Only users who submitted a name and a valid UofT email may chat
    if not is_uoft_email(session.get('email')):
        return redirect(url_for('index'))
    return render_template('chatbot.html', name=session.get('name'))


@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message'].strip()
    lower = message.lower()
    # The name the user tells the bot is kept in the session, so it is
    # still available on later requests from the same browser
    name_match = re.search(r'my name is\s+([^.!?]+)', message, re.IGNORECASE)
    if name_match:
        chat_name = name_match.group(1).strip()
        session['chat_name'] = chat_name
        reply = f'Nice to meet you, {chat_name}!'
    elif "what is my name" in lower or "what's my name" in lower:
        chat_name = session.get('chat_name')
        if chat_name:
            reply = f'Your name is {chat_name}.'
        else:
            reply = "I don't know your name yet. Tell me by saying \"My name is ...\""
    elif 'hello' in lower:
        chat_name = session.get('chat_name')
        reply = f'Hello, {chat_name}!' if chat_name else 'Hello!'
    else:
        reply = "I don't understand."
    return {'reply': reply}


@app.route('/logout')
def logout():
    # Removes everything stored for this browser: form data and chat memory
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))
