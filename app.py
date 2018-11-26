import json

from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json
from functools import wraps


from database_interface import Database
from photos import Photos


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


# @app.route('/get/photos/<int:limit>')
# def photos(limit):
#     print(limit)
#     photo_data = db.get_photos_in_range(limit=limit)
#     return jsonify(photo_data)


# 127.0.0.1:5000/api/test?limit=20&offset=10
@app.route('/api/photos/', methods=['GET'])
def get_photos():
    p = Photos()
    photo_data = p.get_photos_in_range()
    json_data = photo_data

    # print()
    # json_data = dict(photo_data['photos'])

    # print(json_data)

    return render_template('photos.html', json_data=json_data), 200


# 43613382810
@app.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    photo_data = db.get_photo(photo_id)
    json_data = photo_data
    print(json_data)
    return render_template('photo.html', json_data=json_data), 200


@app.route('/api/photos/next/<int:photo_id>', methods=['GET'])
def get_next_photo(photo_id):
    print('\n\n\n\n', photo_id, '\n\n\n\n')


# with app.test_request_context():
#     print(url_for('login'))

# @app.route("/tags")
# def hello():

#     tag_data = {
#         'tags': tags
#     }
#     return jsonify(tag_data)
if __name__ == '__main__':
    app.run()
