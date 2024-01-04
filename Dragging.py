from talon import ctrl

class MouseDragger:
    def __init__(self):
        self.is_dragging = False
    
    def toggle_drag(self):
        if self.is_dragging:
            self.stop_dragging()
        else:
            self.start_dragging()
    
    def start_dragging(self):
        ctrl.mouse_click(button=0, down=True)
        self.is_dragging = True
    
    def stop_dragging(self):
        ctrl.mouse_click(button=0, up=True)
        self.is_dragging = False