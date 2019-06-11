import os
import json
import datetime


from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

from common import utils
from common.utils import login_required
from common.exif_util import ExifUtil
from common.resize_photo import PhotoUtil

from upload.uploaded_photos import UploadedPhotos


upload_blueprint = Blueprint('upload', __name__)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Directory for saving photos.
UPLOAD_FOLDER = os.getcwd() + '/static/images'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def upload_file():
    # This really needs to be decomposed, it's not ideal.
    if request.method == 'POST':
        files = request.files.getlist('file')
        # No files selected.
        # This is now prevented on the frontend.
        if 'file' not in request.files:
            # flash('No file selected')
            return redirect(request.url)

        # Handles single or multiple files selected.
        elif len(files) >= 1:
            created = datetime.datetime.now()
            for file in files:
                photo_id = utils.get_id()
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # where the file will be saved
                    save_directory = UPLOAD_FOLDER + \
                        '/{}/{}'.format(created.year, created.month)
                    # check if directory exists if not create it
                    if not os.path.exists(save_directory):
                        os.makedirs(save_directory)
                    # Get all files in the save_directory
                    file_in_dir = os.listdir(save_directory)
                    # Guards against multiple files having the same name.
                    if filename in file_in_dir:
                        temp = filename.split('.')

                        temp[0] = temp[0] + "_" + str(photo_id) + '_o'

                        filename = '.'.join(temp)

                    # Save the original photo.
                    file.save(
                        os.path.join(
                            save_directory, filename))

                    # Try to set the datetime value from the EXIF data.
                    date_taken = ExifUtil.get_datetime_taken(
                        os.path.join(save_directory, filename))

                    try:
                        exif_data = ExifUtil.test_exifread(
                            os.path.join(save_directory, filename))
                    except Exception as e:
                        exif_data = None
                        print('problem reading exif data ', e)

                    # Makes sure the image is the right orientation.
                    PhotoUtil.orientate_save(save_directory, filename)

                    # Adds identifying name to the thumbnail file.
                    thumbnail_name = filename.split('.')
                    thumbnail_name[0] = thumbnail_name[0] + '_lg_sqaure'

                    thumbnail_filename = '.'.join(thumbnail_name)

                    # Construct path to save thumbnail file to.
                    save_path = save_directory + '/'

                    # Creates the thumbnail image.
                    PhotoUtil.square_thumbnail(
                        filename, thumbnail_filename, save_path)

                    # Store the path to the photos in the db.
                    original_path = '/static/images/{}/{}/{}'.format(
                        created.year, created.month, filename)
                    large_square_path = '/static/images/{}/{}/{}'.format(
                        created.year, created.month, thumbnail_filename)

                    up = UploadedPhotos()
                    up.save_photo(
                        photo_id,
                        str(created),
                        original_path,
                        large_square_path,
                        exif_data,
                        date_taken
                    )

                else:
                    flash('Incorrect file type.')
                    return redirect(request.url)

            return redirect(url_for('upload.uploaded_photos_page'), code=302)

    # Get request and initial loading of the upload page.
    return render_template('upload/upload.html'), 200


def show_uploaded(json_data):
    up = UploadedPhotos()
    if session and len(up.get_uploaded_photos()['photos']) > 0:
        json_data['show_session'] = True

    return json_data


@upload_blueprint.route('/test')
@login_required
def test_route():
    up = UploadedPhotos()
    json_data = up.get_uploaded_photos()
    return jsonify(json_data)


@upload_blueprint.route('/photostream', methods=['GET', 'POST'])
@login_required
def to_photostream():
    data = request.get_json()
    up = UploadedPhotos()
    up.add_to_photostream(data['photos'])
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


@upload_blueprint.route('/uploaded')
@login_required
def uploaded_photos_page():
    # React gets the data for this.
    return render_template('upload/uploaded_photos.html'), 200


@upload_blueprint.route('/api/uploaded')
@login_required
def get_uploaded_photos():
    up = UploadedPhotos()
    json_data = up.get_uploaded_photos()
    return jsonify(json_data)


@upload_blueprint.route('/api/uploaded/title', methods=['GET', 'POST'])
@login_required
def update_title():
    d = request.get_json()
    title = d['title'].strip()
    title = utils.make_encoded(title)

    up = UploadedPhotos()

    if up.update_title(d['photoId'], title):
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@upload_blueprint.route('/discard/photo', methods=['GET', 'POST'])
@login_required
def discard_photo():
    """
    Deletes a photo from the upload editor.
    """
    photo_id = request.get_json()
    up = UploadedPhotos()
    result = up.discard_photo(photo_id['photoId'])

    if up.discard_photo(photo_id['photoId']):
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
