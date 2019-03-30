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

# original - this is actually a resize of the original image
# 700x467


class PhotoUtil(object):

    @staticmethod
    def orientate_save(path, file_name):
        """
        This is supposed to save a photo in the correct orientation.

        I'm not convinced it actually works.
        """
        # Catch NoneType error when a photo does not contain any EXIF data.
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

            image.save(os.path.join(path, file_name))

        except Exception as error:
            print('Orientate_save problem ', error)

    @staticmethod
    def resize_photo(infile, outfile, base_size):
        """
        Preserves ratio, working for 700x467 and 467x700

        It does this by determining what percentage 300 pixels is of the original width
        """
        basewidth = base_size
        img = Image.open(infile)

        current_width = img.size[0]
        current_height = img.size[1]

        if current_height > current_width:
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
        # Save current dir.
        start_path = os.getcwd()
        os.chdir(save_path)
        img = Image.open(infile)
        size = (base_size, base_size)
        thumb = ImageOps.fit(img, size, Image.ANTIALIAS)
        thumb.save(outfile)
        # Switch back to start path.
        os.chdir(start_path)


if __name__ == "__main__":
    PhotoUtil.orientate_save(
        '/home/a/projects/testicles/flask-photo-site/static/images/2018/12/', 'IMG_9810.JPG')
