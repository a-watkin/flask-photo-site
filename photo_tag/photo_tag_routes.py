import json

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash


from common.utils import login_required
from photo.photo import Photo
from photo_tag.photo_tag import PhotoTag

# /photo/tag
photo_tag_blueprint = Blueprint('tag', __name__)

# Removed post request here.
@photo_tag_blueprint.route('/<string:tag_name>', methods=['GET'])
def get_tag_photos(tag_name=None):
    args = request.args.to_dict()
    pt = PhotoTag()

    # for testing
    pt.check_for_orphaned_photo_tag()

    if tag_name is None:
        tag_name = args['tag_name']

    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset <= 0:
            offset = 0

        tag_photos_data = pt.get_tag_photos_in_range(
            args['tag_name'], 20, offset)

        return render_template('photo_tag/tag_photos.html', json_data=tag_photos_data)

    tag_photos_data = pt.get_tag_photos_in_range(tag_name)
    return render_template('photo_tag/tag_photos.html', json_data=tag_photos_data)


@photo_tag_blueprint.route('/delete/<string:tag_name>', methods=['GET', 'POST'])
@login_required
def delete_tag(tag_name):
    if request.method == 'GET':
        pt = PhotoTag()
        tag_data = pt.get_tag(tag_name)
        return render_template('photo_tag/delete_tag.html', data=tag_data), 200

    if request.method == 'POST':
        pt = PhotoTag()
        deleted_tag = pt.get_tag(tag_name)
        if pt.delete_tag(tag_name):
            return render_template('photo_tag/deleted_tag.html', data=deleted_tag), 200


@photo_tag_blueprint.route('/')
def get_tags():
    pt = PhotoTag()
    tag_data = pt.get_all_tags()
    return render_template('photo_tag/tags.html', json_data=tag_data)


@photo_tag_blueprint.route('/edit/tags')
@login_required
def edit_tags():
    pt = PhotoTag()
    tag_data = pt.get_all_tags()
    return render_template('photo_tag/edit_tags.html', json_data=tag_data), 200


@photo_tag_blueprint.route('/edit/<string:tag_name>', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_name):
    """
    A GET request returns a form to edit the tag name.

    A POST request changes the given tag name to the one provided in the form data.
    """
    if request.method == 'GET':
        pt = PhotoTag()
        tag_data = pt.get_tag(tag_name)
        return render_template('photo_tag/edit_tag.html', data=tag_data)

    if request.method == 'POST':
        pt = PhotoTag()
        new_tag_name = request.form['new_tag_name']
        old_tag = tag_name

        update_response = pt.update_tag(new_tag_name, old_tag)

        if update_response:
            return render_template('photo_tag/edit_tag.html', data=update_response)

        else:
            flash('There was a problem updating the tag, please contact support.')
            return redirect(url_for('photo_tag/photo_tag.edit_tag', tag_name=new_tag_name))


@photo_tag_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_tag():
    # This should still work but you would have to pass it the current tags mixed with the new ones.
    args = request.args.to_dict()
    if request.method == 'GET':
        p = Photo()
        pt = PhotoTag()
        photo_data = p.get_photo(args['photo_id'])
        # Get all tags belonging to the photo.
        photo_tags = pt.get_human_readable_photo_tag_list(args['photo_id'])
        photo_data['human_readable_tags'] = photo_tags
        return render_template('photo_tag/add_tag.html', json_data=photo_data), 200

    if request.method == 'POST':
        photo_id = args['photo_id']
        # Get the new tags from the form.
        tag_data = request.form['new_tag_name']
        # tag_data is a str and so needs splitting into a list.
        tag_data = tag_data.split(',')
        # Associate the tags with the photo.
        pt = PhotoTag()
        pt.add_tags_to_photo(photo_id, tag_data)
        # Redirect to get photo.
        return redirect(url_for('photo.get_photo', photo_id=photo_id))


@photo_tag_blueprint.route('/remove', methods=['GET', 'POST'])
@login_required
def remove_tag():
    """
    Remove a tag from a photo
    """
    if request.method == 'GET':
        args = request.args.to_dict()
        p = Photo()
        photo_data = p.get_photo(args['photo_id'])
        return render_template('photo_tag/remove_tags.html', json_data=photo_data), 200


@photo_tag_blueprint.route('/api/get/phototags', methods=['GET', 'POST'])
@login_required
def get_photo_tag_data():
    """
    Used by tag_selector.js

    Returns tag data for a specific photo in JSON format in response to a GET request.

    Removes the specified tags in response to a POST request.
    """
    if request.method == 'GET':
        args = request.args.to_dict()
        p = Photo()
        photo_data = p.get_photo(args['photo_id'])
        return jsonify(photo_data)

    else:
        pt = PhotoTag()
        data = request.get_json()
        pt.remove_tags_from_photo(data['photoId'], data['selectedTags'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@photo_tag_blueprint.route('/api/add/tags', methods=['GET', 'POST'])
@login_required
def add_uploaded_tags():
    """
    Gets tag data from React.

    Updates tag data for a photo in upload on the fly.

    Used by upload_editor.js
    """
    pt = PhotoTag()
    tag_data = request.get_json()
    tags = tag_data['tagValues'].split(',')

    resp = pt.add_tags_to_photo(tag_data['photoId'], tags)

    if resp:
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
