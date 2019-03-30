import os

from PIL import Image, ImageOps, ExifTags
# sizes that flickr used:
# 700x467
# 500x334
# 240x160
# 75x75
# 100x66
# 500x334

# # actually useful
# large_square
# 150x150

# original
# 700x467


class PhotoUtil(object):

    @staticmethod
    def orientate_save(path, file_name):
        print('orientate_save called', path, file_name)
        print(os.path.join(path, file_name))
        print()

        try:
            image = Image.open(os.path.join(path, file_name))
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())

            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)

            print(dir(image.save))
            image.save(os.path.join(path, file_name))
            # with open('blah.jpg', 'wb') as fw:
            #     fw.write(image.tobytes())

        except Exception as error:
            print('problems ', error)

    @staticmethod
    def resize_photo(infile, outfile, base_size):
        """
        Preserves ratio, working for 700x467 and 467x700

        It does this by determining what percentage 300 pixels is of the original width
        """
        # i need some way to check for portraits and switch this
        basewidth = base_size
        img = Image.open(infile)

        current_width = img.size[0]
        current_height = img.size[1]

        if current_height > current_width:
            # what percentage is the new height of the old
            height_percent = (float(img.size[1])/base_size)
            width_size = round(float(img.size[0])/float(height_percent))
            img = img.resize((width_size, basewidth), Image.ANTIALIAS)
        else:
            wpercent = (basewidth/float(img.size[0]))
            hsize = round((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)

        img.save(outfile)

    @staticmethod
    def square_thumbnail(infile, outfile, save_path, base_size=300):
        start_path = os.getcwd()
        os.chdir(save_path)
        print(save_path)
        img = Image.open(infile)
        size = (base_size, base_size)
        thumb = ImageOps.fit(img, size, Image.ANTIALIAS)
        # save current dir
        thumb.save(outfile)
        # back to the start path
        os.chdir(start_path)
        print(os.getcwd())

    # resize_photo('test_landscape.jpg', 'test_landscape_resized.jpg', 700)
    # resize_photo('test_portrait.jpg', 'test_portrait_resized.jpg', 700)

    # square_thumbnail('test_landscape.jpg', 'test_landscape_resized.jpg', 150)
    # square_thumbnail('test_portrait.jpg', 'test_portrait_resized.jpg',
    #                  '/home/a/projects/flask-photo-site/static/images/2018/12/',
    #                  300)


def main():
    PhotoUtil.orientate_save(
        '/home/a/projects/testicles/flask-photo-site/static/images/2018/12/', 'IMG_9810.JPG')


if __name__ == "__main__":
    main()
