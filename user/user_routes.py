from flask import Blueprint, request, render_template, redirect, url_for, flash, session

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
            return redirect(url_for('photo.get_photos'))

        else:
            status_code = 401
            flash('Wrong username and/or password', error)
    return render_template('photo_user/login.html')


@user_blueprint.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('photo.get_photos'))


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
            return render_template('photo_user/account.html'), 200

        if not user.check_password():
            flash('Incorrect password.')
            return render_template('photo_user/account.html'), 200

        if user.check_password() and user.password == old_pass:
            user.insert_hashed_password(new_password)
            flash('Password changed.')

    return render_template('photo_user/account.html'), 200
