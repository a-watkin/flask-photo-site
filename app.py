from flask import Flask, render_template, request, session, flash, redirect, url_for, g

from functools import wraps


from database_interface import Database


app = Flask(__name__)
app.config['DEBUG'] = True


USERNAME = 'admin'
PASSWORD = 'admin'

SECRET_KEY = 'secret'


db = Database('eigi-data.db')


tags = db.get_all_tags()

"""
$ export FLASK_APP=my_application
$ export FLASK_ENV=development
$ flask run
"""


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    status_code = 200
    if request.method == 'POST':
        try:
            if request.form['username'] != app.config['USERNAME'] or \
                    request.form['password'] != app.config['PASSWORD']:
                error = 'Invalid Credentials. Please try again.'
                status_code = 401
            else:
                session['logged_in'] = True
                return redirect(url_for('main'))

        except Exception as e:
            print('error ', e)

    # if method is get then this is returned
    return render_template('login.html', error=error), status_code


# with app.test_request_context():
#     print(url_for('login'))

# @app.route("/")
# def hello():

#     tag_data = {
#         'tags': tags
#     }

#     return jsonify(tag_data)


if __name__ == '__main__':
    app.run()
