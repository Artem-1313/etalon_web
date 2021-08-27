from PIL import Image
import random, string
from flask import flash
import os


def allowed_files(filename):
    if filename.rsplit('.', 1)[1].lower() in {'png', 'jpeg', 'jpg'}:
        return True
    else:
        return False


def rename_file(file_name):
    extens_file = file_name.rsplit('.', 1)[1]
    new_file_name = str(''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=7))) + '.' + extens_file
    return new_file_name


class resize_img:

    def __init__(self, img, new_w, new_h):
        self.img = img
        self.new_w = new_w
        self.new_h = new_h

    def check_img_size(self):
        with Image.open(self.img) as image:
            width, height = image.size
            if width < self.new_w or height < self.new_h:
                return False
            else:
                return True

    def resize(self):
        try:
         with Image.open(self.img) as image:
            new_size = (self.new_w, self.new_h)
            res_im = image.resize(new_size)
            res_im.save(self.img, format="png")
        except:
            print("saaaaa")

