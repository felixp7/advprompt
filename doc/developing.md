Development guide
=================


Between the editor and runner sits the story file format, a simple and uniform database currently serialized as JSON, that encodes a variety of game behaviors implicitly. It should be possible to implement an undo function -- at least the back-and-forth kind -- in the same way restarting works.

Currently there are no provisions for localizations, but few messages are hardcoded, and most of them can be overridden in-game.
