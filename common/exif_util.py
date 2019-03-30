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
        rtn_dict = {}

        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k, v in sorted(exif.items()):
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                rtn_dict[str(k)] = str(exif[k])

        return json.dumps(rtn_dict)

    @staticmethod
    def get_datetime_taken(fn):
        with open(fn, 'rb') as f:
            exif = exifread.process_file(f)

        for k in sorted(exif.keys()):
            if k not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                if '%s' % k == 'EXIF DateTimeOriginal':
                    return '%s' % exif[k]


if __name__ == "__main__":
    pass
