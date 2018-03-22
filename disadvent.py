#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

import configparser

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
	import sys
	import json
	import argparse

	pargs = argparse.ArgumentParser(prog="disadvent.py",
		description="Decompile Adventure Prompt story files.")
	pargs.add_argument("-s", "--stats", action="store_true",
		help="output statistics instead of decompiling")
	pargs.add_argument("story", type=argparse.FileType('r'), nargs=1,
		help="story file to decompile")
	args = pargs.parse_args()

	try:
		game_data = json.load(args.story[0])
		args.story[0].close()

		# TO DO: sanity checks?
		if args.stats:
			stats = story_stats(game_data)
			print("Object count by type:")
			for i in stats:
				print("{0:10s}: {1:3d}".format(i, stats[i]))
			print("Total:    {0:5d}".format(sum(stats.values())))
		else:
			output = game2config(game_data)
			output.write(sys.stdout)
	except Exception as e:
		print("Couldn't read story file: " + str(e), sys.stderr)
