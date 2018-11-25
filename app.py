from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json
from functools import wraps


from database_interface import Database


app = Flask('app')
app = Flask(__name__.split('.')[0])

# some change with flask?
# for some reason it accepts secret_key but nothing else
# without doing this
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'admin'
# so secret key is built in from the get go
app.config['SECRET_KEY'] = 'secret'

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
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == app.config['USERNAME'] and password == app.config['PASSWORD']:
            flash('you did it, congrats')
            return render_template('main.html')
        else:
            status_code = 401
            flash('Wrong username and/or password', error)

    return render_template('login.html')


@app.route('/photos')
def photos():
    photo_data = db.get_photos_in_range()

    photos_data = {
        'title': 'blah',
        'views': 90,
        'original': 'https://farm2.staticflickr.com/1945/44692598005_c19f3c377b_o.jpg',
        # they actually do it as: Taken on August 14, 2013
        'dateTaken': '2018-10-11'
    }

    return jsonify(photos_data)


# with app.test_request_context():
#     print(url_for('login'))

@app.route("/tags")
def hello():

    tag_data = {
        'tags': tags
    }

    return jsonify(tag_data)


if __name__ == '__main__':
    app.run()
