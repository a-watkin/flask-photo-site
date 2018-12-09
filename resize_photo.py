import os

from PIL import Image, ImageOps
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


def square_thumbnail(infile, outfile, base_size):
    img = Image.open(infile)
    size = (base_size, base_size)
    thumb = ImageOps.fit(img, size, Image.ANTIALIAS)
    # save current dir
    start_path = os.getcwd()
    save_path = '/home/a/projects/flask-photo-site/static/images/'
    os.chdir(save_path)
    thumb.save(outfile)
    # back to the start path
    os.chdir(start_path)
    print(os.getcwd())


# resize_photo('test_landscape.jpg', 'test_landscape_resized.jpg', 700)
# resize_photo('test_portrait.jpg', 'test_portrait_resized.jpg', 700)

# square_thumbnail('test_landscape.jpg', 'test_landscape_resized.jpg', 150)
square_thumbnail('test_portrait.jpg', 'test_portrait_resized.jpg', 300)
