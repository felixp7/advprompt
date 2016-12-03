#!/usr/bin/env python3
# coding=utf-8

"""Adventure Prompt -- author interactive fiction interactively."""

from __future__ import division
from __future__ import print_function

try:
	import readline
except ImportError as e:
	print("(Command line editing is unavailable.)\n")

import cmd
import shlex
import json
import uuid

app_banner = """
Welcome to Adventure Prompt, a system for authoring interactive fiction
interactively. Type HELP or ? to see a list of commands.
"""

help_text = {}

help_text["basics"] = """
Adventure Prompt is a system for authoring interactive fiction interactively,
the same way online building works in a MUSH or MUCK. Walking simulators, or
even simple room escape games, can be created without any scripting, unless
you count the command language itself.

To begin with, type `look` (without the quotes) at the command prompt. Any
game made with Adventure Prompt must contain at least two objects: an actor
with id `hero`, and at least one room for the hero to be in (see: objects).
You can make more objects with the build commands: `dig`, `open`, `create`;
inspect their properties with `look`, `examine` or `say`; and change these
properties with `set` or one of `name`, `desc`, `succ`, `fail`, `drop`,
`lock`, `unlock`. Other commands allow you to save and restore a story file,
clone and recycle objects, move your viewpoint around and so on.

When loaded in an interpreter, the story starts wherever the hero is located
initially; the author's viewpoint is only a convenience for building.
"""

help_text["shortcuts"] = """
The command line supports shortcuts to the most common commands:

- `l` for look;
- `ex` for examine;
- `tel` for teleport.

In addition, typing the name of an object in the current room by itself
will move the author's viewpoint to the exit's destination.
"""

help_text["objects"] = """
Objects are the basic building block of Adventure Prompt story files. Each
story file needs to contain at least two objects in order to be valid:

1. an actor with the ID `hero`, to serve as the player's avatar;
2. a room for the hero to be in.

Each object is recognized by a unique identifier (see: identifiers) and has
at least two properties: a type and a name. The name is what the player sees.
The type determines how the object can be interacted with, and the meaning
of other properties. See: types.
"""

help_text["types"] = """
The editor directly supports four main object types:

- `room` objects contain everything else in the story, even indirectly;
  if an object's location (see: properties) can't be traced back to a room,
  it's out of play and inaccessible;
- `exit` objects connect rooms together into a navigable grid;
- `actor`: these are the characters of the story -- only the hero for now;
- `thing` denotes objects the player can pick up and carry around.

To get other types, first `create` a thing, then `set` its type to one of:

- `scenery` objects are part of the landscape and not meant to be picked up.
  Additionally, if linked to somewhere else they double as an exit;
- `vehicle`: the hero can board such an object if they pass the lock. Once
  in a vehicle, all exits treat it as the actor for traversal purposes.
"""

help_text["identifiers"] = """
Identifiers, IDs for short, are character strings by which objects are
stored in the story file. You should keep identifiers short and easy to
type; also, an ID shouldn't start with a "!" (exclamation point), "+"
(plus sign) or "-" (minus sign). For exits, the recommended ID scheme is:

	<room id>-<direction>
	
e.g. `foyer-w` or `bar-n`. Future versions may introduce other restrictions,
such as forcing all IDs to lowercase.

Two IDs are currently reserved: `here` always refers to where the author's
viewpoint is currently located in the editor, and `me` for future use.
"""

help_text["properties"] = """
Most objects support most of the properties below, with different meanings
depending on each object's type:

- string properties: type, name, description, success, failure, drop, nodrop;
- reference properties: link, location;
- numeric properties: score;
- variant properties: lock.

Of these, the editor is aware of type, name, description, location
and link. All others are only meaningful to the story file interpreter.
"""

help_text["success"] = """
The `success` property contains a message to be shown when the object is
successfully used by the player. What that means depends on object type:

- a room is successfully used when seen (and lit);
- an exit is successfully used when traversed;
- a thing is successfully used when picked up.
"""

help_text["linking"] = """
Link is the quick command to set the target of an exit, room, etc. Syntax:

	link source-id|here target-id

Most objects can be linked to others. What that means depends on the type:

- for exit objects (the most common case), it's where the exit leads to;
- for room objects, it means where anything dropped in that room ends up
  (think being at the top of a tree, versus the ground below);
- a thing linked to something else will make the target not dark when
  successfully picked up. Obvious use case: remove a tapestry from a wall
  to reveal a secret passage.
"""

help_text["flags"] = """
- dark
- sticky
- visited
- light
- ending
"""

help_text["dark"] = """
The dark flag applies to most types of objects:

- in a dark room you can't see the room itself or any present objects,
  unless a source of light is in scope;
- a dark exit or thing is invisible even in a lit room, and impossible
  to interact with.
"""

help_text["sticky"] = """
The sticky flag applies to most types of objects:

- a sticky thing can't be dropped once picked up;
- a sticky room won't let you drop anything inside it;
- a sticky actor will follow the player around once they meet;
- a sticky exit remains unlocked after the lock has been bypassed once.
"""

help_text["ending"] = """
The game ends when an object with the `ending` flag set is successfully
used by the player (see: success). The object's success message will be
shown with appropriate formatting. Currently this only works for rooms
and exits.
"""

help_text["meta"] = """
The Adventure Prompt story file format supports a variety of metadata.
You can manipulate it with the `meta` command, in one of three forms:

	meta			# Display all the metadata currently set.
	meta <field>		# Delete given field from the metadata.
	meta <field> <value>	# Set a new value for the given field.

Currently the interpreter supports the following fields: title*, subtitle,
author*, date, genre, blurb, license, ifid*, language:

- the title and author should always be present; new stories get defaults;
- the date (of first publication) should be a year, or else an ISO date in
  yyyy-mm-dd format;
- the language code (e.g. en-US) isn't shown to readers, but the interpreter
  passes it on to the web browser;
- the IFID (note: keep the field name in lower case) is a unique identifier
  generated for each new story file; if you need another one for any reason,
  enter the following command at the prompt:
  
	!print(str(uuid.uuid4()))
"""

def shell_parse(text):
	try:
		return shlex.split(text)
	except ValueError as e:
		print(e)
		return []

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

def new_exit(name, loc=None):
	return {
		"type": "exit",
		"name": name,
		"link": None,
		"location": loc
	}

def new_thing(name, loc=None):
	return {
		"type": "thing",
		"name": name,
		"description": "",
		"location": loc
	}

class Editor(cmd.Cmd):
	intro = app_banner
	prompt = "\n> "
	
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.new_game()
		self.trash = {}

	def new_game(self):
		self.game = {
			"meta": new_meta(),
			"objects": {
				"limbo": new_room("Limbo"),
				"hero": new_actor("me", "limbo")
			},
			"config": new_config()
		}
		self.setprop("limbo", "description", "You are in limbo.")
	
		self.here = "limbo"
		self.modified = False
	
	def find(self, prop, val):
		obj = self.game["objects"]
		return [o for o in obj if obj[o].get(prop) == val]
	
	def examine(self, obj_id):
		obj = self.game["objects"][obj_id]
		print("Object {0}:".format(obj_id))
		for i in obj:
			print("{0}: {1}".format(i, obj[i]))
	
	def setprop(self, obj, prop, val):
		if obj in self.game["objects"]:
			target = self.game["objects"][obj]
			if val != False and val != None and val != "":
				target[prop] = val
			elif prop in target:
				del target[prop]
		else:
			print("No such object: {0}".format(obj))

	def goto(self, room):
		if room in self.game["objects"]:
			self.here = room
			self.look(self.here)
		else:
			print("Can't go to {0}: no such object".format(room))
	
	def look(self, room):
		where = self.game["objects"][room]
		print("{0} (id: {1})".format(where["name"], room))
		print(where["description"])
		if "success" in where:
			print(where["success"])
		
		allhere = self.find("location", room)

		for i in allhere:
			obj = self.game["objects"][i]
			if obj["type"] == "actor":
				print("\n{0} ({1}) is here.".format(
					obj["name"], i))
		
		print("\nExits:")
		for i in allhere:
			obj = self.game["objects"][i]
			if obj["type"] == "exit":
				print("\t{0} ({1})".format(obj["name"], i))
		
		print("\nYou can see:")
		for i in allhere:
			obj = self.game["objects"][i]
			if obj["type"] not in ["exit", "actor"]:
				print("\t{0} ({1})".format(obj["name"], i))
	
	def do_look(self, args):
		"""Look at the room you're in, or else the named object."""
		args = shell_parse(args)
		if len(args) < 1:
			self.look(self.here)
		elif args[0] in self.game["objects"]:
			print(self.game["objects"][args[0]]["description"])
			for i in self.game["objects"]:
				obj = self.game["objects"][i]
				if obj["location"] == args[0]:
					print("\t{0} ({1})".format(obj["name"], i))
					
		else:
			print("No such object: {0}".format(args[0]))
	
	def do_examine(self, args):
		"""List all properties of the named object."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: examine here|object-id')
		elif args[0] == "here":
			self.examine(self.here)
		elif args[0] in self.game["objects"]:
			self.examine(args[0])
		else:
			print("No such object: {0}".format(args[0]))

	def do_say(self, args):
		"""Print a newline, message, or an object's property value."""
		args = shell_parse(args)
		if len(args) < 1:
			print()
		elif len(args) < 2:
			print(args[0], end="")
		elif args[0] == "here":
			room = self.game["objects"][self.here]
			if args[1] in room:
				print(room[args[1]], end="")
		elif args[0] in self.game["objects"]:
			obj = self.game["objects"][args[0]]
			if args[1] in obj:
				print(obj[args[1]], end="")
		else:
			print("No such object: {0}".format(args[0]))
	
	def do_dig(self, args):
		"""Create a new room with given name and ID."""
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: dig "Room name" room-id')
		elif args[1] in self.game["objects"]:
			print("ID {0} already in use.".format(args[1]))
		elif args[1] == "here" or args[1] == "me":
			print("{0} is a reserved word.".format(args[1]))
		else:
			self.game["objects"][args[1]] = new_room(args[0])
			self.modified = True
			print("Room created.")
	
	def do_teleport(self, args):
		"""Move the viewpoint or an object to another location."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: tel [object-id] here|room-id')
		elif len(args) < 2:
			if args[0] in self.game["objects"]:
				self.here = args[0]
				self.look(self.here)
			elif args[0] == "here":
				print("Nothing to do")
			else:
				print("No such object: {0}".format(args[0]))
		elif args[0] in self.game["objects"]:
			if args[1] in self.game["objects"]:
				self.setprop(args[0], "location", args[1])
				self.modified = True
				print("Obj. {0} moved to {1}.".format(*args))
			elif args[1] == "here":
				self.setprop(args[0], "location", self.here)
				self.modified = True
				print("Obj. {0} brought here.".format(args[0]))
			else:
				print("No such object: {0}.".format(args[1]))
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_name(self, args):
		"""Change the name of a room or other object."""
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: name here|object-id "New name"')
		elif args[0] == "here":
			self.setprop(self.here, "name", args[1])
			self.modified = True
			print("Room name changed.")
		elif args[0] in self.game["objects"]:
			self.setprop(args[0], "name", args[1])
			self.modified = True
			print("Name of {0} changed.".format(args[0]))
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_desc(self, args):
		"""Change the description of a room or other object."""
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: desc here|object-id "New description"')
		elif args[0] == "here":
			self.setprop(self.here, "description", args[1])
			self.modified = True
			print("Room description changed.")
		elif args[0] in self.game["objects"]:
			self.setprop(args[0], "description", args[1])
			self.modified = True
			print("Description of {0} changed.".format(args[0]))
		else:
			print("No such object: {0}.".format(args[0]))

	def do_open(self, args):
		"""Create an exit to another room at the current location."""
		objs = self.game["objects"]
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: open "Exit name" exit-id [dest-id]')
		elif args[1] in objs:
			print("Object {0} already exists.".format(args[1]))
		elif args[1] == "here" or args[1] == "me":
			print("{0} is a reserved word.".format(args[1]))
		elif len(args) < 3:
			objs[args[1]] = new_exit(args[0], self.here)
			self.modified = True
			print("Exit created.")
		elif args[2] in objs:
			objs[args[1]] = new_exit(args[0], self.here)
			objs[args[1]]["link"] = args[2]
			self.modified = True
			print("Exit created and linked.")
		else:
			print("No such object: {0}.".format(args[2]))
	
	def do_go(self, args):
		"""Follow an exit to its destination."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: go exit-name')
			return

		allhere = self.find("location", self.here)
		
		for i in allhere:
			obj = self.game["objects"][i]
			if obj["type"] == "exit" and obj["name"] == args[0]:
				self.goto(obj["link"])
				return

		print("You can't go that way.")
	
	def do_link(self, args):
		"""Change the destination of an existing exit or room."""
		here = self.game["objects"][self.here]
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: link source-id|here target-id')
		elif args[1] not in self.game["objects"]:
			print("No such object: {0}.".format(args[1]))
		elif args[0] == "here":
			here["link"] = args[1]
			self.modified = True
			print("Room relinked.")
		elif args[0] in self.game["objects"]:
			self.game["objects"][args[0]]["link"] = args[1]
			self.modified = True
			print("Object relinked.")
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_unlink(self, args):
		"""Remove an exit or room destination."""
		here = self.game["objects"][self.here]
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: unlink exit-id|here|room-id')
		elif args[0] == "here":
			del here["link"]
			self.modified = True
			print("Room unlinked.")
		elif args[0] in self.game["objects"]:
			del self.game["objects"][args[0]]["link"]
			self.modified = True
			print("Object unlinked.")
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_lock(self, args):
		"""Set a lock on the given object."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage 1: lock object-id')
			print('Usage 2: lock object-id vehicleID')
			print('Usage 2: lock object-id !vehicleID')
			print('Usage 3: lock object-id +thingID')
			print('Usage 4: lock object-id -thingID')
			print('Usage 5: lock object-id <property> <value>')
		elif args[0] not in self.game["objects"]:
			print("No such object: {0}.".format(args[1]))
		elif len(args) < 2:
			self.setprop(args[0], "lock", True)
			self.modified = True
			print("Object locked unconditionally.")
		elif len(args) < 3:
			if args[1][0] in ["!", "+", "-"]:
				obj_id = args[1][1:]
			else:
				obj_id = args[1]
			
			if obj_id not in self.game["objects"]:
				print("No such object: {0}.".format(obj_id))
			elif args[0] not in self.game["objects"]:
				print("No such object: {0}.".format(args[0]))
			else:
				self.setprop(args[0], "lock", args[1])
				print("Object locked to given key.")
		else:
			self.setprop(args[0], "lock", {args[1]: args[2]})
			self.modified = True
			print("Object locked to property value.")
	
	def do_unlock(self, args):
		"""Remove any lock from the given object."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: unlock object-id')
		elif args[0] in self.game["objects"]:
			del self.game["objects"][args[0]]["lock"]
			self.modified = True
			print("Object unlocked.")
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_succ(self, args):
		"""Change the success message of a room or other object."""
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: succ here|object-id "New message"')
		elif args[0] == "here":
			self.setprop(self.here, "success", args[1])
			self.modified = True
			print("Room success message changed.")
		elif args[0] in self.game["objects"]:
			self.setprop(args[0], "success", args[1])
			self.modified = True
			print("Success msg. of {0} changed.".format(args[0]))
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_fail(self, args):
		"""Change the failure message of a room or other object."""
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: fail here|object-id "New message"')
		elif args[0] == "here":
			self.setprop(self.here, "failure", args[1])
			self.modified = True
			print("Room failure message changed.")
		elif args[0] in self.game["objects"]:
			self.setprop(args[0], "failure", args[1])
			self.modified = True
			print("Failure msg. of {0} changed.".format(args[0]))
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_drop(self, args):
		"""Change the drop message of a room or other object."""
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: drop here|object-id "New message"')
		elif args[0] == "here":
			self.setprop(self.here, "drop", args[1])
			self.modified = True
			print("Room drop message changed.")
		elif args[0] in self.game["objects"]:
			self.setprop(args[0], "drop", args[1])
			self.modified = True
			print("Drop msg. of {0} changed.".format(args[0]))
		else:
			print("No such object: {0}.".format(args[0]))
	
	def do_create(self, args):
		"""Create a thing here."""
		objs = self.game["objects"]
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: create "Thing name" thing-id')
		elif args[1] in objs:
			print("Object {0} already exists.".format(args[1]))
		elif args[1] == "here" or args[1] == "me":
			print("{0} is a reserved word.".format(args[1]))
		else:
			objs[args[1]] = new_thing(args[0], self.here)
			self.modified = True
			print("Thing created.")
	
	def do_clone(self, args):
		"""Clone an existing object with a different ID."""
		objs = self.game["objects"]
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage: clone old-id new-id')
		elif args[0] not in self.game["objects"]:
			print("No such object: {0}.".format(args[0]))
		elif args[1] in objs:
			print("Object {0} already exists.".format(args[1]))
		elif args[1] == "here" or args[1] == "me":
			print("{0} is a reserved word.".format(args[1]))
		else:
			objs[args[1]] = objs[args[0]].copy()
			self.modified = True
			print("Object cloned.")
	
	def do_set(self, args):
		"""Set a certain flag or property on a given object."""
		objs = self.game["objects"]
		args = shell_parse(args)
		if len(args) < 2:
			print('Usage 1: set object-id [!]flag-name')
			print('Usage 2: set object-id prop-name prop-value')
		elif args[0] not in objs:
			print("No such object: {0}.".format(args[0]))
		elif len(args) < 3:
			if args[1][0] != "!":
				self.setprop(args[0], args[1], True)
				print("Flag set.")
			else:
				self.setprop(args[0], args[1][1:], False)
				print("Flag reset.")
			self.modified = True
		else:
			self.setprop(args[0], args[1], parse_value(args[2]))
			print("Property changed.")
			self.modified = True
	
	def do_find(self, args):
		"""Find all objects with a certain flag or property."""
		objs = self.game["objects"]
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage 1: find [!]flag-name')
			print('Usage 2: find prop-name prop-value')
		elif len(args) < 2:
			if args[0][0] != "!":
				found = self.find(args[0], True)
			else:
				found = self.find(args[0][1:], False)
			for i in found:
				name = objs[i]["name"]
				print("{0} (id: {1})".format(name, i))
		else:
			found = self.find(args[0], args[1])
			for i in found:
				name = objs[i]["name"]
				print("{0} (id: {1})".format(name, i))
	
	def do_recycle(self, args):
		"""Move an object to the recycle bin."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: recycle object-id')
		elif args[0] == "here" or args[0] == self.here:
			print("Can't recycle the room you're in right now.")
		elif args[0] == "hero":
			print("Can't recycle the hero of the story.")
		elif args[0] == self.game["objects"]["hero"]["location"]:
			print("Can't recycle the hero's current location.")
		elif args[0] in self.game["objects"]:
			self.trash[args[0]] = self.game["objects"][args[0]]
			del self.game["objects"][args[0]]
			self.modified = True
			print("Object moved to recycle bin.")
	
	def do_unrecycle(self, args):
		"""Bring an object back from the recycle bin."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: unrecycle object-id')
		elif args[0] in self.trash:
			self.game["objects"][args[0]] = self.trash[args[0]]
			del self.trash[args[0]]
			self.modified = True
			print("Object brought back from recycle bin.")
		else:
			print("No such object in the recycle bin.")
	
	def do_meta(self, args):
		"""List or change game metadata such as title and author."""
		args = shell_parse(args)
		if len(args) < 1:
			meta = self.game["meta"]
			for i in meta:
				print("{0}: {1}".format(i, meta[i]))
		elif len(args) < 2:
			del self.game["meta"][args[0]]
			self.modified = True
			print("Field deleted.")
		else:
			self.game["meta"][args[0]] = args[1]
			self.modified = True
			print("Field value changed.")
	
	def do_config(self, args):
		"""List or change configuration settings like the banner."""
		config = self.game["config"]
		args = shell_parse(args)
		if len(args) < 1:
			for i in config:
				print("{0}: {1}".format(i, config[i]))
		elif len(args) < 2:
			if args[0] in config:
				print("{0}: {1}".format(
					args[0], config[args[0]]))
			else:
				print("No such setting.")
		else:
			self.game["config"][args[0]] = parse_value(args[1])
			self.modified = True
			print("Field value changed.")
	
	def do_new(self, args):
		"""Start over with a blank game."""
		args = shell_parse(args)
		if not self.modified:
			self.new_game();
			print("New game initialized.")
		elif len(args) > 0 and args[0] == "forced":
			self.new_game();
			print("New game initialized.")
		else:
			print("You have an unsaved game in progress.")
			print("Type NEW FORCED to override.")
	
	def do_save(self, args):
		"""Save current game to disk."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: save <filename>')
		else:
			try:
				with open(args[0], "w") as f:
					json.dump(self.game, f)
				self.modified = False
				print("Game saved.")
			except Exception as e:
				print("Couldn't save game: " + str(e))
	
	def do_restore(self, args):
		"""Restore a game from disk."""
		args = shell_parse(args)
		if len(args) < 1:
			print('Usage: restore <filename>')
		else:
			try:
				with open(args[0], "r") as f:
					game = json.load(f)
					# TO DO: sanity checks
					self.game = game
					self.here = game["objects"]["hero"]["location"]
				print("Game restored.")
			except Exception as e:
				print("Couldn't restore game: " + str(e))
	
	def do_quit(self, args):
		"""Quit the editor and return to the operating system."""
		args = shell_parse(args)
		if not self.modified:
			return True
		elif len(args) > 0 and args[0] == "forced":
			return True
		else:
			print("You have an unsaved game in progress.")
			print("Type QUIT FORCED to override.")
	
	def do_shell(self, args):
		"""Run Python code in a global context, for debugging."""
		try:
			exec(args, globals())
		except Exception as e:
			print(e)
	
	def default(self, line):
		args = shell_parse(line)
		if args[0] == "l":
			if len(args) < 2:
				return self.do_look("")
			else:
				return self.do_look(args[1])
		elif args[0] == "tel":
			if len(args) < 2:
				return self.do_teleport("")
			elif len(args) < 3:
				return self.do_teleport(args[1])
			else:
				return self.do_teleport(
					args[1] + " " + args[2])
		elif args[0] == "ex":
			return self.do_examine(args[1])
		elif len(args) == 1:
			return self.do_go(args[0])
		else:
			print("Unknown command: {0}.".format(args[0]))
	
	def help_basics(self):
		print(help_text["basics"])
	
	def help_shortcuts(self):
		print(help_text["shortcuts"])
	
	def help_objects(self):
		print(help_text["objects"])
	
	def help_types(self):
		print(help_text["types"])
	
	def help_identifiers(self):
		print(help_text["identifiers"])
	
	def help_rooms(self):
		print("To be done.")
	
	def help_exits(self):
		print("To be done.")
	
	def help_linking(self):
		print(help_text["linking"])
	
	def help_locking(self):
		print("To be done.")
	
	def help_properties(self):
		print(help_text["properties"])
	
	def help_flags(self):
		print(help_text["flags"])
	
	def help_ending(self):
		print(help_text["ending"])
	
	def help_success(self):
		print(help_text["success"])
	
	def help_dark(self):
		print(help_text["dark"])
	
	def help_sticky(self):
		print(help_text["sticky"])
	
	def help_visited(self):
		print("To be done.")
	
	def help_meta(self):
		print(help_text["meta"])

if __name__ == "__main__":
	editor = Editor()
	editor.cmdloop()
