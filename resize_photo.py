from PIL import Image, ImageOps


def preserve_ratio(filename):
    # width that the image is resized to
    basewidth = 700

    img = Image.open('IMG_4032.JPG')

    wpercent = (basewidth/float(img.size[0]))

    hsize = int((float(img.size[1])*float(wpercent)))

    img = img.resize((basewidth, hsize), Image.ANTIALIAS)

    img.save('sompic3.jpg')


def square_thumbnail(filename, size):
    img = Image.open('IMG_4164.JPG')
    # print(img.size)
    # # width, height
    # test = img.resize((300, 300), Image.ANTIALIAS)

    # test.save('test2.jpg')
    size = (300, 300)
    thumb = ImageOps.fit(img, size, Image.ANTIALIAS)
    thumb.save('test.jpg')
