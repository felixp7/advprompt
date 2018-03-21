#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

import configparser

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

	pargs = argparse.ArgumentParser(
		description='disadvent: decompile Adventure Prompt story files')
	pargs.add_argument("-s", "--stats", action="store_true",
		help="output stats about the game instead of decompiling")
	pargs.add_argument("source", type=argparse.FileType('r'), nargs=1,
		help="story file to read the data from")
	args = pargs.parse_args()

	try:
		game_data = json.load(args.source[0])
		args.source[0].close()

		# TO DO: sanity checks?
		if args.stats:
			obj_total = 0
			type_count = {}
			for i in game_data["objects"]:
				obj = game_data["objects"][i]
				t = obj["type"]
				if t in type_count:
					type_count[t] += 1
				else:
					type_count[t] = 1
				obj_total += 1
			print("Object count by type:")
			for i in type_count:
				print("{0:10s}: {1:3d}".format(
					i, type_count[i]))
			print("Total:    {0:5d}".format(obj_total))
		else:
			output = game2config(game_data)
			output.write(sys.stdout)
	except Exception as e:
		print("Couldn't read story file: " + str(e), sys.stderr)
