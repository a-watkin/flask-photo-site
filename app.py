import json
import os
import datetime
import uuid
import urllib.parse
from functools import wraps


from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json


# my modules

# From common package.
from common.database_interface import Database
from common import name_util
from common.name_util import login_required


from photo import Photos
from album import Album
from tag import Tag
from upload.uploaded_photos import UploadedPhotos
from upload.upload_routes import show_uploaded


# User route import.
from user.user_routes import user_blueprint
from upload.upload_routes import upload_blueprint


app = Flask('app')
app = Flask(__name__.split('.')[0])


# app config
app.config['SECRET_KEY'] = b'\xef\x03\xc8\x96\xb7\xf9\xf3^\x16\xcbz\xd7\x83K\xfa\xcf'


# Register blueprints.

# Login, logout, changing password
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(upload_blueprint, url_prefix="/upload")

db = Database('eigi-data.db')
p = Photos()
a = Album()
t = Tag()
# up = UploadedPhotos()


# $ export FLASK_APP=app.py
# $ export FLASK_ENV=development
# Make it reload on changes:
# $ export FLASK_DEBUG=1
# $ flask run


# lsof -w -n -i tcp:5000
# kill -9 processId

current_user = None


@app.route('/create/album', methods=['GET', 'POST'])
@login_required
def to_new_album():
    # print('hello from to_new_album')
    if request.method == 'GET':
        return render_template('upload_new_album.html'), 200

    if request.method == 'POST':
        album_title = request.form['title']
        album_description = request.form['description']

        if a.get_album_by_name(album_title):
            new_album_data = {
                'album_title': album_title,
                'album_description': album_description
            }

            flash(
                'An album with this name already exists. Please enter a different name.')

            return render_template('create_album.html', data=new_album_data), 200

        else:

            album_id = a.create_album(
                '28035310@N00', album_title, album_description)

            # use album_id to add all uploaded photos to the album
            up = UploadedPhotos()
            up.add_all_to_album(album_id)

            album_data = a.get_album(album_id)

            return redirect('/albums/{}'.format(album_id)), 302


# route that loads the script to select an album
@app.route('/api/select/album')
@login_required
def upload_select_album():
    return render_template('upload_select_album.html'), 200


@app.route('/api/photos/')
def get_photos():
    # print('\nHello from get_photos\n')
    # print(20 * '\n', 'ENTERED')
    args = request.args.to_dict()

    photo_data = None
    # print(args)

    if len(args) > 0:

        if 'offset' in args.keys() and 'limit' not in args.keys():
            if int(args['offset']) <= 0:
                args['offset'] = 0
            # gotta make this an int
            photo_data = p.get_photos_in_range(20, int(args['offset']))

            print(photo_data)

            json_data = photo_data

            # print('args are ', args)
            json_data = show_uploaded(json_data)
            return render_template('photos.html', json_data=json_data), 200
        elif 'offset' not in args.keys() and 'limit' in args.keys():
            # print(9 * '\n')
            # default offset is 0
            photo_data = p.get_photos_in_range(int(args['limit']))
            json_data = photo_data

            json_data = show_uploaded(json_data)
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

            json_data = show_uploaded(json_data)
            return render_template('photos.html', json_data=json_data), 200

    else:
        """
        No arguments
        """
        photo_data = p.get_photos_in_range()
        json_data = photo_data

        # print('\n', session and len(up.get_uploaded_photos()['photos']) > 0)
        # if session and len(up.get_uploaded_photos()['photos']) > 0:
        #     print('\n session present \n')
        #     json_data['show_session'] = True

        # print(json_data)
        # print(10*'\n')

        json_data = show_uploaded(json_data)
        return render_template('photos.html', json_data=json_data), 200


@app.route('/api/getalbums', methods=['GET', 'POST'])
@login_required
def get_albums_json():
    print('get_albums_json called')
    args = request.args.to_dict()

    # print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                # gotta make this an int
                album_data = a.get_albums_in_range(20, int(args['offset']))
                json_data = album_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            album_data = a.get_albums_in_range(20, int(args['offset']))
            json_data = album_data
            return jsonify(album_data)

    if request.method == 'POST':
        print('called api/getalbum with a post request')
        print('test', request.get_json())

        data = request.get_json()

        album_id = data['albumId'][0]

        # add all the uploaded photos to the album
        up = UploadedPhotos()
        up.add_all_to_album(album_id)

        return redirect("/albums/{}".format(album_id), code=302)

        # add_all_to_album

        #     data = request.get_json()
        #     a.add_photos_to_album(data['albumId'], data['photos'])

        #     return redirect("/albums/{}".format(data['albumId']), code=302)


@app.route('/api/getphotos', methods=['GET', 'POST'])
@login_required
def get_photos_json():
    # print()
    # print('hello from get_photos_json')
    # print()
    args = request.args.to_dict()

    # print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                # gotta make this an int
                photo_data = p.get_photos_in_range(20, int(args['offset']))
                json_data = photo_data

                # print('args are ', args)

                json_data = photo_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data
            return jsonify(json_data)

    if request.method == 'POST':

        print('hello from get_photos_json, data passed is ', request.get_json())

        data = request.get_json()
        a.add_photos_to_album(data['albumId'], data['photos'])

        return redirect("/albums/{}".format(data['albumId']), code=302)


@app.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    # print('\nHello from get_photo\n')
    photo_data = p.get_photo(photo_id)
    json_data = photo_data
    # json_data = dict(photo_data['photos'])2
    # print(json_data)
    return render_template('photo.html', json_data=json_data), 200


@app.route('/', methods=['GET'])
def home():
    photo_data = p.get_photos_in_range()
    json_data = photo_data
    json_data = show_uploaded(json_data)
    return render_template('photos.html', json_data=json_data), 200


@app.route('/edit/photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    if request.method == 'GET':
        print(10*'\n')
        photo_data = p.get_photo(photo_id)
        photo_data['title'] = needs_decode(photo_data['title'])

        print('get_photo', photo_data)
        print(10*'\n')
        return render_template('edit_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        # get the value from the form
        new_title = request.form['new_photo_name']

        new_title = check_chars(new_title)

        print(new_title)
        # update the name in the database
        p.update_title(photo_id, new_title)
        photo_data = p.get_photo(photo_id)
        photo_data['title'] = needs_decode(photo_data['title'])
        return render_template('edit_photo.html', json_data=photo_data), 200


@app.route('/delete/photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    if request.method == 'GET':
        photo_data = p.get_photo(photo_id)
        return render_template('delete_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        photo_data = p.get_photo(photo_id)
        # delete the photo
        p.delete_photo(photo_id)
        return render_template('deleted_photo.html', json_data=photo_data), 200


def url_encode_tag(tag_name):
    return urllib.parse.quote(tag_name, safe='')


def url_decode_tag(tag_name):
    return urllib.parse.unquote(tag_name)


def needs_decode(a_str):
    if '%' in a_str:
        return url_decode_tag(a_str)
    else:
        return a_str


def check_forbidden(tag_name):
    print('hello from check_forbidden')
    print(tag_name)

    forbidden = [";", "/", "?", ":", "@", "=", "&", '"', "'", "<", ">",
                 "#", "%", "{", "}", "|", "\\", "^", "~", "[", "]", "`"]
    for char in tag_name:
        if char in forbidden:
            tag_data = t.get_photos_by_tag(
                urllib.parse.quote(tag_name, safe=''))
            tag_data['human_readable_tag'] = tag_name
            return tag_data

    tag_data = t.get_photos_by_tag(tag_name)
    tag_data['human_readable_tag'] = tag_name

    return tag_data


def check_chars(tag_name):
    print('hello from check_chars', tag_name)
    forbidden = [";", "/", "?", ":", "@", "=", "&", '"', "'", "<", ">", " ",
                 "#", "{", "}", "|", "\\", "/", "^", "~", "[", "]", "`"]
    for char in tag_name:
        if char in forbidden:
            print(tag_name, ' needs encoding')
            return url_encode_tag(tag_name)

    return tag_name


@app.route('/api/add/tags', methods=['GET', 'POST'])
@login_required
def add_uploaded_tags():
    print('ADD TAGS METHOD CALLED?')
    # gets data from react

    tag_data = request.get_json()
    print('tags from react ', tag_data)
    # tags are a string when they come in here,
    # they need to be split
    tags = tag_data['tagValues'].split(',')

    for i in range(len(tags)):
        # remove whitespace from front and back of element
        tags[i] = tags[i].strip()
        # make it url safe
        tags[i] = url_encode_tag(tags[i])

    print(tags)

    print('tag_data', tag_data)
    resp = t.add_tags_to_photo(tag_data['photoId'], tags)
    print(resp)
    if resp:
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@app.route('/tags/<string:tag_name>')
def photos_by_tag_name(tag_name):
    # print('hello from photos by tag name, ',
    #       tag_name)
    json_data = t.get_photos_by_tag(tag_name)
    print(json_data)

    if json_data['tag_info']['number_of_photos'] == 0:
        print('handle this \n')

        tag_data = t.get_tag(tag_name)

        return render_template('tag_photos.html', json_data=tag_data)

    return render_template('tag_photos.html', json_data=json_data)


@app.route('/api/tag/photos', methods=['GET', 'POST'])
def get_tag_photos():
    args = request.args.to_dict()

    print('get_tag_photos args, ', args)

    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset < 0:
            offset = 0

        tag_photos_data = t.get_tag_photos_in_range(
            args['tag_name'], 20, offset)

        if offset >= tag_photos_data['tag_info']['number_of_photos']:
            offset = tag_photos_data['tag_info']['number_of_photos']
            pass

        return render_template('tag_photos.html', json_data=tag_photos_data)

    tag_photos_data = t.get_tag_photos_in_range(args['tag_name'])
    return render_template('tag_photos.html', json_data=tag_photos_data)


@app.route('/delete/<string:tag_name>', methods=['GET', 'POST'])
@login_required
def delete_tag(tag_name):
    print('hello from delete_tag passed the value ', tag_name)
    # return 'test'
    if request.method == 'GET':
        tag_data = t.get_tag(tag_name)
        return render_template('delete_tag.html', data=tag_data), 200
    if request.method == 'POST':
        # print('DELETE THE THING', tag_name)
        deleted_tag = t.get_tag(tag_name)
        if t.delete_tag(tag_name):
            # print('no more cucumbers')
            return render_template('deleted_tag.html', data=deleted_tag), 200


@app.route('/tags/')
def get_tags():
    print('hello from get_tags')

    tag_data = t.get_all_tags()
    # tag_data = t.get_all_tags_without_count()
    # print(tag_data)
    return render_template('tags.html', json_data=tag_data)


@app.route('/edit/tags')
@login_required
def edit_tags():
    tag_data = t.get_all_tags()
    return render_template('edit_tags.html', json_data=tag_data), 200


@app.route('/edit/tag/<string:tag_name>', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_name):
    """
    Change tag name.
    """
    print('hello from edit tags')

    if request.method == 'GET':
        print('get received ', tag_name)

        tag_data = t.get_tag(tag_name)

        return render_template('edit_tag.html', data=tag_data), 200

    if request.method == 'POST':
        new_tag_name = request.form['new_tag_name']

        # IF THE THING YOU'RE TRYING TO CHANGE IS IN AN INVALID FORMAT THEN YOU NEED
        # ENCODE THAT instead of its replacement
        old_tag = check_chars(tag_name)
        new_tag = check_chars(new_tag_name)

        print()
        print('old_tag', old_tag, 'new_tag', new_tag)
        print()

        if old_tag == new_tag:
            tag_data = t.get_tag(tag_name)
            return render_template('edit_tag.html', data=tag_data), 200

        update_response = t.update_tag(new_tag, old_tag)

        print('\n', update_response, '\n')

        if update_response:
            # redirect_url = "/edit/tag/{}".format(new_tag)
            # print('INFO ', redirect_url, new_tag_name, tag_name)
            # http://127.0.0.1:5000/edit/tag/17191909
            # you need to return with the photo also
            return redirect(url_for('edit_tag', tag_name=new_tag))
            # return redirect(redirect_url, code=302)

        else:
            flash('There was a problem updating the tag, please contact support.')
            return render_template('edit_tag.html', tag_name=new_tag_name), 200


@app.route('/add/tag/', methods=['GET', 'POST'])
@login_required
def add_tag():
    print('\nHello from add_tag \n')
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
        for i in range(len(tag_data)):
            tag_data[i] = tag_data[i].strip()
            tag_data[i] = check_chars(tag_data[i])

        print('nope', tag_data)

        # add tags to the tag table if needed and associated them with the photo
        t.add_tags_to_photo(photo_id, tag_data)
        # data on the photo to render the view
        photo_data = p.get_photo(args['photo_id'])
        return render_template('photo.html', json_data=photo_data), 200


@app.route('/remove/tag/', methods=['GET', 'POST'])
@login_required
def remove_tag():
    """
    Remove a tag from a photo
    """
    if request.method == 'GET':
        args = request.args.to_dict()
        photo_data = p.get_photo(args['photo_id'])
        # tags = t.get_photo_tags(args['photo_id'])
        # args['tags'] = tags

        print(photo_data)

        # return 'remove tag page'

        return render_template('remove_tags.html', json_data=photo_data), 200


@app.route('/api/get/phototags', methods=['GET', 'POST'])
@login_required
def get_photo_tag_data():
    if request.method == 'GET':
        args = request.args.to_dict()
        photo_data = p.get_photo(args['photo_id'])
        return jsonify(photo_data)
    else:
        data = request.get_json()
        print(data)
        # remove tags here
        print(data['photoId'], data['selectedTags'])

        # for i in range(len(data['selectedTags'])):
        #     data['selectedTags'][i] = check_chars(data['selectedTags'][i])

        t.remove_tags_from_photo(data['photoId'], data['selectedTags'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/albums')
def get_albums():
    albums_data = a.get_albums()
    # print(albums_data)
    json_data = albums_data
    # print(json_data[0]['large_square'])
    return render_template('albums.html', json_data=json_data), 200


@app.route('/delete/album/<string:album_id>', methods=['GET', 'POST'])
@login_required
def delete_album(album_id):
    if request.method == 'GET':
        # get data for that album
        album_data = a.get_album(album_id)
        # print(album_data)
        return render_template('delete_album.html', json_data=album_data)

    if request.method == 'POST':
        album_data = a.get_album(album_id)
        album_title = album_data['title']

        a.delete_album(album_id)

        if a.delete_album(album_id):
            return render_template('deleted_album.html', deleted_album=album_data), 200


@app.route('/albums/<int:album_id>', methods=['GET'])
def get_album_photos(album_id):
    # photo_data = a.get_album_photos(album_id)
    # json_data = photo_data
    photo_data = a.get_album_photos_in_range(album_id)
    return render_template('album.html', json_data=photo_data), 200


@app.route('/add/album', methods=['GET', 'POST'])
@login_required
def create_album():
    if request.method == 'GET':
        return render_template('create_album.html'), 200
    if request.method == 'POST':
        album_title = request.form['title']
        album_description = request.form['description']

        if a.get_album_by_name(album_title):
            new_album_data = {
                'album_title': album_title,
                'album_description': album_description
            }

            flash(
                'An album with this name already exists. Please enter a different name.')

            return render_template('create_album.html', data=new_album_data), 200

        else:

            album_id = a.create_album(
                '28035310@N00', album_title, album_description)

            album_data = a.get_album(album_id)

            return redirect('/edit/album/{}/photos'.format(album_id)), 302


@app.route('/edit/album/<int:album_id>/photos')
@login_required
def add_album_photos(album_id):
    album_data = a.get_album(album_id)
    photo_data = p.get_photos_in_range(20, 0)
    photo_data['album_data'] = album_data
    # print('Hello from add_album_photos ', photo_data)
    return render_template('add_album_photos.html', json_data=photo_data), 200


@app.route('/edit/album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """
    Updates the name and description of an album.
    """
    if request.method == 'GET':
        json_data = a.get_album(album_id)
        return render_template('edit_album.html', json_data=json_data), 200

    if request.method == 'POST':
        album_name = name_util.make_encoded(request.form['name'])

        # album_name = request.form['name']
        album_description = name_util.make_encoded(request.form['description'])
        # add the data to the database

        print(' why oh why oh why....', album_name, album_description)
        a.update_album(album_id, album_name, album_description)
        # print('test', album_id, album_name, album_description)
        json_data = a.get_album(album_id)
        print('what is get album returning? ', json_data)
        return render_template('edit_album.html', json_data=json_data), 200


@app.route('/edit/albums')
@login_required
def edit_albums():
    """
    Lists all the albums.
    """
    print('hello from edit albums')
    albums_data = a.get_albums()
    print(albums_data)
    return render_template('edit_albums.html', json_data=albums_data), 200


@app.route('/api/albumphotos', methods=['GET', 'POST'])
@login_required
def get_album_photos_json():
    """
    Used to pass data to React.
    """
    args = request.args.to_dict()
    # print(args)
    if request.method == 'GET':
        if len(args) > 0:

            if 'limit' not in args.keys():
                args['limit'] = 20

            if 'offset' not in args.keys():
                args['offset'] = 0

            album_data = a.get_album_photos_in_range(
                args['album_id'],
                args['limit'],
                args['offset']
            )
            json_data = album_data
            return jsonify(json_data)

    if request.method == 'POST':
        # print('test', request.get_json())
        data = request.get_json()
        a.remove_photos_from_album(data['albumId'], data['photos'])
        return redirect("/albums/{}".format(data['albumId']), code=302)


@app.route('/api/album/photos', methods=['GET', 'POST'])
def get_album_photos_in_pages():
    args = request.args.to_dict()

    print(args)

    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset <= 0:
            # pass
            offset = 0

        # guards against an offset greater than the number of photos
        if offset >= a.count_photos_in_album(args['album_id']):
            # ok if you want it to return to the start of the pages
            # offset = 0
            pass

        # else:
        album_photos = a.get_album_photos_in_range(
            args['album_id'], 20, offset)
        return render_template('album.html', json_data=album_photos)

    album_photos = a.get_album_photos_in_range(args['tag_name'])
    return render_template('album.html', json_data=album_photos)


@app.route('/edit/album/<int:album_id>/remove/photos', methods=['GET'])
@login_required
def remove_album_photos(album_id):
    album_data = a.get_album(album_id)
    photo_data = a.get_album_photos_in_range(album_id)
    photo_data['album_data'] = album_data
    return render_template('remove_album_photos.html', json_data=photo_data), 200


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True
    )
