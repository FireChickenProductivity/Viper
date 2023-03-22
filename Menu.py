import csv
from talon import actions

class Menu:
    def __init__(self, menu_items = None):
        self.menu_items = menu_items
        if menu_items is None:
            self.menu_items = []
        self.current_item = 0
   
    def pick_current_item(self):
        item: MenuItem = self.menu_items[self.current_item]
        item.pick_item()
   
    def select_next_item(self, direction: int = 1):
        # if direction = 1 move down if -1 move up
        self.current_item = (self.current_item + direction) % len(self.menu_items)

    def reset_selection(self):
        self.current_item = 0

    def get_items(self):
        return self.menu_items
   
    def get_current_item_number(self):
        return self.current_item
   
    def add_item(self, display_name: str, action):
        new_item: MenuItem = MenuItem(display_name, action)
        self.menu_items.append(new_item)

class MenuItem:
    def __init__(self, display_name: str, action):
        self.display_name = display_name
        self.action = action
   
    def pick_item(self):
        self.action()
   
    def get_display_name(self):
        return self.display_name

    def is_individual_item(self):
        return True

#Function provided by WhatIV
def compute_menu_from_csv(file_name):
    csv_Menu = Menu()
    with open(file_name) as menu_file:
        menu_info = csv.reader(menu_file)
        for item in menu_info:
            csv_Menu.add_item(item[0],getattr(actions,item[1]))

    return csv_Menu
