#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

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

def merge_data(config, output):
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

def story_stats(game_data):
	type_count = {}
	for i in game_data["objects"]:
		obj = game_data["objects"][i]
		t = obj["type"]
		if t in type_count:
			type_count[t] += 1
		else:
			type_count[t] = 1
	return type_count

def game2config(game):
	output = configparser.ConfigParser()

	output["META"] = {}
	for i in game["meta"]:
		output["META"][i] = str(game["meta"][i])
	output["CONFIG"] = {}
	for i in game["config"]:
		output["CONFIG"][i] = str(game["config"][i])
	for i in game["objects"]:
		obj = game["objects"][i]
		output[i] = {}
		for j in obj:
			output[i][j] = str(obj[j])

	return output

if __name__ == "__main__":
	import sys
	import json
	import argparse

	pargs = argparse.ArgumentParser(prog="advc.py",
		description="Compile Adventure Prompt config to a story file.")
	group = pargs.add_mutually_exclusive_group()
	group.add_argument("-s", "--stats", action="store_true",
		help="output statistics instead of a story file")
	group.add_argument("-m", "--merge", action="store_true",
		help="output a merged configuration instead of a story file")
	pargs.add_argument("source", type=argparse.FileType('r'), nargs='*',
		help="configuration files to use as input")
	args = pargs.parse_args()

	output = new_game()
	try:
		for i in args.source:
			config = configparser.ConfigParser()
			config.read_file(i)
			i.close()
			merge_data(config, output)

		# TO DO: sanity checks
		if args.stats:
			stats = story_stats(output)
			print("Object count by type:")
			for i in stats:
				print("{0:10s}: {1:3d}".format(i, stats[i]))
			print("Total:    {0:5d}".format(sum(stats.values())))
		elif args.merge:
			game2config(output).write(sys.stdout)
		else:
			print(json.dumps(output), end='')
	except Exception as e:
		print("Couldn't read configuration file: " + str(e))
