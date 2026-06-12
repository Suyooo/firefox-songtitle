import html
import importlib
import json
import os
import re
import sys


def receive():
	length = int.from_bytes(sys.stdin.buffer.read(4), 'little')
	msg = sys.stdin.buffer.read(length).decode('utf-8')
	return json.loads(msg)


def send(msg):
	msg = json.dumps(msg).encode('utf-8')
	sys.stdout.buffer.write(len(msg).to_bytes(4, 'little'))
	sys.stdout.buffer.write(msg)


def handle(config):
	try:
		msg = receive()
		if "version" in msg and msg["version"] != 1:
			raise Exception("The desktop application is outdated, please update! https://github.com/Suyooo/firefox-nowplaying/releases/")

		formatted = config["format"]

		formatted = re.sub(r"\{\$if_artist\$(.+?)\$\}", r"\1" if ("artist" in msg and msg["artist"]) else "", formatted)
		formatted = re.sub(r"\{\$if_album\$(.+?)\$\}", r"\1" if ("album" in msg and msg["album"]) else "", formatted)

		raw_formatted = formatted.replace("{$title$}", 
			msg["title"] if ("title" in msg and msg["title"]) else "")
		raw_formatted = raw_formatted.replace("{$artist$}", 
			msg["artist"] if ("artist" in msg and msg["artist"]) else "")
		raw_formatted = raw_formatted.replace("{$album$}", 
			msg["album"] if ("album" in msg and msg["album"]) else "")
		raw_formatted = raw_formatted.replace("{$artwork$}", 
			msg["artwork"] if ("artwork" in msg and msg["artwork"]) else "")

		html_formatted = formatted.replace(
				"{$title$}",
				('<span id="title">' + html.escape(msg["title"]) + "</span>")
					if ("title" in msg and msg["title"]) else ""
			)
		html_formatted = html_formatted.replace(
				"{$artist$}",
				('<span id="artist">' + html.escape(msg["artist"]) + "</span>")
					if ("artist" in msg and msg["artist"]) else ""
			)
		html_formatted = html_formatted.replace(
				"{$album$}",
				('<span id="album">' + html.escape(msg["album"]) + "</span>")
					if ("album" in msg and msg["album"]) else ""
			)
		html_formatted = html_formatted.replace(
				"{$artwork$}",
				('<img id="artwork" src="' + html.escape(msg["artwork"]) + '" />')
					if ("artwork" in msg and msg["artwork"]) else ""
			)

		text_file_path = os.path.join(os.path.dirname(sys.argv[0]), "nowplaying.txt")
		with open(text_file_path + ".tmp", "w", encoding="utf-8") as outfile:
			outfile.write(raw_formatted)
		os.replace(text_file_path + ".tmp", text_file_path)

		html_file_path = os.path.join(os.path.dirname(sys.argv[0]), "nowplaying.html")
		with importlib.resources.open_text(__name__, "nowplaying-template.html", encoding="utf-8") as templfile:
			with open(html_file_path + ".tmp", "w", encoding="utf-8") as outfile:
				outfile.write(templfile.read().replace("$FORMAT$", html_formatted).replace("$CSS$", config["css"]))
		os.replace(html_file_path + ".tmp", html_file_path)
		
		send("1")
	except Exception as e:
		msg = str(e)
		with open(os.path.join(os.path.dirname(sys.argv[0]), "error.txt"), "w", encoding="utf-8") as outfile:
			outfile.write(msg)
		send(msg)
