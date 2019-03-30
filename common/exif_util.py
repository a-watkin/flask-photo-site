import os
import sys
import json


from PIL import Image, ImageOps, ExifTags
from PIL import Image
from PIL.ExifTags import TAGS
import exifread
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


class ExifUtil(object):

    @staticmethod
    def test_exifread(fn):
        """
        Gets exif data, there may be a problem with this.
        """
        # print('\n<< Test of exifread >>\n')

        rtn_dict = {}

        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k, v in sorted(exif.items()):
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                # print('%s = %s' % (k, exif[k]))
                # print('%s = %s' % (TAGS.get(k), v))
                # rtn_dict[TAGS.get(k)] = v
                rtn_dict[str(k)] = str(exif[k])

        return json.dumps(rtn_dict)

    @staticmethod
    def get_datetime_taken(fn):
        print('hello from get_datetime_taken', fn)
        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k in sorted(exif.keys()):
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                # print(k)
                # print('\n')
                # print('%s = %s' % (k, exif[k]))
                if '%s' % k == 'EXIF DateTimeOriginal':
                    # print('%s' % exif[k])
                    return '%s' % exif[k]
                # print()

                # if k == 'Image DateTime':
                #     print('datetime taken, ', exif[k])
                #     return exif[k]


def main():
    pass
    # test = ExifUtil.read_exif('test_portrait.jpg')
    # print(json.dumps(test))
    # print(ExifUtil.read_exif('test_portrait.jpg'))
    # print(ExifUtil.read_exif('IMG_9811.JPG'))

    # print(ExifUtil.test_exifread('test.jpg'))
    # exif_data = ExifUtil.test_exifread('IMG_9811.JPG')
    # print(
    #     '\n',
    #     json.dumps(exif_data)
    # )


if __name__ == "__main__":
    main()
