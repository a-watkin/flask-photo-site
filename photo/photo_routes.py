from flask import Blueprint, render_template, request, jsonify


from album.album import Album
from photo_tag.photo_tag import PhotoTag
from upload.uploaded_photos import UploadedPhotos

from photo.photo import Photo
from upload.upload_routes import show_uploaded

from common.utils import login_required
from common import utils


photo_blueprint = Blueprint('photo', __name__)


@photo_blueprint.route('/photo', methods=['GET'])
def home():
    p = Photo()
    photo_data = p.get_photos_in_range()
    json_data = photo_data
    json_data = show_uploaded(json_data)
    return render_template('photos.html', json_data=json_data), 200


@photo_blueprint.route('/')
def get_photos():
    args = request.args.to_dict()

    photo_data = None

    if len(args) > 0:
        if 'offset' in args.keys() and 'limit' not in args.keys():
            offset = int(args['offset'])
            if offset <= 0:
                offset = 0

            p = Photo()
            photo_data = p.get_photos_in_range(20, offset)
            json_data = photo_data
            json_data = show_uploaded(json_data)
            return render_template('photo/photos.html', json_data=json_data), 200

        # Both offset and limit present.
        elif 'offset' not in args.keys() and 'limit' in args.keys():
            p = Photo()
            # Default offset is 0.
            photo_data = p.get_photos_in_range(int(args['limit']))
            json_data = photo_data

            json_data = show_uploaded(json_data)
            return render_template('photo/photos.html', json_data=json_data), 200

        else:
            # Both offset and limit are present
            if 'offset' in args.keys():
                offset = int(args['offset'])

                if offset <= 0:
                    offset = 0

            if int(args['limit']) <= 0:
                args['offset'] = 0

            p = Photo()
            photo_data = p.get_photos_in_range(
                int(args['limit']), int(args['offset'])
            )
            json_data = photo_data
            json_data = show_uploaded(json_data)
            return render_template('photo/photos.html', json_data=json_data), 200

    else:
        p = Photo()
        # If the request has no arguments.
        photo_data = p.get_photos_in_range()
        json_data = photo_data
        json_data = show_uploaded(json_data)
        return render_template('photo/photos.html', json_data=json_data), 200


@photo_blueprint.route('/photo/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    p = Photo()
    photo_data = p.get_photo(photo_id)
    json_data = photo_data
    return render_template('photo/photo.html', json_data=json_data), 200


@photo_blueprint.route('/edit/photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    if request.method == 'GET':
        p = Photo()
        photo_data = p.get_photo(photo_id)
        photo_data['title'] = utils.make_decoded(photo_data['title'])
        return render_template('photo/edit_photo.html', json_data=photo_data), 200

    if request.method == 'POST':
        p = Photo()
        # Get the value from the form.
        new_title = request.form['new_photo_name']
        new_title = utils.make_encoded(new_title)
        p.update_title(photo_id, new_title)
        photo_data = p.get_photo(photo_id)
        photo_data['title'] = utils.make_decoded(photo_data['title'])
        return render_template('photo/edit_photo.html', json_data=photo_data), 200


@photo_blueprint.route('/delete/photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    if request.method == 'GET':
        p = Photo()
        photo_data = p.get_photo(photo_id)
        return render_template('photo/delete_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        p = Photo()
        photo_data = p.get_photo(photo_id)
        p.delete_photo(photo_id)
        return render_template('photo/deleted_photo.html', json_data=photo_data), 200


@photo_blueprint.route('/api/getphotos', methods=['GET'])
@login_required
def get_photos_json():
    """
    Gets photo data for us in React to select photos for albums.
    """
    args = request.args.to_dict()

    if request.method == 'GET':
        p = Photo()
        if len(args) > 0:

            if 'offset' in args.keys() and 'limit' not in args.keys():
                if int(args['offset']) <= 0:
                    args['offset'] = 0
                photo_data = p.get_photos_in_range(20, int(args['offset']))

                json_data = photo_data
                return jsonify(json_data)
        else:
            p = Photo()
            args['offset'] = 0
            photo_data = p.get_photos_in_range(20, int(args['offset']))
            json_data = photo_data
            return jsonify(json_data)
