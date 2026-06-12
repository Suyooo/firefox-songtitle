import importlib.resources
import json
import os
import pathlib
import tkinter as tk
import tkinter.filedialog as tkfd
import sys

root = None
var_format = None
txt_css = None


class EntryNumber(tk.Entry):
	def __init__(self, master=None, textvariable=None, **kwargs):
		tk.Entry.__init__(self, master, textvariable=textvariable, **kwargs)
		self.old_value = textvariable.get()
		self.var = textvariable
		textvariable.trace('w', self.check)

	def check(self, *args):
		if self.var.get().isdigit(): 
			self.old_value = self.var.get()
		else:
			self.var.set(self.old_value)


def handle(config):
	global root, var_format, txt_css

	root = tk.Tk()
	root.title("Now Playing Config")

	var_format = tk.StringVar(value=config["format"])

	frm_install = tk.LabelFrame(text="Connect to Firefox", relief=tk.GROOVE, borderwidth=1, padx=10, pady=5)
	frm_install.columnconfigure(0, weight=1)
	frm_install.columnconfigure(1, weight=1)
	btn_install = tk.Button(master=frm_install, text="Connect", command=click_install)
	btn_install.grid(column=0, row=0, padx=5, sticky="we")
	btn_uninstall = tk.Button(master=frm_install, text="Disconnect", command=click_uninstall)
	btn_uninstall.grid(column=1, row=0, padx=5, sticky="we")
	frm_install.pack(fill=tk.X, padx=10, pady=5)

	frm_output = tk.LabelFrame(text="Text Format", relief=tk.GROOVE, borderwidth=1, padx=10, pady=5)
	etr_format = tk.Entry(master=frm_output, textvariable=var_format)
	etr_format.pack(fill=tk.X, padx=5, pady=5)
	frm_help = tk.Frame(master=frm_output)

	i = 0
	def add_help(left, right):
		nonlocal i
		lbl_help_l = tk.Label(master=frm_help, text=left, font=("monospace", 12, "bold"))
		lbl_help_l.grid(column=0, row=i, padx=5, sticky="nw")
		lbl_help_r = tk.Label(master=frm_help, wraplength=500, justify=tk.LEFT, anchor="w", text=right)
		lbl_help_r.grid(column=1, row=i, padx=5, sticky="nw")
		i += 1
	
	add_help("{$title$}", "The current song's title.")
	add_help("{$artist$}", "The current song's artist, can be empty.")
	add_help("{$album$}", "The current song's album name, can be empty.")
	add_help("{$artwork$}", "Artwork from the current song, could be a cover art or a video thumbnail. Will be output as an URL in the text file, and an image element in the HTML file.")
	add_help("{$if_artist$...$}", "If the current song has an artist defined, this is replaced with whatever you write in for ... - otherwise, it gets removed. Use this for seperators between title and artist.")
	add_help("{$if_album$...$}", "Like above, but for the album name.")
	frm_help.pack(fill=tk.X, pady=5)
	frm_output.pack(fill=tk.X, padx=10, pady=5)

	frm_style = tk.LabelFrame(text="CSS Styling", relief=tk.GROOVE, borderwidth=1, padx=10, pady=5)
	lbl_help_style = tk.Label(
			master=frm_style, wraplength=700, justify=tk.LEFT, anchor="w",
			text="Enter CSS here to insert into the HTML output file. You can use the #nowplaying selector to style the container surrounding everything, and the #title and #artist selectors to style just those parts."
		)
	lbl_help_style.pack(fill=tk.X, padx=5)
	frm_css = tk.Frame(master=frm_style)
	txt_css = tk.Text(master=frm_css, height=10, wrap="word")
	txt_css.insert("1.0", config["css"])
	scr_css = tk.Scrollbar(master=frm_css, orient="vertical", command=txt_css.yview)
	txt_css["yscrollcommand"] = scr_css.set
	txt_css.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
	scr_css.pack(side=tk.LEFT, fill=tk.Y)
	frm_css.pack(fill=tk.X, padx=5, pady=5)
	frm_style.pack(fill=tk.X, padx=10, pady=5)

	btn_save = tk.Button(text="Save Configuration", command=click_save)
	btn_save.pack(fill=tk.X, padx=10, pady=10)

	frm_footer = tk.Frame()
	with importlib.resources.open_text(__name__, "version") as versionfile:
		lbl_version = tk.Label(master=frm_footer, text="v" + versionfile.read(), font=("sans-serif", 8))
		lbl_version.pack(side=tk.LEFT)
	lbl_url = tk.Label(master=frm_footer, text="https://github.com/Suyooo/firefox-nowplaying/", font=("sans-serif", 8))
	lbl_url.pack(side=tk.RIGHT)
	frm_footer.pack(fill=tk.X)

	root.mainloop()


def click_install():
	try:
		with importlib.resources.open_text(__name__, "native-base.json") as jsonfile:
			newjson = json.load(jsonfile)
		
		if os.name == "nt":
			# Windows
			script_path = os.path.realpath(sys.argv[0])
			if script_path.endswith(".exe"):
				newjson["path"] = script_path
			else:
				with open(script_path + ".bat", "w", encoding="utf-8") as batchfile:
					batchfile.write("@echo off\n")
					batchfile.write(sys.executable)
					batchfile.write(" ")
					batchfile.write(script_path)
					batchfile.write(" %0")
				newjson["path"] = script_path + ".bat"
			with open(os.path.join(os.path.dirname(sys.argv[0]), "firefox_connection.json"), "w", encoding="utf-8") as jsonfile:
				json.dump(newjson, jsonfile, indent="\t")
			
			import winreg
			registry = winreg.CreateKey(
					winreg.HKEY_CURRENT_USER, "Software\\Mozilla\\NativeMessagingHosts"
				)
			winreg.SetValue(
					registry, "be.suyo.firefox_nowplaying", winreg.REG_SZ,
					os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "firefox_connection.json")
				)
			winreg.CloseKey(registry)
		else:
			# Linux / MacOS
			newjson["path"] = os.path.realpath(sys.argv[0])
			with open(os.path.join(
					pathlib.Path.home(), ".mozilla", "native-messaging-hosts", "be.suyo.firefox_nowplaying.json"
				), "w", encoding="utf-8") as jsonfile:
				json.dump(newjson, jsonfile, indent="\t")
		tk.messagebox.showinfo(title="Now Playing Config", message="Now Playing has been connected to Firefox!")
	except Exception as e:
		tk.messagebox.showerror(title="Now Playing Config", message="Failed to connect:\n" + str(e))


def click_uninstall():
	try:
		if os.name == "nt":
			# Windows
			import winreg
			registry = winreg.OpenKey(
					winreg.HKEY_CURRENT_USER, "Software\\Mozilla\\NativeMessagingHosts", 0, winreg.KEY_WRITE
				)
			winreg.DeleteKey(registry, "be.suyo.firefox_nowplaying")
			winreg.CloseKey(registry)
		else:
			# Linux / MacOS
			os.unlink(os.path.join(
					pathlib.Path.home(), ".mozilla", "native-messaging-hosts", "be.suyo.firefox_nowplaying.json"
				))
		tk.messagebox.showinfo(title="Now Playing Config", message="Now Playing has been disconnected from Firefox.")
	except Exception as e:
		tk.messagebox.showerror(title="Now Playing Config", message="Failed to disconnect:\n" + str(e))


def click_save():
	try:
		with open(os.path.join(os.path.dirname(sys.argv[0]), "settings.json"), "w", encoding="utf-8") as configfile:
			json.dump({
				"format": var_format.get(),
				"css": txt_css.get("1.0", "end"),
			}, configfile, indent="\t")
		tk.messagebox.showinfo(title="Now Playing Config", message="Configuration has been saved!")
	except Exception as e:
		tk.messagebox.showerror(title="Now Playing Config", message="Failed to save the configuration:\n" + str(e))
