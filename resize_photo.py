from PIL import Image, ImageOps
"""
700x467
500x334
240x160
75x75
100x66
500x334

large_square
150x150

original
700x467
"""


def resize_photo(infile, outfile, base_size):
    """
    Preserves ratio
    """
    # i need some way to check for portraits and switch this
    basewidth = base_size
    img = Image.open(infile)
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(outfile)


def square_thumbnail(infile, outfile, base_size):
    img = Image.open(infile)
    size = (base_size, base_size)
    thumb = ImageOps.fit(img, size, Image.ANTIALIAS)
    thumb.save(outfile)


resize_photo('test_landscape.jpg', 'test_landscape_resized.jpg', 700)
resize_photo('test_portrait.jpg', 'test_portrait_resized.jpg', 700)
