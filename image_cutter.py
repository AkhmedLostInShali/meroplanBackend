from PIL import Image


def squarify(filename):
    im = Image.open(filename)
    x, y = im.size
    if x > y:
        crop_settings = (x // 2 - y // 2, 0, x // 2 + y // 2, y)
    elif y > x:
        crop_settings = (0, y // 2 - x // 2, x, y // 2 + x // 2)
    else:
        return "already was square"
    out = im.crop(crop_settings)
    if out.size[0] > 1080:
        out = out.resize((1080, 1080))
    out.save(filename)
    return "successfully squarified"


def get_central_rect(out_size, filename):
    im = Image.open(filename)
    x, y = im.size
    ex, ey = out_size
    proportion = ex / ey
    if x > y:
        if proportion > 1:
            crop_settings = (0, round(y / 2 - x / proportion / 2), x, round(y / 2 + x / proportion / 2))
        else:
            crop_settings = (round(x / 2 - y / proportion / 2), 0, round(x / 2 + y / proportion / 2), y)
    else:
        if proportion > 1:
            crop_settings = (0, round(y / 2 - x / proportion / 2), x, round(y / 2 + x / proportion / 2))
        else:
            crop_settings = (round(x / 2 - y / proportion / 2), 0, round(x / 2 + y / proportion / 2), y)
    out = im.crop(crop_settings)
    if out.size[0] > ex or out.size[1] > ey:
        out = out.resize(out_size)
    out.save(filename)
    return "successfully cut"


def resize_for_avatar(filename):
    squarify(filename)
    im = Image.open(filename)
    x, y = im.size
    if x > 200:
        out = im.resize((200, 200))
    else:
        return "already was small"
    out.save(filename)
    return "successfully resized"
