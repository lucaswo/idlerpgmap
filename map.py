#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from configparser import ConfigParser
import os,sys,time, csv, operator

scriptpath = os.path.join(os.getcwd(),os.path.dirname(sys.argv[0]));

config = ConfigParser()
config.read(os.path.join(scriptpath,'map.conf'))
path_to_db = os.path.expanduser(config['DEFAULT']['PathToIRPGDB'])
csv.register_dialect('irpg', delimiter='\t', quoting=csv.QUOTE_NONE)

class Map:
    def __init__(self,config):
        self.textEnabled = (config['EnableText'] == '1')
        self.tailEnabled = (config['EnableTail'] == '1')
        self.scale = int(config['ImageScale'])
        self.update = int(config['UpdateEvery'])
        self.path = config['MapPath']
        self.bg_path = os.path.join(scriptpath,config['BackgoundPath'])

        font_path = os.path.join(scriptpath,config['Font'])
        self.font = ImageFont.truetype(font_path, int(config['FontSize']))

        self.pixel_width = int(config['PixelWidth'])
        print("Created map ",self.path)
  
    def playerPixel(self, player):
        return (self.scale*player.x-self.pixel_width,self.scale*player.y-self.pixel_width,
                self.scale*player.x+self.pixel_width,self.scale*player.y+self.pixel_width)

    def render(self):
        try:
            myim = Image.open(str(self.bg_path))
        except (IsADirectoryError, IOError):
            myim = Image.new("RGB", (500*self.scale,500*self.scale), (255,255,255))
        
        draw = ImageDraw.Draw(myim)

        for player in players.values():
            color = (0,0,0)

            if not player.online:
                color = (120,0,0)

            myim.paste(color, self.playerPixel(player))
            description = [player.name, "level: " + player.level]
            y = 0

            if self.textEnabled:
                for line in description:
                    draw.text((player.x*self.scale, player.y*self.scale+y),line, fill=color, font=self.font)
                    y = y + 12

            if self.tailEnabled:
                color = (0,128,0)
                colorInc = int(255/int(config['DEFAULT']['TailHistory']))
                curPos = (player.x*self.scale,player.y*self.scale)
                for p in reversed(player.history):
                    pos = (p[0]*self.scale,p[1]*self.scale)
                    if (max(abs(curPos[0]-pos[0]),abs(curPos[1]-pos[1])) > 
                        int(config['DEFAULT']['InternalInterval'])*self.update*2):
                        continue
                    draw.line([curPos,pos],fill=color,width=2)
                    curPos = pos
                    color = (color[0]+colorInc,color[1]+int(colorInc/2),color[2]+colorInc)
            
            myim.save(os.path.expanduser(self.path))

class Player:
    
    def __init__(self,data):
        self.name = data["# username"]
        self.history = []
        self.processData(data)

    def processData(self,data):
        assert(self.name== data["# username"])

        self.x = int(data["x pos"])
        self.y = int(data["y pos"])

        self.weapon = data["weapon"]
        self.level = data["level"]
        self.online = data["online"] != '0'
        self.history += [(self.x,self.y)]

players = dict()
maps = list()
for s in config.sections():
    maps.append(Map(config[s]))

iteration = 0
while True:
    csvfile = open(path_to_db,'r')
    reader = csv.DictReader(csvfile, dialect='irpg')

    for p in reader:
        try:
            players[p["# username"]].processData(p)
        except:
            players[p["# username"]] = Player(p)

    for m in maps:
        if iteration % m.update == 0:
            m.render()

    iteration += 1
    time.sleep(int(config['DEFAULT']['InternalInterval']))

