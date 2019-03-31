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


@app.route('/api/getphotos', methods=['GET'])
@login_required
def get_photos_json():
    """
    Gets photo data for us in React to select photos for albums.
    """
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
        photo_data['title'] = name_util.make_decoded(photo_data['title'])

        print('get_photo', photo_data)
        print(10*'\n')
        return render_template('edit_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        # get the value from the form
        new_title = request.form['new_photo_name']

        new_title = name_util.make_encoded(new_title)

        print(new_title)
        # update the name in the database
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
        # delete the photo
        p.delete_photo(photo_id)
        return render_template('deleted_photo.html', json_data=photo_data), 200


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
        tags[i] = name_util.url_encode_tag(tags[i])

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
        old_tag = name_util.make_encoded(tag_name)
        new_tag = name_util.make_encoded(new_tag_name)

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
            tag_data[i] = name_util.make_encoded(tag_data[i])

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

        t.remove_tags_from_photo(data['photoId'], data['selectedTags'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True
    )
