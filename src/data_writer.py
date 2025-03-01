import json

class DataWriter:
    
    ### Faltó metodo append

    def __init__(self, file_name, directory):
        self.file_name = file_name
        self.directory = directory
        self.data = []
        self.best = None

    def read_file(self):
        with open(f"./{self.directory + '/' if self.directory else ''}{self.file_name}.json",'r') as file:
            json_data = json.load(file)
            print(json_data)
            self.best = json_data['best']
            self.data = json_data['data']

        if(not self.best): self.set_best()

    def write_file(self):
        with open(f"./{self.directory + '/' if self.directory else ''}{self.file_name}.json",'w') as file:
            data = {'best': self.best, 'data': self.data}
            json.dump(data, file)

    def add_data(self, data):
        self.data.append(data)
        if(not self.best or data['y'] < self.best['y']):
            self.best = data

    def change_file(self, file_name, directory = None, write = True):
        if(write): self.write_file()
        self.file_name = file_name
        self.data  = []
        self.best = None
        if(directory): self.directory = directory

    def set_best(self):
        for d in self.data:
            if(not self.best or d['y'] < self.best['y']):
                self.best = d    
