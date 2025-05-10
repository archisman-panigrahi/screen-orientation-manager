import gi
import subprocess
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
script_dir = os.path.dirname(__file__)

# Use config file in user's home directory
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".config", "screen-orientation-manager.conf")

# Create config file with defaults if it does not exist
if not os.path.exists(CONFIG_PATH):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        f.write("Elan Touchpad\nhid-over-i2c 06CB:7817\n\nTrue\n")

class ScreenOrientationManager(Gtk.Window):

    def __init__(self):

        # init
        margin = 20
        devices = self.popcache()

        # window
        Gtk.Window.__init__(self, title="Screen Orientation Manager for X11")
        self.set_icon_name("screen-orientation-manager")

        # --- Menu Bar ---
        menubar = Gtk.MenuBar()

        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        file_menu.append(quit_item)

        # Help menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)

        about_item = Gtk.MenuItem(label="About")
        about_item.connect("activate", self.on_credits_clicked)
        help_menu.append(about_item)

        menubar.append(file_item)
        menubar.append(help_item)

        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.pack_start(menubar, False, False, 0)

        # layout
        self.grid = Gtk.Grid()
        self.grid.props.margin_top = margin
        self.grid.props.margin_left = margin
        self.grid.props.margin_bottom = margin
        self.grid.props.margin_right = margin
        vbox.pack_start(self.grid, True, True, 0)
        self.add(vbox)

        # [0] add instruction label
        self.touchscreen_hint = Gtk.Label(label="Use `xinput list` to find your touchpad id")
        self.touchscreen_hint2 = Gtk.Label(label="and touchscreen id and enter it below.")
        self.touchscreen_hint2.props.margin_bottom = 5
        self.grid.attach(self.touchscreen_hint, 0, 1, 50, 1)
        self.grid.attach(self.touchscreen_hint2, 0, 2, 50, 1)

        # [1] add screen entry
        self.screen_label = Gtk.Label(label="Touchscreen ID")
        self.screen_label.props.margin_right = 10
        self.screen_label.set_valign(Gtk.Align.CENTER)
        self.grid.attach(self.screen_label, 0, 3, 1, 1)
        self.screen_entry = Gtk.Entry()
        self.screen_entry.set_placeholder_text("e.g. hid-over-i2c 06CB:7817")
        if len(devices[1]) != 0:
            self.screen_entry.set_text(devices[1])
        self.grid.attach(self.screen_entry, 1, 3, 50, 1)

        # [2] add touchpad entry
        self.touchpad_label = Gtk.Label(label="Touchpad ID")
        self.touchpad_label.props.margin_right = 10
        self.touchpad_label.set_valign(Gtk.Align.CENTER)
        self.grid.attach(self.touchpad_label, 0, 4, 1, 1)
        self.touchpad_entry = Gtk.Entry()
        self.touchpad_entry.props.margin_top = margin
        self.touchpad_entry.set_placeholder_text("e.g. ELAN Touchpad")
        if len(devices[0]) != 0:
            self.touchpad_entry.set_text(devices[0])
        self.grid.attach(self.touchpad_entry, 1, 4, 50, 1)

        # [3] add check button
        self.display_check = Gtk.CheckButton(label="Lock Touchscreen and Touchpad ID to save")
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

        # Remove About button and credits_grid setup
        # (Delete or comment out the following lines:)
        # self.credits_grid = Gtk.Grid()
        # self.credits_grid.props.margin_top = margin
        # self.grid.attach(self.credits_grid, 1, 8, 50, 1)
        # credits = Gtk.Button(label="About")
        # credits.connect("clicked", self.on_credits_clicked)
        # self.credits_grid.attach(credits, 25, 0, 1, 1)

        # finally
        self.on_check_changed(self.display_check)

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

    def create_credits_button(self, grid, label, sibling):
        button = Gtk.Button(label=label)
        button.props.margin_left = 20
        button.connect("clicked", self.on_credits_clicked)
        grid.attach_next_to(button, sibling, Gtk.PositionType.RIGHT, 1, 1)
        return button

    def on_credits_clicked(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True)
        about.set_program_name("Screen Orientation Manager for X11")
        about.set_version("1.0")
        about.set_comments(
            "This program allows you to rotate the\n"
            "touchscreen input, display and touchpad\n"
            "input of your laptop or tablet running X11.\n"
        )
        about.set_website("https://github.com/archisman-panigrahi/surface-RT-screen-rotator/tree/screen-orientation-manager")
        about.set_website_label("Homepage")
        about.set_authors([
            "Archisman Panigrahi (@archisman-panigrahi)",
            "Based on work by Ruben Barkow (@rubo77)",
            "and Rahul Pillai (@theGeekyLad)"
        ])
        about.set_artists([
            "Archisman Panigrahi and @GuLinux"
        ])
        about.set_logo_icon_name("screen-orientation-manager")
        about.run()
        about.destroy()

    def on_click(self, widget):

        label = str(widget.get_label())
        print(label)
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
        
    def on_check_changed(self, widget):
        if widget.get_active() is True:
            self.screen_entry.set_sensitive(False)
            self.touchpad_entry.set_sensitive(False)
            self.display_entry.set_sensitive(True)
        else:
            self.screen_entry.set_sensitive(True)
            self.touchpad_entry.set_sensitive(True)
            self.display_entry.set_sensitive(False)

    def create_message_dialog(self, title, message):
        message_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, title)
        message_dialog.format_secondary_text(message)
        message_dialog.run()
        message_dialog.destroy()

    def rotate(self, rotation):
        proc = subprocess.Popen(['sh', os.path.join(script_dir,'rotation-scripts/' + rotation + '.sh'), self.touchpad_entry.get_text(), self.screen_entry.get_text(), self.display_entry.get_text()], stdout=subprocess.PIPE).wait()

    def encache(self, touchpad, touchscreen, display, checked):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as file:
            file.write(touchpad + "\n" + touchscreen + "\n" + display + "\n" + checked)

    def popcache(self):
        devices = ["", "", "", ""]
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                lines = file.readlines()
                for i in range(min(4, len(lines))):
                    devices[i] = lines[i].strip()
        return devices

    def on_window_close(self, *args):
        self.encache(
            self.touchpad_entry.get_text(),
            self.screen_entry.get_text(),
            self.display_entry.get_text(),
            str(self.display_check.get_active())
        )
        return False  # Allow the window to close

    def on_quit(self, widget):
        self.on_window_close()  # Save config before quitting
        Gtk.main_quit()


win = ScreenOrientationManager()
win.connect("delete-event", win.on_window_close)  # Save config before closing
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
