from talon import actions
from .Menu import MenuItem

#whatIV contributed significantly to the keyboard code
#I made considerable edits to integrate it into my system

class KeyBoardItem:
    def __init__(self, key_name: str, display_name = None):
        self.key_name = key_name
        self.display_name = display_name
        if display_name is None:
            self.display_name = self.key_name
   
    def get_display_name(self):
        return self.display_name

class RowItem:
    def __init__(self, keyboard_items, display_name):
        self.keyboard_items = keyboard_items
        self.display_name = display_name
   
    def get_item(self, index):
        return self.keyboard_items[index]
   
    def get_items(self):
        return self.keyboard_items
   
    def compute_length(self):
        return len(self.keyboard_items)
   
    def get_display_name(self):
        return self.display_name
   
    def is_individual_item(self):
        return False

class KeyBoard:
    _keys_to_hold = ["shift","ctrl","alt","super"]
    def __init__(self):
        self.rows = []
        self.current_keystroke = ''
        self.current_row = 0
        self.current_column = 0
        self.last_keystroke = ''
   
    def set_rows(self, rows):
        self.rows = rows
        self.reset_selection()

    def pick_current_key(self):
        key: KeyBoardItem = self.get_current_key()
        self.add_key_to_keystroke(key)
        if KeyBoard.should_start_keystroke(key):
            self.perform_current_keystroke()
        self.reset_selection()

    def get_current_key(self):
        key: KeyBoardItem = self.rows[self.current_row].get_item(self.current_column)
        return key

    def add_key_to_keystroke(self, key: KeyBoardItem):
        if len(self.current_keystroke) == 0:
            self.current_keystroke = key.key_name
        else:
            self.current_keystroke += '-' + key.key_name

    @staticmethod
    def should_start_keystroke(key: KeyBoardItem):
        return not key.key_name in KeyBoard._keys_to_hold

    def perform_current_keystroke(self):
            actions.key(self.current_keystroke)
            self.last_keystroke = self.current_keystroke
            self.current_keystroke = ''
   
    def select_next_column(self, direction: int = 1):
        # if direction = 1 move down if -1 move up
        self.current_column = (self.current_column + direction) % self.rows[self.current_row].compute_length()


    def select_next_row(self, direction: int = 1):
        # if direction = 1 move down if -1 move up
        self.current_row = (self.current_row + direction) % len(self.rows)

   
    def get_current_row(self):
        return self.current_row
   
    def get_current_column(self):
        return self.current_column

    def get_current_column_items(self):
        items = self.rows[self.current_row].get_items()
        return items
   
    def get_current_row_items(self):
        return self.rows
   
    def pick_current_single_item_row(self):
        self.rows[self.current_row].pick_item()

    def is_on_single_item_row(self):
        return self.rows[self.current_row].is_individual_item()
   
    def reset_selection(self):
        self.current_row = 0
        self.current_column = 0

    def repeat_last_keystroke(self):
        actions.key(self.last_keystroke)

class KeyboardMenu:
    def __init__(self, keyboard: KeyBoard):
        self.keyboard = keyboard
        self.is_picking_row = True
   
    def pick_current_item(self):
        if self.keyboard.is_on_single_item_row():
            self.keyboard.pick_current_single_item_row()
        else:
            if self.is_picking_column():
                self.keyboard.pick_current_key()
            self.swap_picking_row_versus_column()

    def is_picking_column(self):
        return not self.is_picking_row

    def swap_picking_row_versus_column(self):
        self.is_picking_row = not self.is_picking_row
   
    def select_next_item(self, direction):
        if self.is_picking_row:
            self.keyboard.select_next_row(direction)
        else:
            self.keyboard.select_next_column(direction)
   
    def reset_selection(self):
        pass
   
    def get_items(self):
        if self.is_picking_row:
            return self.keyboard.get_current_row_items()
        return self.keyboard.get_current_column_items()
       
    def get_current_item_number(self):
        if self.is_picking_row:
            return self.keyboard.get_current_row()
        return self.keyboard.get_current_column()

def create_keyboard_menu(hissing_control):
    keyboard = KeyBoard()
    movement_keys = RowItem(
        [KeyBoardItem('right'), KeyBoardItem('down'), KeyBoardItem('up'), KeyBoardItem('left'), KeyBoardItem('end'), KeyBoardItem('home'), KeyBoardItem('pagedown', 'page down'),
         KeyBoardItem('pageup', 'page up')],
        'Movement'
    )
    modifier_keys = RowItem(
        [KeyBoardItem('ctrl', 'control'), KeyBoardItem('shift'), KeyBoardItem('alt'), KeyBoardItem('super')],
        'Modifiers'
    )
    a_f = create_single_character_row('abcdef')
    g_k = create_single_character_row('ghijk')
    l_p = create_single_character_row('lmnop')
    q_u = create_single_character_row('qrstu')
    v_z = create_single_character_row('vwxyz')
    punctuation = RowItem(
        [KeyBoardItem('.', 'period'), KeyBoardItem(',', 'comma'), KeyBoardItem('?', 'question mark'), KeyBoardItem('!', 'exclamation mark'),
         KeyBoardItem(':', 'colon'), KeyBoardItem(';', 'semicolon'), KeyBoardItem('"', 'double quote'), KeyBoardItem("'", 'quote'), KeyBoardItem('-', 'dash')],
        'punctuation'
    )
    editing_enter_tab_space = RowItem(
        [KeyBoardItem('space'), KeyBoardItem('enter'), KeyBoardItem('tab'), KeyBoardItem('escape'), KeyBoardItem('backspace'), KeyBoardItem('delete'), KeyBoardItem('end enter', 'end-enter')],
        'space enter tab escape editing'
    )
    symbols = create_single_character_row('+-=*/_@$%^#|()\\~`{}[]<>', 'symbols')
    digits = create_single_character_row('1234567890')

    def return_to_main_menu():
        hissing_control.update_current_menu('main')
        hissing_control.reset_mode()
    close_menu_item = MenuItem('close keyboard', return_to_main_menu)
    repeat_last_keystroke_item = MenuItem('repeat last keystroke', keyboard.repeat_last_keystroke)
   
    keyboard.set_rows([repeat_last_keystroke_item, modifier_keys, a_f, g_k, l_p, q_u, v_z, punctuation, digits, editing_enter_tab_space, movement_keys, symbols, close_menu_item])
    menu = KeyboardMenu(keyboard)
    return menu

def create_single_character_row(characters: str, name: str = ''):
    if name == '':
        name = characters
    items = [KeyBoardItem(character) for character in characters]
    result = RowItem(items, name)
    return result
