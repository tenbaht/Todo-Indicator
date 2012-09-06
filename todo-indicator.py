#!/usr/bin/env python


import fileinput
import os
import sys

from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator


DARK_PANEL_ICON = "gtg-panel"
TESTING_TODO_FILE = "sample-todo.txt"
EDITOR = "xdg-open"


class TodoIndicator(object):

    def __init__(self, todo_filename):
        """Sets the filename, loads the list of items from the file, builds the
        indicator."""
        self.todo_filename = todo_filename
        self._build_indicator() # creates self.ind

    def _load_todo_file(self):
        """Populates the list of todo items from the todo file."""
        f = open(self.todo_filename)
        todo_list = f.read().split("\n")
        f.close()
        self.todo_list = sorted(filter(None, todo_list)) # kill empty items+sort

    def _check_off_item_with_label(self, label):
        """Matches the given todo item, finds it in the file, and "checks it
        off" by adding "x " to the beginning of the string. If you have
        multiple todo items that are exactly the same, this will check them all
        off. Also, you're stupid for doing that."""
        for line in fileinput.input(self.todo_filename, inplace=1):
            if line.strip() == label:
                print "x " + line, # magic!
            else:
                print line,

    def _check_off_handler(self, menu_item):
        self._check_off_item_with_label(menu_item.get_label()) # write file
        self._build_indicator() # rebuild!

    def _edit_handler(self, menu_item):
        """Opens the todo.txt file with selected editor."""
        os.system(EDITOR + " " + self.todo_filename)

    def _refresh_handler(self, menu_item):
        """Refreshes the list."""
        # TODO: gives odd warning about removing a child...
        self._build_indicator() # rebuild indicator

    def _quit_handler(self, menu_item):
        """Quits our fancy little program."""
        Gtk.main_quit()

    def _build_indicator(self):
        """Builds the Indicator object."""
        self.ind = appindicator.Indicator.new("todo-txt-indicator",
                                         DARK_PANEL_ICON,
                                         appindicator.IndicatorCategory.OTHER)
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        menu = Gtk.Menu()

        # make sure the list is loaded
        self._load_todo_file()

        # create todo menu items
        for todo_item in self.todo_list:
            menu_item = Gtk.MenuItem(todo_item)
            if todo_item[0:2] == 'x ': # gray out completed items
                menu_item.set_sensitive(False)
            menu_item.connect("activate", self._check_off_handler)
            menu_item.show()
            menu.append(menu_item)

        # add a separator
        menu_item = Gtk.SeparatorMenuItem()
        menu_item.show()
        menu.append(menu_item)

        # add "edit list" menu item
        menu_item = Gtk.MenuItem("Edit todo.txt")
        menu_item.connect("activate", self._edit_handler)
        menu_item.show()
        menu.append(menu_item)

        # add "refresh" menu item
        menu_item = Gtk.MenuItem("Refresh")
        menu_item.connect("activate", self._refresh_handler)
        menu_item.show()
        menu.append(menu_item)

        # add quit menu item
        menu_item = Gtk.MenuItem("Quit")
        menu_item.connect("activate", self._quit_handler)
        menu_item.show()
        menu.append(menu_item)

        # do it!
        self.ind.set_menu(menu)

    def main(self):
        """The indicator's main loop."""
        Gtk.main()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        todo_filename = sys.argv[1]
    else:
        todo_filename = TESTING_TODO_FILE

    ind = TodoIndicator(todo_filename)
    ind.main()
