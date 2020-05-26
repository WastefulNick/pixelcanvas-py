from pil import Image
import requests
from time import sleep
import json

colors = ((255, 255, 255), #	white
        (228, 228, 228), #		lightgray
        (136, 136, 136), #		gray
        (34, 34, 34), #			black
        (255, 167, 209), #		pink
        (229, 0, 0), #			red
        (229, 149, 0), #		orange
        (160, 106, 66), #		brown
        (229, 217, 0), #		yellow
        (148, 224, 68), #		lightgreen
        (2, 190, 1),#			green
        (0, 211, 221), #		turqoise
        (0, 131, 199), #		ligthblue
        (0, 0, 234), #			darkblue
        (207, 110, 228), #		darkpink
        (130, 0, 128)) #		purple

def nearest_color(query):
        return min(colors, key = lambda subject: sum((s - q) ** 2 for s, q in zip(subject, query)))

class PixelCanvas:
    def __init__(self, img, coors, fingerprint, size):
        self.img = img
        self.c = coors
        self.size = size
        self.fingerprint = fingerprint

        with open('state.json') as f:
            self.json_f = json.load(f)
        
        self.curr_pixel = self.json_f['curr_pixel']

    def place(self, color):
        color = colors.index(color)
        wasabi = self.c[0] + self.c[1] + 2342

        url = 'https://europe-west1-pixelcanvasv2.cloudfunctions.net/pixel'
        headers = {
            'Content-type': 'application/json',
            'DNT': '1',
            'Origin': 'https://pixelcanvas.io',
            'Referer' : f'https://pixelcanvas.io/@{self.c[0]},{self.c[1]}',
            'Sec-Fetch-Mode' : 'cors',
            'Accept-Encoding': 'gzip',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.57388'
        }
        data = f'{{"x":{self.c[0]},"y":{self.c[1]},"color":{color},"fingerprint":"{self.fingerprint}","token":null,"wasabi":{wasabi}}}'

        r = requests.post(url=url, headers=headers, data=data)
        try:
            response = r.json()
            return response['waitSeconds'], r.status_code
        except:
            return 0, -1

    def write_state(self, i, j):
        self.json_f['coors'] = ' '.join(str(x) for x in self.c)
        self.json_f['curr_pixel'] = self.curr_pixel
        self.json_f['i'] = i
        self.json_f['j'] = j
        self.curr_pixel += 1

        with open('state.json', 'w') as f:
            json.dump(self.json_f, f)

    def start(self):
        pixels = self.img.load()
        original_y = int(self.json_f['starting_coor'].split(' ')[1])

        i = self.json_f['i']
        j = self.json_f['j']

        while i <= self.size[0] - 1:
            while j <= self.size[1] - 1:
                wait_seconds, status_code = self.place(pixels[i, j])
                
                if status_code == 200:
                    print(f'[o] {self.c[0]} {self.c[1]} - {wait_seconds}s')

                    if self.c[1] != (original_y + self.size[1] - 1):
                        self.c[1] += 1
                        j += 1
                    else:
                        self.c[1] = original_y
                        self.c[0] += 1
                        j += 1

                    self.write_state(i, j)
                elif status_code != -1:
                    print(f'[x] {self.c[0]} {self.c[1]} - {wait_seconds}s')

                try:
                    sleep(wait_seconds)
                except:
                    sleep(1)
            i += 1
            j = 0
        print('Done')

        self.json_f['starting_coor'] = None
        self.json_f['coors'] = None
        self.json_f['size'] = None
        self.json_f['curr_pixel'] = 0
        self.json_f['i'] = 0
        self.json_f['j'] = 0

        with open('state.json', 'w') as f:
            json.dump(self.json_f, f)
        return
                
def main():
    with open('state.json') as f:
        json_f = json.load(f)

    if json_f['coors'] == None:
        img_name = input('Image name: ')
        
        coors = input('Coordinates ("x y"): ')
        size = input('Size ("x y"): ')

        json_f['starting_coor'] = coors
        json_f['size'] = size

        with open('state.json', 'w') as f:
            json.dump(json_f, f)

        fingerprint = input('Fingerprint: ')

        coors = list(map(int, coors.split()))
        size = list(map(int, size.split()))

        img = Image.open(img_name).resize((size[0], size[1]))

        pixels = img.load()
        for i in range(img.size[0]):
            for j in range(img.size[1]):
                pixels[i, j] = nearest_color(pixels[i, j])

        img.save('out.png') 
        img = Image.open('out.png')
        
        PixelCanvas(img, coors, fingerprint, size).start()
    else:
        coors = list(map(int, json_f['coors'].split()))
        size = list(map(int, json_f['size'].split()))

        img = Image.open('out.png')

        fingerprint = input('Fingerprint: ')

        PixelCanvas(img, coors, fingerprint, size).start()

if __name__ == "__main__":
    main()