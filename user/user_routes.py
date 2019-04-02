from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session


from common.name_util import login_required
from user.user import User

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    status_code = 200

    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        # New instance of User.
        user = User(username, password)
        current_user = user

        if user.check_for_username() and user.check_password():
            flash('Welcome back {}'.format(username))
            session['logged_in'] = True
            return redirect(url_for('photo.home'))
        else:
            status_code = 401
            flash('Wrong username and/or password', error)
    return render_template('user/login.html')


@user_blueprint.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out')
    return redirect(url_for('photo.home'))


@user_blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Endpoint to change password.
    """
    if request.method == 'POST':

        username = request.form.get("username")
        old_pass = request.form.get("old-password")
        new_password = request.form.get("new-password")
        new_pass_confirm = request.form.get("new-password-confirm")

        user = User(username, old_pass)

        if new_password != new_pass_confirm:
            flash('Your passwords do not match.')

        if not user.check_password():
            flash('Incorrect password.')

        if user.check_password() and user.password == old_pass:
            user.insert_hashed_password(new_password)
            flash('Password changed.')

    return render_template('user/account.html'), 200
