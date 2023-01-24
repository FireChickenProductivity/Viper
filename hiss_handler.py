from talon import Module, Context, noise, actions, cron, scope, imgui, app
from enum import Enum
from .fire_chicken.mouse_position import MousePosition
import math
from .direction_display import SingleLineDisplay
from .fire_chicken import tag_utilities
from .Dragging import MouseDragger
from .Menu import Menu

module = Module()
HISSING_CONTROL_TAG_BASE_NAME = 'fire_chicken_hissing_control'
module.tag(HISSING_CONTROL_TAG_BASE_NAME, desc = 'Enables the fire chicken hissing control')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_action_selection', desc = 'Active when hissing selects the next fire chicken hissing control action')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_direction_selection', desc = 'Active when hissing chooses the next fire chicken hissing control action direction')
module.tag(HISSING_CONTROL_TAG_BASE_NAME + '_movement', desc = 'Active when hissing moves the mouse through the fire chicken hissing control')
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
    default = 15.0,
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
    default = 200,
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

def should_simulate_hiss_with_pop():
    return simulate_hiss_with_pop.get() != 0

def on_pop(active):
    if should_simulate_hiss_with_pop():
        actions.user.fire_chicken_simulate_hissing_change_with_overridden_movement_delay(pop_mouse_movement_delay.get())

def on_hiss(active):
    if hissing_control_enabled():
        actions.user.fire_chicken_simulate_hissing_change()

def hissing_control_enabled():
    tags = scope.get("tag")
    return 'user.' + HISSING_CONTROL_TAG_BASE_NAME in tags

@module.action_class
class Actions:
    def fire_chicken_hissing_control_handle_hiss(active: bool):
        ''''''
        if active:
            hissing_control.handle_hiss_start()
        else:
            hissing_control.handle_hiss_ending()
    
    def fire_chicken_simulate_hissing_change():
        ''''''
        hissing_control.simulate_hissing_change()
    
    def fire_chicken_simulate_hissing_change_but_decrease_direction():
        ''''''
        hissing_control.simulate_hissing_change(should_increase_direction_on_direction_change = False)

    def fire_chicken_simulate_hissing_change_with_overridden_movement_delay(movement_delay: int):
        ''''''
        hissing_control.simulate_hissing_change(movement_delay_override = movement_delay)

mouse_dragger = MouseDragger()

def build_main_menu(hissing_control):
    menu = Menu()
    def pick_direction_and_move():
        hissing_control.update_mode(HissingControlMode.DIRECTION_SELECTION)
    def left_click():
        actions.mouse_click(0)
        mouse_dragger.stop_dragging()
    def right_click():
        actions.mouse_click(1)
        mouse_dragger.stop_dragging()
    def double_left_click():
        actions.mouse_click(0)
        actions.mouse_click(0)
        mouse_dragger.stop_dragging()
    def toggle_drag():
        mouse_dragger.toggle_drag()
    menu.add_item('Pick Direction and Move', pick_direction_and_move)
    menu.add_item('Left Click', left_click)
    menu.add_item('Right Click', right_click)
    menu.add_item('Double Click', double_left_click)
    menu.add_item('Toggle Holding Left Click Down', toggle_drag)
    return menu

MAXIMUM_ANGLE = 360

class HissingControl:
    def __init__(self):
        self.reset_mode()
        self.direction = 0
        self.job = None
        self.direction_display = DirectionDisplay()
        self.mouse_dragger = MouseDragger()
        self.progress_towards_next_action = 0
        self.hissing_active = False
        self.menu = build_main_menu(self)

    def reset_mode(self):
        self.update_mode(HissingControlMode.ACTION_SELECTION)

    def simulate_hissing_change(self, should_increase_direction_on_direction_change = True, movement_delay_override = False):
        if self.hissing_active:
            self.handle_hiss_ending()
        else:
            self.handle_hiss_start(should_increase_direction_on_direction_change, movement_delay_override)

    def handle_hiss_start(self, should_increase_direction_on_direction_change, movement_delay_override):
        self.hissing_active = True
        if self.mode == HissingControlMode.DIRECTION_SELECTION:
            self.start_changing_direction(should_increase_direction_on_direction_change)
        elif self.mode == HissingControlMode.MOVEMENT:
            self.start_moving_mouse(movement_delay_override)
        elif self.mode == HissingControlMode.ACTION_SELECTION:
            self.start_increasing_progress_towards_next_action()

    def handle_hiss_ending(self):
        self.hissing_active = False
        if self.mode == HissingControlMode.DIRECTION_SELECTION:
            self.stop_changing_direction()
        elif self.mode == HissingControlMode.MOVEMENT:
            self.stop_moving_mouse()
        elif self.mode == HissingControlMode.ACTION_SELECTION:
            self.stop_increasing_progress_towards_next_action()

    def start_moving_mouse(self, movement_delay_override):
        delay_amount = mouse_movement_delay.get()
        if movement_delay_override:
            delay_amount = movement_delay_override
        self.start_asynchronous_job(move_mouse, delay_amount)

    def stop_moving_mouse(self):
        self.stop_asynchronous_job()
        self.reset_mode()

    def start_changing_direction(self, should_increase_direction_on_direction_change):
        if should_increase_direction_on_direction_change:
            self.start_increasing_direction()
        else:
            self.start_decreasing_direction()

    def start_increasing_direction(self):
        self.start_asynchronous_job(increase_direction, direction_change_delay.get())
    
    def start_decreasing_direction(self):
        self.start_asynchronous_job(decrease_direction, direction_change_delay.get())

    def stop_changing_direction(self):
        self.stop_asynchronous_job()
        self.update_mode(HissingControlMode.MOVEMENT)
        cron.after(f'{direction_change_delay.get()*2}ms', self.direction_display.hide)

    def start_increasing_progress_towards_next_action(self):
        self.start_asynchronous_job(make_progress_towards_next_action, next_action_progress_delay.get())
        gui.show()

    def stop_increasing_progress_towards_next_action(self):
        self.stop_asynchronous_job()
        gui.hide()
        self.progress_towards_next_action = 0
        self.menu.pick_current_item()
        self.menu.reset_selection()

    def increase_progress_towards_next_action(self):
        self.progress_towards_next_action += 1
        if self.progress_towards_next_action >= next_action_progress_needed.get():
            self.progress_towards_next_action = 0
            self.menu.select_next_item()

    def update_mode(self, mode):
        self.mode = mode
        tag_name = HISSING_CONTROL_MODE_TAG_PREFIX + mode.name.lower()
        update_hissing_mode_context(tag_name)
    
    def stop_asynchronous_job(self):
        if self.job:
            cron.cancel(self.job)
        self.job = None
    
    def start_asynchronous_job(self, job_function, time_between_calls_in_milliseconds: int):
        self.job = cron.interval(f'{time_between_calls_in_milliseconds}ms', job_function)
    
    def get_direction(self):
        return self.direction
    
    def get_menu(self):
        return self.menu
    
    def change_direction_by(self, change_in_direction: float):
        self.direction += change_in_direction
        while self.direction > MAXIMUM_ANGLE:
            self.direction -= MAXIMUM_ANGLE
        self.direction_display.display_direction(self.direction)

class HissingControlMode(Enum):
    ACTION_SELECTION = 1
    DIRECTION_SELECTION = 2
    MOVEMENT = 3

class DirectionDisplay:
    def __init__(self):
        self.display = SingleLineDisplay()
    
    def display_direction(self, direction: float): 
        current_position = MousePosition.current()
        change = compute_mouse_position_with_direction_and_magnitude(direction, direction_line_size.get())
        target_position = current_position + change
        self.display.display(current_position, target_position, current_position)
    
    def hide(self):
        self.display.hide()

hissing_control = HissingControl()

def make_progress_towards_next_action():
    hissing_control.increase_progress_towards_next_action()

def increase_direction():
    hissing_control.change_direction_by(direction_change_amount.get())

def decrease_direction():
    hissing_control.change_direction_by(-direction_change_amount.get())

def move_mouse():
    mouse_position_change: MousePosition = compute_mouse_position_with_direction_and_magnitude(hissing_control.get_direction(), movement_amount.get())
    change_mouse_position_by(mouse_position_change)

def compute_mouse_position_with_direction_and_magnitude(direction: float, magnitude: int):
    direction_in_radians = direction*math.pi/180
    horizontal = magnitude*math.cos(direction_in_radians)
    vertical = -magnitude*math.sin(direction_in_radians)
    position = MousePosition(horizontal, vertical)
    return position

def change_mouse_position_by(change: MousePosition):
    new_position: MousePosition = MousePosition.current() + change
    new_position.go()

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

def on_ready():
    noise.register("hiss", on_hiss)
    noise.register("pop", on_pop)
app.register("ready", on_ready)