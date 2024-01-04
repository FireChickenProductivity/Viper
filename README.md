# Viper
Offers talon voice customization for hissing control.

Viper provides a hissing menu that opens by default when you hiss. The selected item on the menu advances as you keep hissing, and you choose the currently selected item and close the menu by stopping hissing. The default main menu is primarily geared towards mouse control.

Be aware that excessive use of hissing can harm your jaw. Also, using the direction changed graphical display while set to rotate rapidly may harm users susceptible to seizures triggered by visual stimulus.

## Pick Direction and Move
This menu option shows a line at the cursor pointing in the movement direction. Hissing from here will rotate the line until you stop. Hissing after that will then move the cursor in the desired direction. This offers a slow but sometimes useful way to move the cursor.

## Scroll
This opens a submenu for picking a scroll direction. Hissing after picking a direction will scroll in that direction. 

## Keyboard
This opens an experimental set of menus for operating the keyboard. This is a highly inefficient way to operate the keyboard. 

## Custom Menus
Viper will generate a directory called "Viper Settings" in your talon user directory. This will have a subdirectory called "Custom Menus". Custom menus may be defined here in CSV files. Every line defines a menu item. The first column gives the item name. If the second column consists of the word "stay", the menu will start at that item when selected the next time you open the hissing menu. The last column gives the action to perform when the item is selected. As a convenience, if the action is key or insert, you may put the key stroke or text to insert in this column by putting a space between the action and the keystroke/text. You may use a custom menu instead of the main menu by using the user.fire_chicken_hissing_control_main_menu_override setting.

Example custom menu for working with EquatIO and my custom EquatIO talon plugin:
```
Pick Direction and Move,user.fire_chicken_hissing_control_pick_direction_and_move
Left Click,user.fire_chicken_hissing_control_left_click
press right,stay,key right
implies,insert \Rightarrow 
equals,insert =
save math,user.equatio_insert_saved_word_math
Double Click,user.fire_chicken_hissing_control_double_left_click
Keyboard,user.fire_chicken_hissing_control_activate_keyboard_menu
```

Example override for the main menu:
```
Pick Direction and Move,user.fire_chicken_hissing_control_pick_direction_and_move
Left Click,user.fire_chicken_hissing_control_left_click
Right Click,user.fire_chicken_hissing_control_right_click
Double Click,user.fire_chicken_hissing_control_double_left_click
Toggle Holding Left Click Down,user.fire_chicken_hissing_control_toggle_drag
Scroll,stay,user.fire_chicken_hissing_control_activate_scrolling_menu
Keyboard,user.fire_chicken_hissing_control_activate_keyboard_menu
Hard Sleep,user.hard_sleep_enable
Repeat,stay,core.repeat_command
Focus,key alt-ctrl-tab
```

## Settings

user.fire_chicken_hissing_control_movement_amount has type int. How much to move the cursor during each time step with the fire chicken hissing control movement in pixels.

user.fire_chicken_hissing_control_direction_change_amount has type float. How much to change the direction during each time step when changing the hissing control movement direction in degrees.

user.fire_chicken_hissing_control_mouse_movement_delay has type int. How long to pause between individual mouse movements with the fire chicken hissing control in milliseconds.

user.fire_chicken_hissing_control_direction_changed_delay has type int. How long to pause between individual changes in direction with the fire chicken hissing control in milliseconds.

user.fire_chicken_hissing_control_direction_line_size has type int. The size in pixels of the direction line of the fire chicken hissing control.

user.fire_chicken_hissing_control_next_action_progress_amount has type int. How much progress towards the next action has to be accumulated before the hissing action changes to the next one. One.gets obtained each time interval of hissing.'

user.fire_chicken_hissing_control_next_action_progress_delay has type int. The amount of time one must hiss to gain 1 unit of progress towards the next hissing action..

user.fire_chicken_hissing_control_simulate_hiss_with_pop has type int. When set to value other than zero, popping simulates hissing with the fire chicken hissing control.

user.fire_chicken_hissing_mouse_pop_control_movement_delay has type int. How long to pause between individual mouse movements with the fire chicken hissing control when movement is started with the popping sound.

user.fire_chicken_hissing_control_vertical_scroll_amount has type int. How quickly to scroll vertically with the fire chicken hissing control.

user.fire_chicken_hissing_control_horizontal_scroll_amount has type int. How quickly to scroll horizontally with the fire chicken hissing control.

user.fire_chicken_hissing_control_pop_vertical_scroll_amount has type int. How quickly to scroll vertically with the fire chicken hissing control with pop input.

user.fire_chicken_hissing_control_pop_horizontal_scroll_amount has type int. How quickly to scroll horizontally with the fire chicken hissing control with pop input.

user.fire_chicken_hissing_control_pop_reverses_menu has type int. When set to anything other than 0, popping interactions with menus have reversed direction.

user.fire_chicken_hissing_control_pop_reverses_direction_during_direction_change has type int. When set to anything other than 0, popping during direction selection reverses direction.

user.fire_chicken_hissing_control_hissing_start_time has type int. How long you must hiss in milliseconds before you are considered to have start hissing. Increasing this can reduce false.positive hiss recognition.

user.fire_chicken_hissing_control_hissing_start_during_movement_reverses_direction has type int. If nonzero, starting to hiss during mouse movement reverses the direction. If you use another noise to start the movement, you could then use this to switch direction. A useful strategy is to have the cursor move relatively quickly when you start moving and then use hissing to reverse the direction but move at a slower pace so that the hissing can be used to achieve precision while the initial movement would quickly get you in the right area.

user.fire_chicken_hissing_control_main_menu_override has type str. When not the empty string, overrides the main menu with the specified custom menu.

user.fire_chicken_hissing_control_use_literal_hiss_handler has type int. If nonzero, the actual hissing handler is used.

## Credit
The display code for the direction line was heavily based on the knausj_talon configuration. Proper credit and a copy of the knausj_talon license is available in the direction_display.py file.

Thank you to GitHub user whatIV for contributing to this project.