import os
import re
import shutil


class del_img:

    def __init__(self, image, id_article):
        self.image = image
        self.id = id_article

    def del_i(self):
        # ищем все картинки с тэгом в <img src= посте
        #result = re.findall(r'<img src="([^"]+)"', self.image)
        result = re.findall(r'<img src="\/static([^"]+)"', self.image)

        if result:
            # получаем с <img src= картинку
            reg = [i.split("/")[-1] for i in result]

           # path = os.path.join(os.getcwd(), '/'.join(result[0].split("/")[1:-1]))

            #path = '/'.join(result[0].split("/")[1:-1])
            path = os.path.join("static", "images", str(self.id))
            print(self.id)

            files = [i for i in os.listdir(path)]
            reg = set(reg)
            files = set(files)
            if not files.issubset(reg):
                [os.remove(os.path.join(path, i)) for i in list(files.symmetric_difference(reg))]
        else:
            if os.path.isdir(os.path.join("static", "images", str(self.id))):
                shutil.rmtree(os.path.join("static", "images", str(self.id)))

