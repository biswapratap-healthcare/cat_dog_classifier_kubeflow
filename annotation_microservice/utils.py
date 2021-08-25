import os
from PIL import Image


def get_image(d, f):
    f_split = f.split('.')
    new_name = '_'.join(f_split[:-1]) + '_converted.' + f_split[-1]
    image = os.path.join(d, f)
    converted_image = os.path.join(d, new_name)
    im = Image.open(image).convert('LA')
    # im.show()
    new_size = (512, 512)
    im = im.resize(new_size)
    # im.show()
    im = im.convert('RGB')
    # im.show()
    im.save(converted_image)
    return converted_image
