from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session


from common.name_util import login_required
from photo.photo import Photo
from photo_tag.photo_tag import PhotoTag


photo_tag_blueprint = Blueprint('photo_tag', __name__)

# Tags
@photo_tag_blueprint.route('/api/add/tags', methods=['GET', 'POST'])
@login_required
def add_uploaded_tags():
    pt = PhotoTag()
    tag_data = request.get_json()
    tags = tag_data['tagValues'].split(',')

    for i in range(len(tags)):
        # Remove whitespace from front and back of tags.
        tags[i] = tags[i].strip()
        # Make it url safe.
        tags[i] = name_util.url_encode_tag(tags[i])

    resp = pt.add_tags_to_photo(tag_data['photoId'], tags)

    if resp:
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@photo_tag_blueprint.route('/tags/<string:tag_name>')
def photos_by_tag_name(tag_name):
    pt = PhotoTag()
    json_data = pt.get_photos_by_tag(tag_name)

    if json_data['tag_info']['number_of_photos'] == 0:
        tag_data = pt.get_tag(tag_name)

        return render_template('tag_photos.html', json_data=tag_data)

    return render_template('tag_photos.html', json_data=json_data)


@photo_tag_blueprint.route('/api/tag/photos', methods=['GET', 'POST'])
def get_tag_photos():
    args = request.args.to_dict()
    pt = PhotoTag()
    if 'offset' in args.keys():
        offset = int(args['offset'])

        if offset < 0:
            offset = 0

        tag_photos_data = pt.get_tag_photos_in_range(
            args['tag_name'], 20, offset)

        if offset >= tag_photos_data['tag_info']['number_of_photos']:
            offset = tag_photos_data['tag_info']['number_of_photos']
            pass

        return render_template('tag_photos.html', json_data=tag_photos_data)

    tag_photos_data = pt.get_tag_photos_in_range(args['tag_name'])
    return render_template('tag_photos.html', json_data=tag_photos_data)


@photo_tag_blueprint.route('/delete/<string:tag_name>', methods=['GET', 'POST'])
@login_required
def delete_tag(tag_name):
    if request.method == 'GET':
        pt = PhotoTag()
        tag_data = pt.get_tag(tag_name)
        return render_template('delete_tag.html', data=tag_data), 200
    if request.method == 'POST':
        pt = PhotoTag()
        deleted_tag = pt.get_tag(tag_name)
        if pt.delete_tag(tag_name):
            return render_template('deleted_tag.html', data=deleted_tag), 200


@photo_tag_blueprint.route('/tags/')
def get_tags():
    pt = PhotoTag()
    tag_data = pt.get_all_tags()
    return render_template('tags.html', json_data=tag_data)


@photo_tag_blueprint.route('/edit/tags')
@login_required
def edit_tags():
    pt = PhotoTag()
    tag_data = pt.get_all_tags()
    return render_template('edit_tags.html', json_data=tag_data), 200


@photo_tag_blueprint.route('/edit/tag/<string:tag_name>', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_name):
    """
    Change tag name.
    """
    if request.method == 'GET':
        pt = PhotoTag()
        tag_data = pt.get_tag(tag_name)
        return render_template('edit_tag.html', data=tag_data), 200

    if request.method == 'POST':
        pt = PhotoTag()
        new_tag_name = request.form['new_tag_name']
        old_tag = tag_name

        update_response = pt.update_tag(new_tag, old_tag)

        if update_response:
            return redirect(url_for('edit_tag', tag_name=new_tag))

        else:
            flash('There was a problem updating the tag, please contact support.')
            return render_template('edit_tag.html', tag_name=new_tag_name), 200


@photo_tag_blueprint.route('/add/tag/', methods=['GET', 'POST'])
@login_required
def add_tag():
    print('hello from add_tag')
    args = request.args.to_dict()
    if request.method == 'GET':
        p = Photo()
        # pt = PhotoTag()
        photo_data = p.get_photo(args['photo_id'])
        return render_template('add_tag.html', json_data=photo_data), 200
    if request.method == 'POST':
        photo_id = args['photo_id']
        # Get the new tags from the form.
        tag_data = request.form['new_tag_name']
        # tag_data is a str and so needs splitting into a list.
        tag_data = tag_data.split(',')
        # Associate the tags with the photo.
        pt = PhotoTag()
        pt.add_tags_to_photo(photo_id, tag_data)
        # Get photo to return to template.
        p = Photo()
        photo_data = p.get_photo(args['photo_id'])
        return render_template('photo.html', json_data=photo_data), 200


@photo_tag_blueprint.route('/remove/tag/', methods=['GET', 'POST'])
@login_required
def remove_tag():
    """
    Remove a tag from a photo
    """
    if request.method == 'GET':
        args = request.args.to_dict()
        photo_data = p.get_photo(args['photo_id'])
        return render_template('remove_tags.html', json_data=photo_data), 200


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
        photo_data = p.get_photo(args['photo_id'])
        return jsonify(photo_data)
    else:
        pt = PhotoTag()
        data = request.get_json()
        pt.remove_tags_from_photo(data['photoId'], data['selectedTags'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
