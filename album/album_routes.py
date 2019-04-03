import json


from flask import Blueprint, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json

from album.album import Album
from upload.uploaded_photos import UploadedPhotos
from photo.photo import Photo

from common.name_util import login_required
from common import name_util


album_blueprint = Blueprint('album', __name__)


@album_blueprint.route('/')
def get_albums():
    a = Album()
    albums_data = a.get_albums()
    json_data = albums_data
    return render_template('album/albums.html', json_data=json_data), 200


@album_blueprint.route('/<int:album_id>', methods=['GET'])
def get_album_photos(album_id):
    a = Album()
    photo_data = a.get_album_photos_in_range(album_id)
    return render_template('album/album.html', json_data=photo_data), 200


@album_blueprint.route('/delete/<string:album_id>', methods=['GET', 'POST'])
@login_required
def delete_album(album_id):
    if request.method == 'GET':
        a = Album()
        album_data = a.get_album(album_id)
        return render_template('album/delete_album.html', json_data=album_data)

    if request.method == 'POST':
        a = Album()
        album_data = a.get_album(album_id)
        album_title = album_data['title']

        a.delete_album(album_id)

        if a.delete_album(album_id):
            return render_template('album/deleted_album.html', deleted_album=album_data), 200


@album_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def create_album():
    if request.method == 'GET':
        return render_template('album/create_album.html'), 200
    if request.method == 'POST':
        album_title = request.form['title']
        album_description = request.form['description']

        a = Album()

        if a.get_album_by_name(album_title):
            new_album_data = {
                'album_title': album_title,
                'album_description': album_description
            }

            flash(
                'An album with this name already exists. Please enter a different name.')

            return render_template('album/create_album.html', data=new_album_data), 200

        else:

            album_id = a.create_album(
                '28035310@N00', album_title, album_description)

            album_data = a.get_album(album_id)

            return redirect('album/edit/{}/photos'.format(album_id)), 302


@album_blueprint.route('/edit/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    """
    Updates the name and description of an album.
    """
    if request.method == 'GET':
        a = Album()
        json_data = a.get_album(album_id)
        return render_template('album/edit_album.html', json_data=json_data), 200

    if request.method == 'POST':
        a = Album()
        album_name = name_util.make_encoded(request.form['name'])
        album_description = name_util.make_encoded(request.form['description'])
        a.update_album(album_id, album_name, album_description)
        json_data = a.get_album(album_id)
        return render_template('album/edit_album.html', json_data=json_data), 200


@album_blueprint.route('/edit/albums')
@login_required
def edit_albums():
    """
    Lists all the albums.
    """
    a = Album()
    albums_data = a.get_albums()
    return render_template('album/edit_albums.html', json_data=albums_data), 200


@album_blueprint.route('/photos', methods=['GET', 'POST'])
def get_album_photos_in_pages():
    args = request.args.to_dict()

    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset <= 0:
            offset = 0

        a = Album()

        # Guards against an offset greater than the number of photos.
        if offset >= a.count_photos_in_album(args['album_id']):
            # 20 here is the limit of the photos returned.
            # offset - 20 means the offset is not incremented.
            album_photos = a.get_album_photos_in_range(
                args['album_id'], 20, offset - 20)
            return render_template('album/album.html', json_data=album_photos)
        else:
            album_photos = a.get_album_photos_in_range(
                args['album_id'], 20, offset)
            return render_template('album/album.html', json_data=album_photos)

    a = Album()
    album_photos = a.get_album_photos_in_range(args['tag_name'])
    return render_template('album/album.html', json_data=album_photos)


@album_blueprint.route('/edit/<int:album_id>/remove/photos', methods=['GET', 'POST'])
@login_required
def remove_album_photos(album_id):
    if request.method == 'GET':
        a = Album()
        album_data = a.get_album(album_id)
        photo_data = a.get_album_photos_in_range(album_id)
        photo_data['album_data'] = album_data
        return render_template('album/remove_album_photos.html', json_data=photo_data), 200
    if request.method == 'POST':
        data = request.get_json()
        a = Album()
        a.remove_photos_from_album(data['albumId'], data['photos'])
        return redirect("album/{}".format(data['albumId']), code=302)


@album_blueprint.route('/edit/<int:album_id>/photos', methods=['GET', 'POST'])
@login_required
def add_album_photos(album_id):
    """
    Returns add_album_photos which loads a React script 
    to select photos to add to the album.

    Adds selected photos to the album upon a POST request.
    """
    if request.method == 'GET':
        a = Album()
        p = Photo()
        album_data = a.get_album(album_id)
        photo_data = p.get_photos_in_range(20, 0)
        photo_data['album_data'] = album_data
        return render_template('album/add_album_photos.html', json_data=photo_data), 200
    if request.method == 'POST':
        data = request.get_json()
        a = Album()
        a.add_photos_to_album(data['albumId'], data['photos'])
        return redirect("/album/{}".format(data['albumId']), code=302)


@album_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def to_new_album():
    """
    Adds uploaded photos to a new album.
    """
    if request.method == 'GET':
        return render_template('album/upload_new_album.html'), 200

    if request.method == 'POST':
        album_title = request.form['title']
        album_description = request.form['description']

        a = Album()

        if a.get_album_by_name(album_title):
            new_album_data = {
                'album_title': album_title,
                'album_description': album_description
            }

            flash(
                'An album with this name already exists. Please enter a different name.')

            return render_template('album/create_album.html', data=new_album_data), 200

        else:
            album_id = a.create_album(
                '28035310@N00', album_title, album_description)

            # Uses album_id to add all uploaded photos to the album.
            up = UploadedPhotos()
            up.add_all_to_album(album_id)
            album_data = a.get_album(album_id)
            return redirect('album/{}'.format(album_id)), 302


# Gets album photos as JSON for React.
@album_blueprint.route('/api/albumphotos', methods=['GET'])
@login_required
def get_album_photos_json():
    """
    Used to pass data to React.
    """
    args = request.args.to_dict()
    if request.method == 'GET':
        a = Album()
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


@album_blueprint.route('/api/select/album')
@login_required
def upload_select_album():
    print('getting here?')
    """
    Returns upload_select_album page which loads a React script to select an album.
    """
    return render_template('album/upload_select_album.html'), 200

# Gets albums as JSON for use in React.
@album_blueprint.route('/api/getalbums', methods=['GET', 'POST'])
@login_required
def get_albums_json():
    """
    Gets JSON data for use in React to select an album.

    Albums are given in increments of 20.

    Also adds uploaded photos to the selected album upon a post request.
    """
    args = request.args.to_dict()
    if request.method == 'GET':
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                a = Album()
                # Arg needs converting to an int.
                album_data = a.get_albums_in_range(20, int(args['offset']))
                json_data = album_data
                return jsonify(json_data)

        else:
            args['offset'] = 0
            a = Album()
            album_data = a.get_albums_in_range(20, int(args['offset']))
            json_data = album_data
            return jsonify(album_data)

    # This should probably be in its own function.
    if request.method == 'POST':
        data = request.get_json()
        album_id = data['albumId'][0]
        # Add all the uploaded photos to the album.
        up = UploadedPhotos()
        up.add_all_to_album(album_id)
        return redirect("album/{}".format(album_id), code=302)
