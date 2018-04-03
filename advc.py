#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

import sys
import configparser
import uuid

obj_types = ["actor", "room", "exit", "thing", "scenery", "vehicle", "text",
	"action", "spell", "topic"]
lock_types = ["?", "!", "+", "-", "@", "^", "#", "~"]

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

def merge_data(config, output):
	for i in config["META"]:
		output["meta"][i] = config["META"][i]
	for i in config["CONFIG"]:
		if i == "max_score":
			output["config"][i] = int(config["CONFIG"][i])
		elif i == "use_score":
			output["config"][i] = config.getboolean("CONFIG", i)
		else:
			output["config"][i] = config["CONFIG"][i]
	flags = ["ending", "dark", "light", "sticky", "visited"]
	for i in config:
		if i in ["DEFAULT", "CONFIG", "META"]:
			continue

		if i not in output["objects"]:
			output["objects"][i] = {}
		inobj = config[i]
		outobj = output["objects"][i]
		for j in inobj:
			if j == "score":
				outobj[j] = int(inobj[j])
			elif j in flags:
				outobj[j] = config.getboolean(i, j)
			else:
				outobj[j] = inobj[j]

def sanity_check(game_data):
	errcount = 0
	db = game_data["objects"]
	linked = set()
	for i in db:
		if "link" in db[i]:
			if db[i]["link"] in db:
				linked.add(db[i]["link"])
			else:
				report_bad_link(i, db[i]["link"])
				errcount += 1
		if "location" in db[i]:
			if db[i]["location"] in db:
				linked.add(db[i]["location"])
			else: # Not really a problem unless it's the hero.
				report_bad_parent(i, db[i]["location"])
				errcount += 1
		if "lock" in db[i]:
			lock = db[i]["lock"][0]
			key = db[i]["lock"][1:]
			if lock not in lock_types:
				report_bad_lock(i, lock)
				errcount += 1
			if key in db:
				linked.add(key)
			else:
				report_bad_key(i, key)
				errcount += 1
	for i in list(db.keys()): # Allow for deleting keys within the loop.
		if "type" not in db[i]:
			db[i]["type"] = "thing"
			report_default_type(i)
		elif db[i]["type"] not in obj_types:
			report_bad_type(i, db[i]["type"])
		elif db[i]["type"] == "room":
			if i not in linked:
				if i == "limbo":
					 # It's probably the unused default.
					del db[i]
				else:
					report_unlinked_room(i)
	return errcount == 0

def report_bad_link(obj_id, link):
	e = "Error: {0} links to non-existent object {1}."
	print(e.format(obj_id, link), file=sys.stderr)

def report_bad_parent(obj_id, link):
	e = "Error: {0} located in non-existent object {1}."
	print(e.format(obj_id, link), file=sys.stderr)

def report_default_type(obj_id):
	e = "Warning: Object {0} has no type, was set to 'thing'."
	print(e.format(obj_id), file=sys.stderr)

def report_bad_type(obj_id, type_id):
	e = "Warning: Object {0} has unknown type {1}."
	print(e.format(obj_id, type_id), file=sys.stderr)

def report_bad_lock(obj_id, lock):
	e = "Error: Bad key type {0} in object {1}."
	print(e.format(lock, obj_id), file=sys.stderr)

def report_bad_key(obj_id, key_id):
	e = "Error: {0} locked to non-existent object {1}."
	print(e.format(obj_id, key_id), file=sys.stderr)

def report_unlinked_room(obj_id):
	e = "Warning: room {0} has no links pointing to it."
	print(e.format(obj_id), file=sys.stderr)

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
		if type(game["config"][i]) == float:
			output["CONFIG"][i] = str(int(game["config"][i]))
		else:
			output["CONFIG"][i] = str(game["config"][i])
	for i in game["objects"]:
		obj = game["objects"][i]
		output[i] = {}
		for j in obj:
			if type(obj[j]) == float:
				output[i][j] = str(int(obj[j]))
			else:
				output[i][j] = str(obj[j])

	return output

if __name__ == "__main__":
	import json
	import argparse

	pargs = argparse.ArgumentParser(prog="advc.py",
		description="Compile Adventure Prompt config to a story file.",
		epilog="Give no input files to get a minimal, default story.")
	pargs.add_argument("-v", "--version", action="version",
		version="%(prog)s version 2018-03-27")
	group = pargs.add_mutually_exclusive_group()
	group.add_argument("-c", "--check", action="store_true",
		help="only perform sanity checks, don't output a story")
	group.add_argument("-s", "--stats", action="store_true",
		help="output statistics instead of a story file")
	group.add_argument("-m", "--merge", action="store_true",
		help="output a merged configuration instead of a story file")
	group.add_argument("-r", "--runner",
		type=argparse.FileType('r'), nargs=1,
		help="bundle a stand-alone game using the given runner")
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

		if not sanity_check(output):
			pass # Should this say something to cap the errors?
		elif args.check:
			pass
		elif args.stats:
			stats = story_stats(output)
			print("Object count by type:")
			for i in stats:
				print("{0:10s}: {1:3d}".format(i, stats[i]))
			print("Total:    {0:5d}".format(sum(stats.values())))
		elif args.merge:
			game2config(output).write(sys.stdout)
		elif args.runner != None:
			tpl = args.runner[0].read(-1)
			args.runner[0].close()
			place = "var game_data = null;"
			text = "var game_data = " + json.dumps(output) + ";"
			print(tpl.replace(place, text), end='')
		else:
			print(json.dumps(output), end='')
	except ValueError as e:
		print("Error in game data: " + str(e), file=sys.stderr)
	except Exception as e:
		print("Error compiling story file: " + str(e), file=sys.stderr)
