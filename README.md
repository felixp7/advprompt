Adventure Prompt
================


Adventure Prompt is an interactive fiction authoring system with a twist. Two or three, even.

For players
-----------

Games come in files with the `.json` extension. (Beware, not all are made for Adventure Prompt!) You can open them with an interpreter called `promptrun.html` -- a single-page web app. It's also possible to find a game pre-bundled, but you can still use the top toolbar to open any other.

You play through a book-like interface with buttons you can click or tap. Most of the information you need is always visible on the screen.

For authors
-----------

If you ever used a [MUSH][] or [MUCK][], you may be acquainted with the online building commands. The Adventure Prompt editor works exactly like that. There are more properties, and more object types, and some details differ, is all.

[MUSH]: https://en.wikipedia.org/wiki/MUSH
[MUCK]: https://en.wikipedia.org/wiki/TinyMUCK

Everything in Adventure Prompt is done by creating objects and setting their properties. Walking simulators, treasure hunts or even room escape games can be created without any scripting, unless you count the command language itself. Moreover, all objects support the same properties, so there's less to remember. It's just that the meaning of a property depends on context.

The editor, `advprompt.py`, is a command-line program (written and tested in Python 3.3, though 2.7 should work) that also contains most of the documentation, available through a live help system. It can also run in IDLE: open the file with Ctrl-O, then press F5 to run it as a module.

The story file runner, or interpreter, currently lags behind the capabilities described in the editor documentation. Bundling a game with the interpreter is not yet automated either.

For developers
--------------

Between the editor and runner sits the story file format, a simple and uniform database currently serialized as JSON, that encodes a variety of game behaviors implicitly. It should be possible to implement an undo function -- at least the back-and-forth kind -- in the same way restarting works.

Currently there are no provisions for localizations, but few messages are hardcoded, and most of them can be overridden in-game.
