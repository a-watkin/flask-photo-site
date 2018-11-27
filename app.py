import json

from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json
from database_interface import Database
from photo import Photos
from album import Album


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
p = Photos()
a = Album()

tags = db.get_all_tags()

"""
$ export FLASK_APP=my_application
$ export FLASK_ENV=development
$ flask run
"""


@app.route('/albums')
def albums():
    albums_data = a.get_albums()
    json_data = albums_data
    print(json_data['large_square'])
    return render_template('albums.html', json_data=json_data), 200


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


@app.route('/api/photos/')
def photos():
    args = request.args.to_dict()

    photo_data = None
    print(args)

    if len(args) > 0:

        if 'offset' in args.keys() and 'limit' not in args.keys():
            if int(args['offset']) <= 0:
                args['offset'] = 0
            # gotta make this an int
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data

            print('args are ', args)

            return render_template('photos.html', json_data=json_data), 200
        elif 'offset' not in args.keys() and 'limit' in args.keys():
            print(9 * '\n')
            # default offset is 0
            photo_data = p.get_photos_in_range(int(args['limit']))
            json_data = photo_data
            return render_template('photos.html', json_data=json_data), 200

        else:
            """
            both offset and limit are present
            """
            if int(args['offset']) <= 0:
                args['offset'] = 0

            if int(args['limit']) <= 0:
                args['offset'] = 0

            photo_data = p.get_photos_in_range(
                int(args['limit']), int(args['offset'])
            )

            json_data = photo_data
            return render_template('photos.html', json_data=json_data), 200

    else:
        print(10 * '\n', 'why you no work')
        photo_data = p.get_photos_in_range()
        json_data = photo_data
        print(json_data)
        return render_template('photos.html', json_data=json_data), 200


# 127.0.0.1:5000/api/test?limit=20&offset=10
# @app.route('/api/photos/', methods=['GET'])
# def get_photos():
#     photo_data = p.get_photos_in_range()
#     json_data = photo_data

#     # print()
#     # json_data = dict(photo_data['photos'])

#     # print(json_data)

#     return render_template('photos.html', json_data=json_data), 200


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


if __name__ == '__main__':
    app.run()
