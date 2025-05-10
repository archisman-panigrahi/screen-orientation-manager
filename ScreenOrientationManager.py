import gi
import subprocess
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
script_dir = os.path.dirname(__file__)

class ScreenOrientationManager(Gtk.Window):

    def __init__(self):

        # init
        margin = 20
        devices = self.popcache()

        # window
        Gtk.Window.__init__(self, title="Screen Orientation Manager")

        # layout
        self.grid = Gtk.Grid()
        self.grid.props.margin_top = margin
        self.grid.props.margin_left = margin
        self.grid.props.margin_bottom = margin
        self.grid.props.margin_right = margin
        self.add(self.grid)

        # [0] add instruction label
        self.touchscreen_hint = Gtk.Label(label="Use `xinput list` to find your")
        self.touchscreen_hint2 = Gtk.Label(label="touchscreen id and enter it below.")
        self.touchscreen_hint2.props.margin_bottom = 5
        self.grid.attach(self.touchscreen_hint, 1, 1, 50, 1)
        self.grid.attach(self.touchscreen_hint2, 1, 2, 50, 1)

        # [1] add screen entry
        self.screen_entry = Gtk.Entry()
        self.screen_entry.set_placeholder_text("e.g. ELAN Touchscreen")
        if len(devices[1]) != 0:
            self.screen_entry.set_text(devices[1])
        self.grid.attach(self.screen_entry, 1, 3, 50, 1)

        # [2] add touchpad entry
        self.touchpad_entry = Gtk.Entry()
        self.touchpad_entry.props.margin_top = margin
        self.touchpad_entry.set_placeholder_text("e.g. ELAN Touchpad")
        if len(devices[0]) != 0:
            self.touchpad_entry.set_text(devices[0])
        #self.grid.attach(self.touchpad_entry, 1, 4, 50, 1)

        # [3] add check button
        self.display_check = Gtk.CheckButton(label="Lock touchscreen id")
        #self.display_check.props.margin_top = margin
        if len(devices[3]) != 0:
            self.display_check.set_active(bool(devices[3]))
        self.display_check.connect("clicked", self.on_check_changed)
        self.grid.attach(self.display_check, 1, 5, 1, 1)

        # [4] add display entry
        self.display_entry = Gtk.Entry()
        self.display_entry.props.margin_top = margin
        self.display_entry.set_placeholder_text("e.g. Video Bus")
        if len(devices[2]) != 0:
            self.display_entry.set_text(devices[2])
        #self.grid.attach(self.display_entry, 1, 6, 50, 1)
        self.display_entry.set_sensitive(False)

        # [5] button layout
        self.buttons_grid = Gtk.Grid()
        self.buttons_grid.props.margin_top = margin
        self.grid.attach(self.buttons_grid, 1, 7, 1, 1)

        # [1] add buttons
        left = self.create_button(self.buttons_grid, "Left", None)
        normal = self.create_button(self.buttons_grid, "Normal", left)
        right = self.create_button(self.buttons_grid, "Right", normal)
        invert = self.create_button(self.buttons_grid, "Invert", right)

        '''
        # [7] help button layout
        self.help_button_grid = Gtk.Grid()
        self.help_button_grid.props.margin_top = margin
        self.grid.attach(self.help_button_grid, 1, 7, 1, 1)
        '''
        # Restart Twofing Button
        restart_twofing = self.create_restart_twofing_button(self.buttons_grid, "Restart Twofing", None)
        # [1] help button
        #help = self.create_help_button(self.buttons_grid, "Help", None)

        # finally
        self.on_check_changed(self.display_check)
        proc = subprocess.Popen(['bash', os.path.join(script_dir,'bin/twofing.sh')], stdout=subprocess.PIPE)#.wait()

    def create_button(self, grid, label, sibling):
        button = Gtk.Button(label=label)
        button.connect("clicked", self.on_click)
        margin = 20
        if sibling is None:
            grid.attach(button, 1, 1, 1, 1)
        else:
            button.props.margin_left = margin
            grid.attach_next_to(button, sibling, Gtk.PositionType.RIGHT, 1, 1)
        return button

    def create_restart_twofing_button(self, grid, label, sibling):
        button = Gtk.Button(label=label)
        button.connect("clicked", self.on_click)
        margin = 20
        button.props.margin_top = margin
        button.props.margin_left = margin
        grid.attach(button, 2, 2, 2, 1)
        return button

    def on_click(self, widget):

        label = str(widget.get_label())
        print(label)
        if label== "Restart Twofing":
            proc = subprocess.Popen(['bash', os.path.join(script_dir,'bin/twofing.sh')], stdout=subprocess.PIPE)#.wait()
            print("done restarting")
        else:
            self.encache(self.touchpad_entry.get_text(), self.screen_entry.get_text(), self.display_entry.get_text(),
                         str(self.display_check.get_active()))
            if label.lower() == "left":
                self.rotate("l")
            elif label.lower() == "normal":
                self.rotate("n")
            elif label.lower() == "right":
                self.rotate("r")
            elif label.lower() == "invert":
                self.rotate("i")
        #else:
            #self.create_message_dialog("Manual", "1. Run xinput\n2. Note down your touchscreen and touchpad names\n"
            #                                     "3. If you don't have a touchscreen, check the box\n4. In case of "
            #                                     "#3, run xrandr\n5. In case of #4, note down your display name")
        
    def on_check_changed(self, widget):
        if widget.get_active() is True:
            self.screen_entry.set_sensitive(False)
            self.display_entry.set_sensitive(True)
        else:
            self.screen_entry.set_sensitive(True)
            self.display_entry.set_sensitive(False)

    def create_message_dialog(self, title, message):
        message_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, title)
        message_dialog.format_secondary_text(message)
        message_dialog.run()
        message_dialog.destroy()

    def rotate(self, rotation):
        proc = subprocess.Popen(['sh', os.path.join(script_dir,'bin/' + rotation + '.sh'), self.touchpad_entry.get_text(), self.screen_entry.get_text(), self.display_entry.get_text()], stdout=subprocess.PIPE).wait()

    def encache(self, touchpad, touchscreen, display, checked):
        with open(os.path.join(script_dir,'bin/config.txt'), 'w') as file:
            file.write(touchpad + "\n" + touchscreen + "\n" + display + "\n" + checked)

    def popcache(self):
        devices = []
        with open(os.path.join(script_dir,'bin/config.txt'), 'r') as file:
            devices = [file.readline().strip(), file.readline().strip(), file.readline().strip(), file.readline().strip()]
        return devices


win = ScreenOrientationManager()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
