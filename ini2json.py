#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

import sys
import json
import configparser

def parse_value(text):
	low = text.lower()
	if low in ["true", "yes", "on"]:
		return True
	elif low in ["false", "no", "off"]:
		return False
	else:
		try:
			return float(text)
		except ValueError:
			return text
		except OverflowError:
			return text

if len(sys.argv) < 2:
	print("Usage: ini2json.py <input file>")
	exit()

game = configparser.ConfigParser()

try:
	with open(sys.argv[1], "r") as f:
		game.read_file(f)
		# TO DO: sanity checks
except Exception as e:
	print("Couldn't read INI file: " + str(e))

output = {}

output["meta"] = {}
for i in game["META"]:
	output["meta"][i] = game["META"][i]
output["config"] = {}
for i in game["CONFIG"]:
	output["config"][i] = parse_value(game["CONFIG"][i])
output["objects"] = {}
for i in game:
	if i in ["DEFAULT", "CONFIG", "META"]:
		continue
	else:
		output["objects"][i] = {}
		obj = game[i]
		for j in obj:
			output["objects"][i][j] = parse_value(obj[j])

print(json.dumps(output))
