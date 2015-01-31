#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from configparser import ConfigParser
import os,sys

scriptpath = os.path.join(os.getcwd(),os.path.dirname(sys.argv[0]));

config = ConfigParser()
config.read(os.path.join(scriptpath,'map.conf'))
path_to_db = os.path.expanduser(config['DEFAULT']['PathToIRPGDB'])
pixel_width = int(config['DEFAULT']['PixelWidth'])
font_path = os.path.join(scriptpath,config['DEFAULT']['Font'])

def read_data(path):

	data = []
	fd = open(path, 'r')
	for line in fd:
		data.append(line.split('\t'))

	#print(xPosition , " " , yPosition)
	# del data[0]
	#print(data[0][xPosition], " " , data[0][yPosition])

	return data


def create_image(data):
	global pixel_width

	myim = Image.new("RGB", (1000,1000), (255,255,255))
	draw = ImageDraw.Draw(myim)
	font = ImageFont.truetype(font_path, int(config['DEFAULT']['FontSize']))

	xPosition = data[0].index("x pos")
	yPosition = data[0].index("y pos")
	player_name = data[0].index("# username")
	player_weapon = data[0].index("weapon")
	online = data[0].index("online")
	player_level = data[0].index("level")

	for p in data[1:]:
		true_X = 2*int(p[xPosition])
		true_Y = 2*int(p[yPosition])
		name = str(p[player_name])
		weapon = str(p[player_weapon])
		level = str(p[player_level])
		color = (0,0,0)

		if p[online] == '0':
			color = (120,0,0)

		myim.paste(color, (true_X-pixel_width,true_Y-pixel_width,true_X+pixel_width,true_Y+pixel_width))
		if true_X > 980:
			true_X = true_X-20
		else:
			true_X = true_X+5

		if true_Y > 965:
			true_Y = true_Y-35
		else:
			true_Y = true_Y+5

		description = [name, "level: " + level]
		y = 0

		for line in description:
			draw.text((true_X, true_Y+y), line, fill=color, font=font)
			y = y + 12

	#myim.show()
	myim.save(os.path.join(os.path.expanduser(config['DEFAULT']['MapPath']),"map.png"))

read_data = read_data(path_to_db)
create_image(read_data)
