from talon import Module, Context, noise, actions, cron, scope, imgui, app
from enum import Enum
from .fire_chicken.mouse_position import MousePosition
from .mouse_position_manipulation import change_mouse_position_by, compute_mouse_position_with_direction_and_magnitude
from .direction_display import SingleLineDisplay
from .fire_chicken import tag_utilities
from .Dragging import MouseDragger
from .Menu import Menu
from .asynchronous_job_scheduling import AsynchronousJobHandler
from .keyboard import create_keyboard_menu
from typing import Union
import os

module = Module()
HISSING_CONTROL_TAG_BASE_NAME = 'fire_chicken_hissing_control'
module.tag(HISSING_CONTROL_TAG_BASE_NAME, desc = 'Enables the fire chicken hissing control')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_action_selection', desc = 'Active when hissing selects the next fire chicken hissing control action')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_direction_selection', desc = 'Active when hissing chooses the next fire chicken hissing control action direction')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_movement', desc = 'Active when hissing moves the mouse through the fire chicken hissing control')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_scrolling', desc = 'Active when hissing scrolls through the fire chicken hissing control')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_keyboard', desc = 'Active with the fire chicken hissing keyboard control')
HISSING_CONTROL_MODE_TAG_PREFIX = 'user.' + HISSING_CONTROL_TAG_BASE_NAME + '_'

hissing_mode_context = Context()
def update_hissing_mode_context(mode):
    global hissing_mode_context
    tag_utilities.make_tag_only_active_tag_in_context(mode, hissing_mode_context)

movement_amount = module.setting(
    'fire_chicken_hissing_control_movement_amount',
    type = int,
    default = 3,
    desc = 'How much to move the cursor during each time step with the fire chicken hissing control movement in pixels'
)

direction_change_amount = module.setting(
    'fire_chicken_hissing_control_direction_change_amount',
    type = float,
    default = 45.0,
    desc = 'How much to change the direction during each time step when changing the hissing control movement direction in degrees'
)

mouse_movement_delay = module.setting(
    'fire_chicken_hissing_control_mouse_movement_delay',
    type = int,
    default = 20,
    desc = 'How long to pause between individual mouse movements with the fire chicken hissing control in milliseconds'
)

direction_change_delay = module.setting(
    'fire_chicken_hissing_control_direction_changed_delay',
    type = int,
    default = 600,
    desc = 'How long to pause between individual changes in direction with the fire chicken hissing control in milliseconds'
)

direction_line_size = module.setting(
    'fire_chicken_hissing_control_direction_line_size',
    type = int,
    default = 400,
    desc = 'The size in pixels of the direction line of the fire chicken hissing control'
)

next_action_progress_needed = module.setting(
    'fire_chicken_hissing_control_next_action_progress_amount',
    type = int,
    default = 10,
    desc = 'How much progress towards the next action has to be accumulated before the hissing action changes to the next one. One gets obtained each time interval of hissing.'
)

next_action_progress_delay = module.setting(
    'fire_chicken_hissing_control_next_action_progress_delay',
    type = int,
    default = 100,
    desc = 'The amount of time one must hiss to gain 1 unit of progress towards the next hissing action.'
)

simulate_hiss_with_pop = module.setting(
    'fire_chicken_hissing_control_simulate_hiss_with_pop',
    type = int,
    default = 0,
    desc = 'When set to value other than zero, popping simulates hissing with the fire chicken hissing control'
)

pop_mouse_movement_delay = module.setting(
    'fire_chicken_hissing_mouse_pop_control_movement_delay',
    type = int,
    default = 10,
    desc = 'How long to pause between individual mouse movements with the fire chicken hissing control when movement is started with the popping sound'
)

vertical_scroll_amount = module.setting(
    'fire_chicken_hissing_control_vertical_scroll_amount',
    type = int,
    default = 50,
    desc = 'How quickly to scroll vertically with the fire chicken hissing control'
)

horizontal_scroll_amount = module.setting(
    'fire_chicken_hissing_control_horizontal_scroll_amount',
    type = int,
    default = 20,
    desc = 'How quickly to scroll horizontally with the fire chicken hissing control'
)

pop_vertical_scroll_amount = module.setting(
    'fire_chicken_hissing_control_pop_vertical_scroll_amount',
    type = int,
    default = 100,
    desc = 'How quickly to scroll vertically with the fire chicken hissing control with pop input'
)

pop_horizontal_scroll_amount = module.setting(
    'fire_chicken_hissing_control_pop_horizontal_scroll_amount',
    type = int,
    default = 40,
    desc = 'How quickly to scroll horizontally with the fire chicken hissing control with pop input'
)

pop_reverses_menu_direction = module.setting(
    'fire_chicken_hissing_control_pop_reverses_menu',
    type = int,
    default = 1,
    desc = 'When set to anything other than 0, popping interactions with menus have reversed direction'
)

pop_reverses_direction_during_direction_change = module.setting(
    'fire_chicken_hissing_control_pop_reverses_direction_during_direction_change',
    type = int,
    default = 1,
    desc = 'When set to anything other than 0, popping during direction selection reverses direction'
)

hissing_start_time = module.setting(
    'fire_chicken_hissing_control_hissing_start_time',
    type = int,
    default = 0,
    desc = 'How long you must hiss in milliseconds before you are considered to have start hissing. Increasing this can reduce false positive hiss recognition.'
)

hissing_start_during_movement_reverses_direction = module.setting(
    'fire_chicken_hissing_control_hissing_start_during_movement_reverses_direction',
    type = int,
    default = 1,
    desc = 'If nonzero, starting to hiss during mouse movement reverses the direction'
)

class OverrideValues:
    def __init__(self, should_increase_direction_on_direction_change = True, movement_delay_override = False, vertical_scrolling_speed_override = False, 
    horizontal_scrolling_speed_override = False, menu_direction_reversed = False):
        self.should_increase_direction_on_direction_change = should_increase_direction_on_direction_change
        self.movement_delay_override = movement_delay_override
        self.vertical_scrolling_speed_override = vertical_scrolling_speed_override
        self.horizontal_scrolling_speed_override = horizontal_scrolling_speed_override
        self.menu_direction_reversed = menu_direction_reversed

def should_simulate_hiss_with_pop():
    return simulate_hiss_with_pop.get() != 0

def compute_pop_override_values():
    values = OverrideValues(
        movement_delay_override = pop_mouse_movement_delay.get(),
        vertical_scrolling_speed_override = pop_vertical_scroll_amount.get(),
        horizontal_scrolling_speed_override = pop_horizontal_scroll_amount.get(),
        menu_direction_reversed = pop_reverses_menu_direction.get() != 0,
        should_increase_direction_on_direction_change = pop_reverses_direction_during_direction_change.get() == 0,
    )
    return values

def on_pop(active):
    if should_simulate_hiss_with_pop():
        pop_override_values = compute_pop_override_values()
        hissing_control.simulate_hissing_change(pop_override_values)

class DelayedHissingJobHandler:
    def __init__(self):
        self.job = None
        self.hiss_successfully_started = False
    
    def handled_delayed_hiss(self, active):
        if active:
            self.start_delayed_hiss()
        else:
            self.stop_delayed_hiss()
    
    def start_delayed_hiss(self):
        self.job = cron.after(f'{hissing_start_time.get()}ms', self.start_hiss_if_not_canceled)
        
    def start_hiss_if_not_canceled(self):
        actions.user.fire_chicken_simulate_hissing_change(True)
        self.hiss_successfully_started = True
        self.job = None
    
    def stop_delayed_hiss(self):
        self.cancel_job()
        if self.hiss_successfully_started:
            actions.user.fire_chicken_simulate_hissing_change(False)
            self.hiss_successfully_started = False
    
    def cancel_job(self):
        if self.job:
            cron.cancel(self.job)
        self.job = None

delayed_hissing_job_handler = DelayedHissingJobHandler()
def on_hiss(active):
    if hissing_control_enabled():
        if hissing_start_time.get() > 0:
            delayed_hissing_job_handler.handled_delayed_hiss(active)
        else:
            actions.user.fire_chicken_simulate_hissing_change(active)

def hissing_control_enabled():
    tags = scope.get("tag")
    return 'user.' + HISSING_CONTROL_TAG_BASE_NAME in tags

@module.action_class
class Actions:
    def fire_chicken_hissing_control_handle_hiss(active: bool):
        ''''''
        if hissing_start_during_movement_reverses_direction.get() != 0 and active and hissing_control.get_hissing_active() and hissing_control.get_mode() == HissingControlMode.MOVEMENT:
            hissing_control.simulate_hissing_change()
            direction_handler.reverse_direction()
            hissing_control.update_mode(HissingControlMode.MOVEMENT)
            hissing_control.simulate_hissing_change()
        else:
            hissing_control.simulate_hissing_change()
    
    def fire_chicken_simulate_hissing_change(active: Union[None, bool] = None):
        ''''''
        if active is None:
            hissing_control.simulate_hissing_change()
        else:
            actions.user.fire_chicken_hissing_control_handle_hiss(active)
    
    def fire_chicken_simulate_hissing_change_but_decrease_direction():
        ''''''
        hissing_control.simulate_hissing_change(OverrideValues(should_increase_direction_on_direction_change = False))

    def fire_chicken_simulate_hissing_change_with_overridden_movement_delay(movement_delay: int):
        ''''''
        hissing_control.simulate_hissing_change(OverrideValues(movement_delay_override = movement_delay))
    
    def fire_chicken_hissing_control_reverse_direction():
        ''''''
        direction_handler.reverse_direction()
        if hissing_control.get_mode() == HissingControlMode.DIRECTION_SELECTION:
            direction_handler.display_direction()
    
    def fire_chicken_hissing_control_stop_changing_direction():
        ''''''
        direction_handler.stop_changing_direction()
    
    def fire_chicken_hissing_control_change_direction_by(degrees: int):
        ''''''
        direction_handler.unlock_direction()
        direction_handler.change_direction_by(degrees)
        direction_handler.lock_direction()
    
    def fire_chicken_hissing_control_update_mode(mode: str):
        ''''''
        hissing_control.update_mode(HissingControlMode[mode])
    
    def fire_chicken_hissing_control_hide_display():
        ''''''
        direction_handler.hide_direction_display()
    
    def fire_chicken_hissing_control_pick_direction_and_move():
        ''''''
        hissing_control.update_mode(HissingControlMode.DIRECTION_SELECTION)
        direction_handler.display_direction()
    
    def fire_chicken_hissing_control_toggle_drag():
        ''''''
        mouse_dragger.toggle_drag()
    
    def fire_chicken_hissing_control_left_click():
        ''''''
        actions.mouse_click(0)
        mouse_dragger.stop_dragging()
    
    def fire_chicken_hissing_control_right_click():
        ''''''
        actions.mouse_click(1)
        mouse_dragger.stop_dragging()
    
    def fire_chicken_hissing_control_double_left_click():
        ''''''
        actions.mouse_click(0)
        actions.mouse_click(0)
        mouse_dragger.stop_dragging()
    
    def fire_chicken_hissing_control_activate_scrolling_menu():
        ''''''
        hissing_control.update_current_menu('scroll')
    
    def fire_chicken_hissing_control_activate_keyboard_menu():
        ''''''
        hissing_control.update_current_menu('keyboard')
        hissing_control.update_mode(HissingControlMode.KEYBOARD)
    
    def fire_chicken_hissing_control_left_click_if_hissing_active():
        ''''''
        if hissing_control.get_hissing_active():
            actions.user.fire_chicken_hissing_control_left_click()

mouse_dragger = MouseDragger()

def build_main_menu():
    menu = Menu()

    menu.add_item('Pick Direction and Move', actions.user.fire_chicken_hissing_control_pick_direction_and_move)
    menu.add_item('Left Click', actions.user.fire_chicken_hissing_control_left_click)
    menu.add_item('Right Click', actions.user.fire_chicken_hissing_control_right_click)
    menu.add_item('Double Click', actions.user.fire_chicken_hissing_control_double_left_click)
    menu.add_item('Toggle Holding Left Click Down', actions.user.fire_chicken_hissing_control_toggle_drag)
    menu.add_item('Scroll', actions.user.fire_chicken_hissing_control_activate_scrolling_menu)
    menu.add_item('Keyboard', actions.user.fire_chicken_hissing_control_activate_keyboard_menu)
    return menu

def build_scroll_menu(hissing_control):     
    menu = Menu()
    def buffer_scroll(vertical: int, horizontal: int):
        hissing_control.update_mode(HissingControlMode.SCROLLING)
        hissing_control.set_horizontal_and_vertical_scroll_amounts(vertical, horizontal)
    def scroll_up():
        buffer_scroll(-vertical_scroll_amount.get(), 0)
    def scroll_down():
        buffer_scroll(vertical_scroll_amount.get(), 0)
    def scroll_right():
        buffer_scroll(0, horizontal_scroll_amount.get())
    def scroll_left():
        buffer_scroll(0, -horizontal_scroll_amount.get())
    menu.add_item('Scroll Up', scroll_up)
    menu.add_item('Scroll Down', scroll_down)
    menu.add_item('Scroll Right', scroll_right)
    menu.add_item('Scroll Left', scroll_left)
    return menu

MAXIMUM_ANGLE = 360
SCROLLING_DELAY_IN_MILLISECONDS = 50

class DirectionHandler:
    def __init__(self):
        self.direction = 0
        self.direction_editable = False
        self.direction_display = DirectionDisplay()
        self.job_handler = AsynchronousJobHandler()

    def start_changing_direction(self, should_increase_direction_on_direction_change):
        self.display_direction()
        self.unlock_direction()
        if should_increase_direction_on_direction_change:
            self.start_increasing_direction()
        else:
            self.start_decreasing_direction()

    def lock_direction(self):
        self.direction_editable = False
    
    def unlock_direction(self):
        self.direction_editable = True

    def start_increasing_direction(self):
        def increase_direction():
            self.change_direction_by(direction_change_amount.get())
        self.job_handler.start_job(increase_direction, direction_change_delay.get())

    def start_decreasing_direction(self):
        def decrease_direction():
            self.change_direction_by(-direction_change_amount.get())
        self.job_handler.start_job(decrease_direction, direction_change_delay.get())

    def stop_changing_direction(self):
        self.lock_direction()
        self.job_handler.stop_job()
        self.hide_direction_display()
    
    def hide_direction_display(self):
        cron.after(f'{direction_change_delay.get()*2}ms', self.direction_display.hide)
    
    def get_direction(self):
        return self.direction
    
    def change_direction_by(self, change_in_direction: float):
        if self.direction_editable:
            self.direction += change_in_direction
            while self.direction > MAXIMUM_ANGLE:
                self.direction -= MAXIMUM_ANGLE
            self.display_direction()
    
    def reverse_direction(self):
        self.direction += 180

    def display_direction(self):
        self.direction_display.display_direction(self.direction)

class HissingControl:
    def __init__(self):
        self.reset_mode()
        self.vertical_scroll_amount = 0
        self.horizontal_scroll_amount = 0
        self.job_handler = AsynchronousJobHandler()
        self.progress_towards_next_action = 0
        self.hissing_active = False
        self.menus = {'main': build_main_menu(), 'scroll': build_scroll_menu(self), 'keyboard': create_keyboard_menu(self)}
        self.menu = self.menus['main']

    def reset_mode(self):
        self.update_mode(HissingControlMode.ACTION_SELECTION)

    def simulate_hissing_change(self, override_values: OverrideValues = OverrideValues()):
        if self.hissing_active:
            self.handle_hiss_ending()
        else:
            self.handle_hiss_start(override_values)

    def handle_hiss_start(self, override_values: OverrideValues = OverrideValues()):
        self.hissing_active = True
        if self.mode == HissingControlMode.DIRECTION_SELECTION:
            direction_handler.start_changing_direction(override_values.should_increase_direction_on_direction_change)
        elif self.mode == HissingControlMode.MOVEMENT:
            self.start_moving_mouse(override_values.movement_delay_override)
        elif self.should_select_action():
            self.start_increasing_progress_towards_next_action(override_values.menu_direction_reversed)
        elif self.mode == HissingControlMode.SCROLLING:
            self.start_scrolling(override_values.vertical_scrolling_speed_override, override_values.horizontal_scrolling_speed_override)

    def handle_hiss_ending(self):
        self.hissing_active = False
        if self.mode == HissingControlMode.DIRECTION_SELECTION:
            direction_handler.stop_changing_direction()
            self.update_mode(HissingControlMode.MOVEMENT)
        elif self.mode == HissingControlMode.MOVEMENT:
            self.stop_moving_mouse()
        elif self.should_select_action():
            self.stop_increasing_progress_towards_next_action()
        elif self.mode == HissingControlMode.SCROLLING:
            self.stop_scrolling()

    def should_select_action(self):
        return self.mode in [HissingControlMode.ACTION_SELECTION, HissingControlMode.KEYBOARD]

    def start_moving_mouse(self, movement_delay_override):
        delay_amount = mouse_movement_delay.get()
        if movement_delay_override:
            delay_amount = movement_delay_override
        def move_mouse():
            mouse_position_change: MousePosition = compute_mouse_position_with_direction_and_magnitude(direction_handler.get_direction(), movement_amount.get())
            change_mouse_position_by(mouse_position_change)
        self.job_handler.start_job(move_mouse, delay_amount)

    def stop_moving_mouse(self):
        self.job_handler.stop_job()
        self.reset_mode()
    
    def start_scrolling(self, vertical_scrolling_speed_override, horizontal_scrolling_speed_override):
        vertical_scroll_amount = self.vertical_scroll_amount
        horizontal_scroll_amount = self.horizontal_scroll_amount
        if vertical_scrolling_speed_override:
            vertical_scroll_amount = compute_scrolling_amount_override(vertical_scroll_amount, vertical_scrolling_speed_override)
        if horizontal_scrolling_speed_override:
            horizontal_scroll_amount = compute_scrolling_amount_override(horizontal_scroll_amount, horizontal_scrolling_speed_override)
        def scroll():
            actions.mouse_scroll(vertical_scroll_amount, horizontal_scroll_amount)
        self.job_handler.start_job(scroll, SCROLLING_DELAY_IN_MILLISECONDS)

    def set_horizontal_and_vertical_scroll_amounts(self, vertical: int, horizontal: int):
        self.vertical_scroll_amount = vertical
        self.horizontal_scroll_amount = horizontal

    def stop_scrolling(self):
        self.job_handler.stop_job()
        self.reset_mode()
        hissing_control.update_current_menu('main')

    def start_increasing_progress_towards_next_action(self, direction_reversed):
        def make_progress_towards_next_action():
            self.increase_progress_towards_next_action(direction_reversed)
        self.job_handler.start_job(make_progress_towards_next_action, next_action_progress_delay.get())
        gui.show()

    def stop_increasing_progress_towards_next_action(self):
        self.job_handler.stop_job()
        gui.hide()
        self.progress_towards_next_action = 0
        self.menu.pick_current_item()
        self.menu.reset_selection()

    def increase_progress_towards_next_action(self, direction_reversed):
        self.progress_towards_next_action += 1
        menu_change_value = 1
        if direction_reversed:
            menu_change_value = -1
        if self.progress_towards_next_action >= next_action_progress_needed.get():
            self.progress_towards_next_action = 0
            self.menu.select_next_item(menu_change_value)

    def update_mode(self, mode):
        self.mode = mode
        tag_name = HISSING_CONTROL_MODE_TAG_PREFIX + mode.name.lower()
        update_hissing_mode_context(tag_name)
    
    def update_current_menu(self, name: str):
        self.menu = self.menus[name]
    
    def get_menu(self):
        return self.menu
    
    def get_mode(self):
        return self.mode

    def get_hissing_active(self):
        return self.hissing_active


def compute_scrolling_amount_override(original: int, override: int):
    if abs(original) > 0:
        return override*compute_sign(original)
    return 0

def compute_sign(number):
    return number/abs(number)

class HissingControlMode(Enum):
    ACTION_SELECTION = 1
    DIRECTION_SELECTION = 2
    MOVEMENT = 3
    SCROLLING = 4
    KEYBOARD = 5

class DirectionDisplay:
    def __init__(self):
        self.display = SingleLineDisplay()
    
    def display_direction(self, direction: float): 
        current_position = MousePosition.current()
        change = compute_mouse_position_with_direction_and_magnitude(direction, movement_amount.get())
        scaled_change = change*direction_line_size.get()*(1/change.compute_magnitude())
        target_position = current_position + scaled_change
        self.display.display(current_position, target_position, current_position)
    
    def hide(self):
        self.display.hide()

direction_handler = DirectionHandler()
hissing_control = HissingControl()

@imgui.open()
def gui(gui: imgui.GUI):
    menu = hissing_control.get_menu()
    for index, item in enumerate(menu.get_items()):
        is_current_item = index == menu.get_current_item_number()
        if is_current_item:
            gui.line()
        gui.text(item.get_display_name())
        if is_current_item:
            gui.line()

CUSTOMIZATION_DIRECTORY = None
CUSTOM_MENU_DIRECTORY = None

def on_ready():
    global CUSTOMIZATION_DIRECTORY, CUSTOM_MENU_DIRECTORY
    CUSTOMIZATION_DIRECTORY = os.path.join(actions.path.talon_user(), 'Viper Settings')
    CUSTOM_MENU_DIRECTORY = os.path.join(CUSTOMIZATION_DIRECTORY, 'Custom Menus')
    noise.register("hiss", on_hiss)
    noise.register("pop", on_pop)
app.register("ready", on_ready)
