import glob
import os
import codecs


class Corpus(object):
    def __init__(self, path, file_extension, encoding=None):
        self.path = path
        self.file_extension = '*.' + file_extension
        self.encoding = encoding
        self.file_list = []
        self.texts = []
        self.get_files()
        self.get_texts()

    def get_files(self):
        for file in glob.glob(self.path + self.file_extension):
            self.file_list.append(file)

    def get_texts(self):
        for file in self.file_list:
            with codecs.open(file,  encoding=self.encoding) as f:
                self.texts.append(f.read())
