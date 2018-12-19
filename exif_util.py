import os
import sys
import json


from PIL import Image, ImageOps, ExifTags
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
"""
sizes that flickr used:
700x467
500x334
240x160
75x75
100x66
500x334

# actually useful
large_square
150x150

original
700x467
"""


class ExifUtil(object):

    def __init__(self):
        pass

    def rotate_orientation(path, fileName):

        try:
            image = Image.open(os.path.join(path, fileName))
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

            # image.thumbnail((THUMB_WIDTH, THUMB_HIGHT), Image.ANTIALIAS)
            image.save(os.path.join(path, 'fuck.jpg'))

        except Exception as error:
            print('problems ', error)

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

        print(dir(img), '\n', img.height, img.width)

        for orientation in ExifTags.TAGS.keys():
            # print(ExifTags.TAGS[orientation])
            # print()
            if ExifTags.TAGS[orientation] == 'Orientation':
                exif = dict(img._getexif().items())
                print('this will not print',
                      ExifTags.TAGS[orientation])
                print()
                print(exif[orientation])

                # print('width', current_width, 'height', current_height)

                # if current_height > current_width:
                #     # what percentage is the new height of the old
                #     height_percent = (float(img.size[1])/base_size)
                #     width_size = round(float(img.size[0])/float(height_percent))
                #     img = img.resize((width_size, basewidth), Image.ANTIALIAS)
                # else:
                #     wpercent = (basewidth/float(img.size[0]))
                #     hsize = round((float(img.size[1])*float(wpercent)))
                #     img = img.resize((basewidth, hsize), Image.ANTIALIAS)

                # img.save(outfile)

    def square_thumbnail(infile, outfile, base_size):
        img = Image.open(infile)
        size = (base_size, base_size)
        thumb = ImageOps.fit(img, size, Image.ANTIALIAS)
        thumb.save(outfile)

    def test_exifread(fn):
        import exifread
        print('\n<< Test of exifread >>\n')

        rtn_dict = {}

        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k in sorted(exif.items()):
            print(k)
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                # print('%s = %s' % (k, exif[k]))
                print('%s = %s' % (TAGS.get(k), v))
                rtn_dict[TAGS.get(k)] = v

    def read_exif(infile):
        img = Image.open(infile)
        # print(dir(img))
        # print(img._getexif())
        rtn_dict = {}

        for (k, v) in img._getexif().items():
            # print('%s = %s' % (TAGS.get(k), v))
            data = v
            # remove bytes
            try:
                data = v.decode()
                # print('yes?', data)
            except AttributeError:
                print('nope')

                # print(TAGS.get(k))
            rtn_dict[TAGS.get(k)] = data

        return rtn_dict

    # resize_photo('test_landscape.jpg', 'test_landscape_resized.jpg', 700)
    # resize_photo('test_portrait.jpg', 'test_portrait_resized.jpg', 700)

    # square_thumbnail('test_landscape.jpg', 'test_landscape_resized.jpg', 300)
    # square_thumbnail('test_portrait.jpg', 'test_portrait_resized.jpg', 300)

    # read_exif('test_portrait.jpg')

    def get_datetime_taken(fn):
        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k in sorted(exif.keys()):
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                # print(k)
                # print('%s = %s' % (k, exif[k]))

                if k == 'Image DateTime':
                    return exif[k]


def main():
    # ExifUtil.resize_photo('problem_portrait.JPG', 'test.jpg', 700)

    ExifUtil.rotate_orientation(os.getcwd(), 'problem_portrait.JPG')

    # print(ExifUtil.test_exifread('test_portrait.jpg'))
    # test = json.dumps(ExifUtil.read_exif('test_portrait.jpg'),
    #                   ensure_ascii=False).encode('utf-8')
    # test = ExifUtil.test_exifread('test_portrait.jpg')

    # test = ExifUtil.read_exif('test_portrait.jpg')
    # print(json.dumps(test))
    # print(ExifUtil.get_datetime_taken('test_portrait.jpg'))
    pass


if __name__ == "__main__":
    main()

# print(get_datetime_taken('test_portrait.jpg'))
