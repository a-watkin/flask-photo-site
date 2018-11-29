import json

from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json
from database_interface import Database
from photo import Photos
from album import Album
from tag import Tag


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
t = Tag()

# tags = db.get_all_tags()

"""
$ export FLASK_APP=app.py
$ export FLASK_ENV=development
Make it reload on changes:
$ export FLASK_DEBUG=1
$ flask run


lsof -w -n -i tcp:5000
kill -9 processId
"""


@app.route('/edit/tag/<string:tag_name>', methods=['GET'])
def edit_tag(tag_name):
    return render_template('edit_tag.html'), 200


@app.route('/edit/tags')
def edit_tags():
    tag_data = t.get_all_tags()
    return render_template('edit_tags.html', json_data=tag_data), 200


@app.route('/tags/')
def get_tags():
    tag_data = t.get_all_tags()
    # print(tag_data)
    return render_template('tags.html', json_data=tag_data)


@app.route('/tags/<string:tag_name>')
def photos_by_tag_name(tag_name):
    tag_data = t.get_photos_by_tag(tag_name)
    json_data = tag_data
    print(json_data)
    return render_template('tag_photos.html', json_data=json_data)


@app.route('/albums')
def get_albums():
    albums_data = a.get_albums()
    json_data = albums_data
    # print(json_data[0]['large_square'])
    return render_template('albums.html', json_data=json_data), 200


@app.route('/albums/<int:album_id>', methods=['GET'])
def get_album_photos(album_id):
    photo_data = a.get_album_photos(album_id)
    json_data = photo_data
    # print(json_data)
    return render_template('album.html', json_data=json_data), 200


@app.route('/api/photos/')
def get_photos():
    print('\nHello from get_photos\n')
    print(20 * '\n', 'ENTERED')
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
        """
        No arguments
        """
        print(10 * '\n', 'why you no work')
        photo_data = p.get_photos_in_range()
        json_data = photo_data
        # print(json_data)
        return render_template('photos.html', json_data=json_data), 200


@app.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    print('\nHello from get_photo\n')
    photo_data = p.get_photo(photo_id)
    json_data = photo_data
    # json_data = dict(photo_data['photos'])2

    print(json_data)

    return render_template('photo.html', json_data=json_data), 200


@app.route('/', methods=['GET'])
def home():
    photo_data = p.get_photos_in_range()
    json_data = photo_data
    # print(json_data)
    return render_template('photos.html', json_data=json_data), 200


# @app.route('/', methods=['GET', 'POST'])
# def login():
#     error = None
#     status_code = 200

#     if request.method == 'POST':
#         username = request.form.get('username', None)
#         password = request.form.get('password', None)

#         if username == app.config['USERNAME'] and password == app.config['PASSWORD']:
#             flash('you did it, congrats')
#             return render_template('main.html')
#         else:
#             status_code = 401
#             flash('Wrong username and/or password', error)

#     return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
