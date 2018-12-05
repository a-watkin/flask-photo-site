import json

from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json
from wtforms import Form, BooleanField, StringField, PasswordField, validators
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


@app.route('/edit/tag/<string:tag_name>', methods=['GET', 'POST'])
def edit_tag(tag_name):
    if request.method == 'GET':
        print('\n get message recieved')

        return render_template('edit_tag.html', tag_name=tag_name), 200

    if request.method == 'POST':
        new_tag_name = request.form['new_tag_name']
        # attemp to do database update

        print('POST REQUEST RECIEVED WITH VALUE OF', new_tag_name, tag_name)

        update_response = t.update_tag(new_tag_name, tag_name)

        print('UPDATE RESPONSE', update_response)

        # if the tag is updated then redirect to the edit page for the new tag
        if update_response:

            redirect_url = "/edit/tag/{}".format(new_tag_name)

            print('INFO ', redirect_url, new_tag_name, tag_name)

            # http://127.0.0.1:5000/edit/tag/17191909
            # you need to return with the photo also
            return redirect(redirect_url, code=302)

        else:
            flash('There was a problem updating the tag, please contact support.')
            return render_template('edit_tag.html', tag_name=new_tag_name), 200


@app.route('/delete/<string:tag_name>', methods=['GET', 'POST'])
def delete_tag(tag_name):

    if request.method == 'GET':
        return render_template('delete_tag.html', tag_name=tag_name), 200

    if request.method == 'POST':
        print('DELETE THE THING', tag_name)
        deleted_tag = tag_name

        if t.delete_tag(tag_name):
            print('no more cucumbers')

            return render_template('deleted_tag.html', deleted_tag=deleted_tag), 200


@app.route('/delete/album/<string:album_id>', methods=['GET', 'POST'])
def delete_album(album_id):
    if request.method == 'GET':
        # get data for that album
        album_data = a.get_album(album_id)
        print(album_data)
        return render_template('delete_album.html', json_data=album_data)

    if request.method == 'POST':
        print('DELETE THE THING', album_id)
        # deleted_tag = tag_name

        album_data = a.get_album(album_id)
        album_title = album_data['title']

        a.delete_album(album_id)

        print(album_title)
        if a.delete_album(album_id):
            print('no more album')

            return render_template('deleted_album.html', deleted_album=album_title), 200

        #     return render_template('deleted_tag.html', deleted_tag=deleted_tag), 200


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
    # print(json_data)
    return render_template('tag_photos.html', json_data=json_data)


@app.route('/add/tag/', methods=['GET', 'POST'])
def add_tag():
    args = request.args.to_dict()

    if request.method == 'GET':
        photo_data = p.get_photo(args['photo_id'])
        return render_template('add_tag.html', json_data=photo_data), 200

    if request.method == 'POST':
        # get the photo_id
        photo_id = args['photo_id']
        # get the new tags from the form
        tag_data = request.form['new_tag_name']
        # This is a string of values
        tag_data = tag_data.split(',')
        # add tags to the tag table if needed and associated them with the photo
        t.add_tags_to_photo(photo_id, tag_data)
        # data on the photo to render the view
        photo_data = p.get_photo(args['photo_id'])
        return render_template('photo.html', json_data=photo_data), 200


@app.route('/albums')
def get_albums():
    albums_data = a.get_albums()
    # print(albums_data)
    json_data = albums_data
    # print(json_data[0]['large_square'])
    return render_template('albums.html', json_data=json_data), 200


@app.route('/albums/<int:album_id>', methods=['GET'])
def get_album_photos(album_id):
    photo_data = a.get_album_photos(album_id)
    json_data = photo_data
    # print(json_data)
    return render_template('album.html', json_data=json_data), 200


@app.route('/edit/albums')
def edit_albums():
    """
    Lists all the albums.
    """
    albums_data = a.get_albums()
    print(albums_data)
    return render_template('edit_albums.html', json_data=albums_data), 200


@app.route('/edit/album/<int:album_id>', methods=['GET', 'POST'])
def edit_album(album_id):
    """
    Updates the name and description of an album.
    """
    if request.method == 'GET':
        json_data = a.get_album(album_id)
        return render_template('edit_album.html', json_data=json_data), 200

    if request.method == 'POST':
        album_name = request.form['name']
        album_description = request.form['description']
        # add the data to the database

        a.update_album(album_id, album_name, album_description)

        print('test', album_id, album_name, album_description)
        json_data = a.get_album(album_id)
        return render_template('edit_album.html', json_data=json_data), 200


@app.route('/api/albumphotos', methods=['GET', 'POST'])
def get_album_photos_json():
    args = request.args.to_dict()

    print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                # gotta make this an int
                photo_data = a.get_album_photos_in_range(
                    args['album_id'],
                    20, int(args['offset']))
                json_data = photo_data

                print('args are ', args)

                json_data = photo_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            photo_data = a.get_album_photos_in_range(
                args['album_id'],
                20, int(args['offset']))
            json_data = photo_data
            return jsonify(json_data)

    # if request.method == 'POST':

    #     print('test', request.get_json())

    #     data = request.get_json()
    #     a.add_photos_to_album(data['albumId'], data['photos'])

    #     return redirect("/albums/{}".format(data['albumId']), code=302)


@app.route('/edit/album/<int:album_id>/photos')
def add_album_photos(album_id):
    album_data = a.get_album(album_id)

    # i need recent photos too
    args = request.args.to_dict()
    args['offset'] = 0
    photo_data = p.get_photos_in_range(20, int(args['offset']))

    photo_data['album_data'] = album_data

    print(photo_data)
    # print(album_data)

    return render_template('add_album_photos.html', json_data=photo_data), 200


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


@app.route('/api/getphotos', methods=['GET', 'POST'])
def get_photos_json():
    args = request.args.to_dict()

    print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                # gotta make this an int
                photo_data = p.get_photos_in_range(20, int(args['offset']))
                json_data = photo_data

                print('args are ', args)

                json_data = photo_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data
            return jsonify(json_data)

    if request.method == 'POST':

        print('test', request.get_json())

        data = request.get_json()
        a.add_photos_to_album(data['albumId'], data['photos'])

        return redirect("/albums/{}".format(data['albumId']), code=302)


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
