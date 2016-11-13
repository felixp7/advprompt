Adventure Prompt
================


Adventure Prompt is a system for authoring interactive fiction interactively, the same way online building works in a [MUSH][] or [MUCK][]. Walking simulators, or even simple room escape games, can be created without any scripting, unless you count the command language itself.

[MUSH]: https://en.wikipedia.org/wiki/MUSH
[MUCK]: https://en.wikipedia.org/wiki/TinyMUCK

Currently, the system is made of two components: the editor, `advprompt.py`, is a command-line program (written and tested in Python 3.3, though 2.7 should work) that also contains most of the documentation, available through a live help system. It can also run in IDLE: open the file with Ctrl-O, then press F5 to run it as a module. The story file runner, or interpreter, is currently implemented as an HTML5 single-page application that can open locally saved story files. It currently lags behind the capabilities described in the editor documentation.

Between the editor and runner sits the story file format, a simple and uniform database currently serialized as JSON, that encodes a variety of game behaviors implicitly. An actual scripting language is planned for the future.
