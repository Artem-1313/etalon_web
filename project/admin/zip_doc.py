import zipfile, os


class zip_doc():
    def __init__(self, file):
        self.file_ = file


    def rename_to_zip(self):
        f = self.file_.split('.')
        f[1] = 'zip'
        zip_file = '.'.join(f)
        return zip_file




