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
from album.album import Album
from tag import Tag
from upload.uploaded_photos import UploadedPhotos
from upload.upload_routes import show_uploaded


# User route import.
from user.user_routes import user_blueprint
from upload.upload_routes import upload_blueprint
from album.album_routes import album_blueprint


app = Flask('app')
app = Flask(__name__.split('.')[0])


# app config
app.config['SECRET_KEY'] = b'\xef\x03\xc8\x96\xb7\xf9\xf3^\x16\xcbz\xd7\x83K\xfa\xcf'


# Register blueprints.

# Login, logout, changing password
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(upload_blueprint, url_prefix="/upload")
app.register_blueprint(album_blueprint, url_prefix="/album")

db = Database('eigi-data.db')
p = Photos()
t = Tag()


@app.route('/api/photos/')
def get_photos():
    args = request.args.to_dict()

    photo_data = None

    if len(args) > 0:
        if 'offset' in args.keys() and 'limit' not in args.keys():
            if int(args['offset']) <= 0:
                args['offset'] = 0
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data
            json_data = show_uploaded(json_data)
            return render_template('photos.html', json_data=json_data), 200
        elif 'offset' not in args.keys() and 'limit' in args.keys():
            # Default offset is 0.
            photo_data = p.get_photos_in_range(int(args['limit']))
            json_data = photo_data

            json_data = show_uploaded(json_data)
            return render_template('photos.html', json_data=json_data), 200

        else:
            # Both offset and limit are present
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
        # No arguments.
        photo_data = p.get_photos_in_range()
        json_data = photo_data
        json_data = show_uploaded(json_data)
        return render_template('photos.html', json_data=json_data), 200


@app.route('/api/getphotos', methods=['GET'])
@login_required
def get_photos_json():
    """
    Gets photo data for us in React to select photos for albums.
    """
    args = request.args.to_dict()

    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                photo_data = p.get_photos_in_range(20, int(args['offset']))
                json_data = photo_data

                json_data = photo_data
                return jsonify(json_data)
        else:
            args['offset'] = 0
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data
            return jsonify(json_data)


@app.route('/api/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    photo_data = p.get_photo(photo_id)
    json_data = photo_data
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
        photo_data = p.get_photo(photo_id)
        photo_data['title'] = name_util.make_decoded(photo_data['title'])
        return render_template('edit_photo.html', json_data=photo_data), 200

    if request.method == 'POST':
        # Get the value from the form.
        new_title = request.form['new_photo_name']
        new_title = name_util.make_encoded(new_title)
        p.update_title(photo_id, new_title)
        photo_data = p.get_photo(photo_id)
        photo_data['title'] = name_util.make_decoded(photo_data['title'])
        return render_template('edit_photo.html', json_data=photo_data), 200


@app.route('/delete/photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    if request.method == 'GET':
        photo_data = p.get_photo(photo_id)
        return render_template('delete_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        photo_data = p.get_photo(photo_id)
        p.delete_photo(photo_id)
        return render_template('deleted_photo.html', json_data=photo_data), 200


@app.route('/api/add/tags', methods=['GET', 'POST'])
@login_required
def add_uploaded_tags():
    tag_data = request.get_json()
    tags = tag_data['tagValues'].split(',')

    for i in range(len(tags)):
        # Remove whitespace from front and back of tags.
        tags[i] = tags[i].strip()
        # Make it url safe.
        tags[i] = name_util.url_encode_tag(tags[i])

    resp = t.add_tags_to_photo(tag_data['photoId'], tags)

    if resp:
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@app.route('/tags/<string:tag_name>')
def photos_by_tag_name(tag_name):
    json_data = t.get_photos_by_tag(tag_name)

    if json_data['tag_info']['number_of_photos'] == 0:
        tag_data = t.get_tag(tag_name)

        return render_template('tag_photos.html', json_data=tag_data)

    return render_template('tag_photos.html', json_data=json_data)


@app.route('/api/tag/photos', methods=['GET', 'POST'])
def get_tag_photos():
    args = request.args.to_dict()

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
    if request.method == 'GET':
        tag_data = t.get_tag(tag_name)
        return render_template('delete_tag.html', data=tag_data), 200
    if request.method == 'POST':
        deleted_tag = t.get_tag(tag_name)
        if t.delete_tag(tag_name):
            return render_template('deleted_tag.html', data=deleted_tag), 200


@app.route('/tags/')
def get_tags():
    tag_data = t.get_all_tags()
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
    if request.method == 'GET':
        tag_data = t.get_tag(tag_name)

        return render_template('edit_tag.html', data=tag_data), 200

    if request.method == 'POST':
        new_tag_name = request.form['new_tag_name']
        # IF THE THING YOU'RE TRYING TO CHANGE IS IN AN INVALID FORMAT THEN YOU NEED
        # ENCODE THAT instead of its replacement
        old_tag = name_util.make_encoded(tag_name)
        new_tag = name_util.make_encoded(new_tag_name)

        if old_tag == new_tag:
            tag_data = t.get_tag(tag_name)
            return render_template('edit_tag.html', data=tag_data), 200

        update_response = t.update_tag(new_tag, old_tag)

        if update_response:
            return redirect(url_for('edit_tag', tag_name=new_tag))

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
            tag_data[i] = name_util.make_encoded(tag_data[i])

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

        t.remove_tags_from_photo(data['photoId'], data['selectedTags'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True
    )
