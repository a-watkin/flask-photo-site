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

    @staticmethod
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

    @staticmethod
    def read_exif(infile):
        img = Image.open(infile)
        print(dir(img), img.format)
        print(img._getexif().items())
        rtn_dict = {}

        for (k, v) in img._getexif().items():
            # print('%s = %s' % (TAGS.get(k), v))
            data = v
            # remove bytes
            try:
                data = v.decode()
                # print('yes?', data)
            except AttributeError as e:
                continue
                # print('AttributeError', e)

                # print(TAGS.get(k))
            rtn_dict[TAGS.get(k)] = data

        return rtn_dict

    @staticmethod
    def get_datetime_taken(fn):
        print('hello from get_datetime_taken', fn)
        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k in sorted(exif.keys()):
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                # print(k)
                # print('%s = %s' % (k, exif[k]))

                if k == 'Image DateTime':
                    return exif[k]


def main():
    # print(ExifUtil.read_exif('IMG_9017.JPG'))

    # print(ExifUtil.test_exifread('IMG_9017.JPG'))

    # ExifUtil.resize_photo('problem_portrait.JPG', 'test.jpg', 700)

    # ExifUtil.rotate_orientation(os.getcwd(), 'problem_portrait.JPG')

    # print(ExifUtil.test_exifread('test_portrait.jpg'))
    # test = json.dumps(ExifUtil.read_exif('test_portrait.jpg'),
    #                   ensure_ascii=False).encode('utf-8')
    # test = ExifUtil.test_exifread('test_portrait.jpg')

    # test = ExifUtil.read_exif('test_portrait.jpg')
    # print(test)
    # print(json.dumps(test))
    # print(ExifUtil.get_datetime_taken('test_portrait.jpg'))
    pass


if __name__ == "__main__":
    main()

# print(get_datetime_taken('test_portrait.jpg'))
