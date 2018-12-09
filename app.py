import json
import os
import datetime
import uuid

from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify
from flask import json
from werkzeug.utils import secure_filename
# from wtforms import Form, BooleanField, StringField, PasswordField, validators

# my modules
from database_interface import Database
from photo import Photos
from album import Album
from tag import Tag
from resize_photo import square_thumbnail


UPLOAD_FOLDER = os.getcwd() + '/static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask('app')
app = Flask(__name__.split('.')[0])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')

        # No files selected
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)

        # Single or multiple files selected
        elif len(files) >= 1:
            created = datetime.datetime.now()
            print('MULTIPLE FILES')
            for file in files:
                if allowed_file(file.filename):
                    print()
                    print(file.filename)
                    print()
                    filename = secure_filename(file.filename)

                    # where the file will be saved
                    save_directory = UPLOAD_FOLDER + \
                        '/{}/{}'.format(created.year, created.month)
                    # check if directory exists if not create it
                    if not os.path.exists(save_directory):
                        os.makedirs(save_directory)

                    # Get all files in the directory
                    file_in_dir = os.listdir(save_directory)
                    # this guards against multiple files having the same name
                    # a problem here is that it also allows the same file to be uploaded
                    # multiple times
                    if file.filename in file_in_dir:
                        temp = filename.split('.')
                        identifier = str(uuid.uuid1()).split('-')[0]

                        temp[0] = temp[0] + "_" + identifier

                        file.filename = '.'.join(temp)

                    # save the file path
                    file.save(os.path.join(
                        save_directory, file.filename))

                    # save path to the photo
                    file_path = save_directory + '/' + filename
                    photo_id = str(int(uuid.uuid4()))[0:10]
                    print(file_path)

                    # save a thumbnail of the photo
                    thumbnail_name = filename.split('.')
                    thumbnail_name[0] = thumbnail_name[0] + '_lg_sqaure'

                    # construct path to save thumbnail to
                    save_path = save_directory + '/'
                    print('.'.join(
                        thumbnail_name))
                    print(save_path)
                    square_thumbnail(filename, '.'.join(
                        thumbnail_name), save_path)

                else:
                    flash('Incorrect file type.')
                    return redirect(request.url)

            # write to temp table, return page where things can be editied
            # return redirect(url_for('upload_file',
            #                         filename=filename))

            # Return all the data about the uloaded photos

            return render_template('uploaded_photos.html', ), 200

    # Get request and initial loading of the upload page
    return render_template('upload.html'), 200


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


@app.route('/edit/photo<int:photo_id>', methods=['GET', 'POST'])
def edit_photo(photo_id):
    if request.method == 'GET':
        photo_data = p.get_photo(photo_id)
        return render_template('edit_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        # get the value from the form
        new_title = request.form['new_photo_name']
        print(new_title)
        # update the name in the database
        p.update_title(photo_id, new_title)
        photo_data = p.get_photo(photo_id)
        return render_template('edit_photo.html', json_data=photo_data), 200


@app.route('/delete/photo<int:photo_id>', methods=['GET', 'POST'])
def delete_photo(photo_id):
    if request.method == 'GET':
        photo_data = p.get_photo(photo_id)
        return render_template('delete_photo.html', json_data=photo_data), 200
    if request.method == 'POST':
        photo_data = p.get_photo(photo_id)
        # delete the photo
        p.delete_photo(photo_id)
        return render_template('deleted_photo.html', json_data=photo_data), 200


@app.route('/tags/<string:tag_name>')
def photos_by_tag_name(tag_name):
    tag_data = t.get_photos_by_tag(tag_name)
    json_data = tag_data
    # print(json_data)
    return render_template('tag_photos.html', json_data=json_data)


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


@app.route('/tags/')
def get_tags():
    tag_data = t.get_all_tags()
    # print(tag_data)
    return render_template('tags.html', json_data=tag_data)


@app.route('/edit/tags')
def edit_tags():
    tag_data = t.get_all_tags()
    return render_template('edit_tags.html', json_data=tag_data), 200


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


@app.route('/albums/<int:album_id>', methods=['GET'])
def get_album_photos(album_id):
    photo_data = a.get_album_photos(album_id)
    json_data = photo_data
    # print()
    # print(json_data)
    # print()
    return render_template('album.html', json_data=json_data), 200


@app.route('/add/album', methods=['GET', 'POST'])
def create_album():
    if request.method == 'GET':
        return render_template('create_album.html'), 200
    if request.method == 'POST':
        album_title = request.form['title']
        album_description = request.form['description']

        album_id = a.create_album(
            '28035310@N00', album_title, album_description)
        # print('Hello from create_album', album_title,
        #       album_description, album_id)

        album_data = a.get_album(album_id)

        return redirect('/edit/album/{}/photos'.format(album_id)), 302


@app.route('/edit/album/<int:album_id>/photos')
def add_album_photos(album_id):
    # ok it seems to get the album id just fine
    # print('why you no album_id?', album_id)

    album_data = a.get_album(album_id)
    # print()
    # print('album_data ', album_data)
    # print()

    # i need recent photos too
    # args = request.args.to_dict()
    # print('\n', args)
    # args['offset'] = 0
    # photo_data = p.get_photos_in_range(20, int(args['offset']))
    photo_data = p.get_photos_in_range(20, 0)
    photo_data['album_data'] = album_data

    print('Hello from add_album_photos ', photo_data)
    return render_template('add_album_photos.html', json_data=photo_data), 200


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


@app.route('/edit/albums')
def edit_albums():
    """
    Lists all the albums.
    """
    albums_data = a.get_albums()
    print(albums_data)
    return render_template('edit_albums.html', json_data=albums_data), 200


@app.route('/api/albumphotos', methods=['GET', 'POST'])
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

        # else:
        #     args['offset'] = 0
        #     photo_data = a.get_album_photos_in_range(
        #         args['album_id'],
        #         20, int(args['offset']))
        #     json_data = photo_data
        #     return jsonify(json_data)

    if request.method == 'POST':

        print('test', request.get_json())
        data = request.get_json()

        a.remove_photos_from_album(data['albumId'], data['photos'])

        return redirect("/albums/{}".format(data['albumId']), code=302)

        # a.add_photos_to_album(data['albumId'], data['photos'])

        # return redirect("/albums/{}".format(data['albumId']), code=302)


@app.route('/edit/album/<int:album_id>/remove/photos', methods=['GET'])
def remove_album_photos(album_id):
    album_data = a.get_album(album_id)
    photo_data = a.get_album_photos_in_range(album_id)
    photo_data['album_data'] = album_data
    return render_template('remove_album_photos.html', json_data=photo_data), 200


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
