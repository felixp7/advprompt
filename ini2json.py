#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

import sys
import json
import configparser
import uuid

def new_meta():
	return {
		"title": "An Interactive Fiction",
		"author": "Anonymous",
		"ifid": str(uuid.uuid4())
	}

def new_config():
	return {"banner": "", "max_score": 0, "use_score": True}

def new_room(name):
	return {
		"type": "room",
		"name": name,
		"description": ""
	}

def new_actor(name, loc=None):
	return {
		"type": "actor",
		"name": name,
		"description": "As good-looking as ever.",
		"location": loc
	}

def new_game():
	game = {
		"meta": new_meta(),
		"objects": {
			"limbo": new_room("Limbo"),
			"hero": new_actor("You", "limbo")
		},
		"config": new_config()
	}
	game["objects"]["limbo"]["description"] = "You are in limbo."
	return game

def parse_value(text):
	low = text.lower()
	if low in ["true", "yes", "on"]:
		return True
	elif low in ["false", "no", "off"]:
		return False
	else:
		try:
			return int(text)
		except ValueError:
			return text
		except OverflowError:
			return text

def config2game(config):
	output = new_game()

	for i in config["META"]:
		output["meta"][i] = config["META"][i]
	for i in config["CONFIG"]:
		output["config"][i] = parse_value(config["CONFIG"][i])
	for i in config:
		if i in ["DEFAULT", "CONFIG", "META"]:
			continue

		if i not in output["objects"]:
			output["objects"][i] = {}
		obj = config[i]
		for j in obj:
			output["objects"][i][j] = parse_value(obj[j])
	
	return output

if len(sys.argv) < 2:
	print("Usage: ini2json.py <input file>")
	exit()

config = configparser.ConfigParser()

try:
	with open(sys.argv[1], "r") as f:
		config.read_file(f)
		# TO DO: sanity checks
except Exception as e:
	print("Couldn't read INI file: " + str(e))

output = config2game(config)
print(json.dumps(output))
