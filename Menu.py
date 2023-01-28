
class Menu:
    def __init__(self, menu_items = None):
        self.menu_items = menu_items
        if menu_items is None:
            self.menu_items = []
        self.current_item = 0
    
    def pick_current_item(self):
        item: MenuItem = self.menu_items[self.current_item]
        item.pick_item()
    
    def select_next_item(self):
        self.current_item += 1
        if len(self.menu_items) <= self.current_item:
            self.current_item = 0

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
