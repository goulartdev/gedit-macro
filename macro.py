# Macro Plugin 1.0.0

# This version for Gedit 3, by Djonathan Goulart <d.goulart@outlook.com.br>, Jan 13, 2017.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gtk, Gedit, Gio

START_REC_ACTION = {
	"name": "start_recording",
	"title": "St_art Recording",
	"key": None,
	"enabled": True,
	"callback": None
}

STOP_REC_ACTION = {
	"name": "stop_recording",
	"title": "St_op Recording",
	"key": None,
	"enabled": True,
	"callback": None
}

PLAYBACK_ACTION = {
	"name": "playback",
	"title": "_Playback",
	"key": "<Primary><Shift>P",
	"enabled": True,
	"callback": None
}

REPEAT_PLAYBACK_ACTION = {
	"name": "repeat_playback",
	"title": "Run Multiple Times",
	"key": "<Primary><Shift>T",
	"enabled": False,
	"callback": None
}

ACTION_DEFS = [
	START_REC_ACTION, STOP_REC_ACTION, PLAYBACK_ACTION, REPEAT_PLAYBACK_ACTION
]

class MacroPlugin:

	def __init__(self, window):
		self.clear()
		self.window = window
		self.is_running = False
		self.handler_id = None

	def start_recording(self):
		self.is_running = True
		self.macro.clear()
		self.handler_id = self.window.connect('key-press-event', self.record_key)

	def stop_recording(self):
		self.is_running = False
		self.window.disconnect(self.handler_id)

	def record_key(self, window, event):
		self.macro.append(event.copy())

	def clear(self):
		self.macro = []

	def playback(self):
		for e in self.macro:
			e.put()

	def repeat_playback(self, count):
		for _ in range(count):
			self.playback()


class MacroAppActivatable(GObject.Object, Gedit.AppActivatable):

	__gtype_name__ = 'MacroAppActivatable'

	app = GObject.Property(type=Gedit.App)

	def __init__(self):
		GObject.Object.__init__(self)
		self.menu_ext = None

	def do_activate(self):
		self.insert_menu()

	def do_deactivate(self):
		self.menu_ext = None

	def insert_menu(self):
		self.menu_ext = self.extend_menu('tools-section')

		menu = Gio.Menu()

		for action_def in ACTION_DEFS:
			if (not action_def["enabled"]):
				continue

			full_name = "win." + action_def["name"]

			if (action_def["key"] is not None):
				self.app.add_accelerator(action_def["key"], full_name, None)

			item = Gio.MenuItem.new(action_def["title"], full_name)
			menu.append_item(item)

		menu_item = Gio.MenuItem.new_submenu("Macro", menu)
		self.menu_ext.append_menu_item(menu_item)


class MacroindowsActivatable(GObject.Object, Gedit.WindowActivatable):

	__gtype_name__ = 'MacroWindowsActivatable'

	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):

		self.macro = MacroPlugin(self.window)

		START_REC_ACTION["callback"] = self.macro.start_recording
		STOP_REC_ACTION["callback"] = self.macro.stop_recording
		PLAYBACK_ACTION["callback"] = self.macro.playback

		for action_def in ACTION_DEFS:
			if (not action_def["enabled"]):
				continue

			action = Gio.SimpleAction(name = action_def["name"])
			action.connect("activate", self.activate_cb, action_def["name"])
			self.window.add_action(action)

		self.update_ui()

	def do_deactivate(self):
		self.macro = None
		self.handler_id = None

		for action_def in ACTION_DEFS:
			if (not action_def["enabled"]):
				continue

			self.window.remove_action(action_def["name"])

	def activate_cb(self, action, data, action_name):
		for action_def in ACTION_DEFS:
			if (action_name == action_def["name"]):
				action_def["callback"]()

		self.update_ui()


	def update_ui(self):
		self.window.lookup_action(START_REC_ACTION["name"]).set_enabled(not self.macro.is_running)
		self.window.lookup_action(STOP_REC_ACTION["name"]).set_enabled(self.macro.is_running)
		self.window.lookup_action(PLAYBACK_ACTION["name"]).set_enabled(not self.macro.is_running)
