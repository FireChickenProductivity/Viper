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
        if item.should_reset_menu_index_after_use():
            self.reset_selection()
   
    def select_next_item(self, direction: int = 1):
        # if direction = 1 move down if -1 move up
        self.current_item = (self.current_item + direction) % len(self.menu_items)

    def select_item(self, item_number: int):
        self.current_item = item_number
        
    def reset_selection(self):
        self.current_item = 0

    def get_items(self):
        return self.menu_items
   
    def get_current_item_number(self):
        return self.current_item
   
    def add_item(self, display_name: str, action, reset_menu_index_after_use: bool = True):
        new_item: MenuItem = MenuItem(display_name, action, reset_menu_index_after_use)
        self.menu_items.append(new_item)

class MenuItem:
    def __init__(self, display_name: str, action, reset_menu_index_after_use: bool = True):
        self.display_name = display_name
        self.action = action
        self.reset_menu_index_after_use = reset_menu_index_after_use
   
    def pick_item(self):
        self.action()
   
    def get_display_name(self):
        return self.display_name

    def is_individual_item(self):
        return True
    
    def should_reset_menu_index_after_use(self):
        return self.reset_menu_index_after_use

#Function provided by WhatIV
def compute_menu_from_csv(file_name):
    csv_Menu = Menu()
    with open(file_name) as menu_file:
        menu_info = csv.reader(menu_file)
        for item in menu_info:
            name = item[0]
            action = item[1]
            reset_menu_index_after_use = True
            if len(item) > 2:
                action = item[2]
                reset_menu_index_after_use = item[1] == 'reset'
                print(reset_menu_index_after_use)
            csv_Menu.add_item(name, compute_action(action), reset_menu_index_after_use)

    return csv_Menu

def compute_action(action_description: str):
    action = action_description
    argument = None
    if action_description.startswith('key ') or action_description.startswith('insert '):
        action, _, argument = action_description.partition(' ')
        function = getattr(actions, action)
        return lambda: function(argument)
    return getattr(actions, action_description)