#!/usr/bin/env python3
import json
import os
import sys

from ui import handle as ui_handle
from receiver import handle as receiver_handle


def run():
	config = {
		"format": "{$title$}{$if_artist$ - $}{$artist$}",
		"css": "#nowplaying {\n\tfont-family: sans-serif;\n}",
	}
	if os.path.isfile(os.path.join(os.path.dirname(sys.argv[0]), "settings.json")):
		with open(os.path.join(os.path.dirname(sys.argv[0]), "settings.json"), "r", encoding="utf-8") as configfile:
			try:
				config = config | json.load(configfile)
			except Exception:
				pass

	if len(sys.argv) == 1:
		# Config UI
		ui_handle(config)
	else:
		# Receiving data from Firefox
		receiver_handle(config)


if __name__ == '__main__':
	run()
