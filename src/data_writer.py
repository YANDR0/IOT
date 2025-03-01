import json

class DataWriter:
    
    def __init__(self, file_name, directory):
        self.file_name = file_name
        self.directory = directory
        self.data = []
        self.best = None

    def read_file(self):
        with open(f"./{self.directory}/{self.directory}.json",'r') as file:
            json_data = json.load(file)
            self.best = json_data.best
            self.data = json_data.data

    def write_file(self):
        with open(f"./{self.directory}/{self.directory}.json",'w') as file:
            data = {'best': self.best, 'data': self.data}
            json.dump(data, file)

    def add_data(self, data):
        self.data.append(data)

    def set_best(self):
        for d in self.data:
            if(not self.best or d['y'] < self.best['y']):
                self.best = d

    def change_parameters(self, file_name):
        self.write_file()
        self.file_name = file_name

    
