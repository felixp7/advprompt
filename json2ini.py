#!/usr/bin/env python3
# coding=utf-8

from __future__ import print_function

import sys
import json
import configparser

if len(sys.argv) < 2:
	print("Usage: json2ini.py <input file>")
	exit()

try:
	with open(sys.argv[1], "r") as f:
		game = json.load(f)
		# TO DO: sanity checks
except Exception as e:
	print("Couldn't read story file: " + str(e))

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

output.write(sys.stdout)
