

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')

        # No files selected
        if 'file' not in request.files:
            # flash('No file selected')
            return redirect(request.url)

        # Single or multiple files selected
        elif len(files) >= 1:
            created = datetime.datetime.now()
            print('MULTIPLE FILES')
            for file in files:
                photo_id = str(int(uuid.uuid4()))[0:10]
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
                    # this guards against multiple files having the same name
                    # a problem here is that it also allows the same file to be uploaded
                    # multiple times
                    # identifier = str(uuid.uuid1()).split('-')[0]
                    if filename in file_in_dir:
                        temp = filename.split('.')

                        temp[0] = temp[0] + "_" + photo_id + '_o'

                        filename = '.'.join(temp)

                    # save the file in the path
                    file.save(
                        os.path.join(
                            save_directory, filename))

                    print('here', save_directory, filename)

                    date_taken = ExifUtil.get_datetime_taken(
                        os.path.join(save_directory, filename))

                    try:
                        exif_data = ExifUtil.test_exifread(
                            os.path.join(save_directory, filename))
                    except Exception as e:
                        exif_data = None
                        print('problem reading exif data', e)

                    PhotoUtil.orientate_save(save_directory, filename)
                    # save path to the photo
                    file_path = save_directory + '/' + filename

                    # print(file_path)

                    # add idenfitying name to file
                    thumbnail_name = filename.split('.')
                    thumbnail_name[0] = thumbnail_name[0] + '_lg_sqaure'

                    thumbnail_filename = '.'.join(thumbnail_name)

                    # construct path to save thumbnail file to
                    save_path = save_directory + '/'
                    # print(os.listdir(save_path), filename,
                    #       filename in os.listdir(save_path), '\n',
                    #       save_path)

                    print()
                    print(save_path)
                    print(thumbnail_filename)
                    print()

                    PhotoUtil.square_thumbnail(
                        filename, thumbnail_filename, save_path)

                    # path for the database
                    original_path = '/static/images/{}/{}/{}'.format(
                        created.year, created.month, filename)
                    large_square_path = '/static/images/{}/{}/{}'.format(
                        created.year, created.month, thumbnail_filename)

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

            return redirect(url_for('uploaded_photos_page'), code=302)

    # Get request and initial loading of the upload page
    return render_template('upload.html'), 200
