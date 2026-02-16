import gi
import subprocess
import os
import re
import argparse
import sys

gi.require_version('Gtk', '3.0')

# Try to import AyatanaAppIndicator3, set a flag if available
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3
    HAS_APPINDICATOR = True
except (ImportError, ValueError):
    print("AyatanaAppIndicator3 not found, running without system tray icon.")
    HAS_APPINDICATOR = False

from gi.repository import Gtk, GObject
script_dir = os.path.dirname(__file__)


# Determine config path in a Flatpak-friendly way
def get_config_path():
    # Prefer XDG_CONFIG_HOME if set, else fallback to ~/.config
    config_home = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
    # If running in Flatpak, $HOME is sandboxed, so this will be .var/app/<app-id>/config
    return os.path.join(config_home, "screen-orientation-manager.conf")

CONFIG_PATH = get_config_path()

# Create config file with defaults if it does not exist
if not os.path.exists(CONFIG_PATH):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        f.write("Elan Touchpad\nhid-over-i2c 06CB:7817\n\n\nTrue\n")

class ScreenOrientationManager(Gtk.Window):

    def __init__(self):

        # init
        margin = 20
        devices = self.popcache()

        # window
        Gtk.Window.__init__(self, title="Screen Orientation Manager for X11")
        self.set_icon_name("io.github.archisman_panigrahi.screen-orientation-manager")

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

        # Attach the autodetect button at the very top (row 0)
        self.autodetect_button = Gtk.Button(label="Autodetect")
        self.autodetect_button.get_style_context().add_class("autodetect-btn")  # Add this line
        self.autodetect_button.connect("clicked", self.on_autodetect_clicked)
        self.grid.attach(self.autodetect_button, 1, 0, 1, 1)

        # [0] add instruction label
        self.touchscreen_hint = Gtk.Label(label="If autodetect does not work, run `xinput list`")
        self.touchscreen_hint2 = Gtk.Label(label="to find your touchpad, touchscreen, and stylus id")
        self.touchscreen_hint3 = Gtk.Label(label="and enter them below (stylus optional).")
        self.touchscreen_hint2.props.margin_bottom = 0  # Remove margin from line 2
        self.touchscreen_hint3.props.margin_bottom = 15  # Add space after instructions
        self.grid.attach(self.touchscreen_hint, 0, 1, 50, 1)
        self.grid.attach(self.touchscreen_hint2, 0, 2, 50, 1)
        self.grid.attach(self.touchscreen_hint3, 0, 3, 50, 1)

        # [1] add screen entry
        self.screen_label = Gtk.Label(label="Touchscreen ID")
        self.screen_label.props.margin_right = 10
        self.screen_label.set_valign(Gtk.Align.CENTER)
        self.grid.attach(self.screen_label, 0, 4, 1, 1)
        self.screen_entry = Gtk.Entry()
        self.screen_entry.set_placeholder_text("e.g. hid-over-i2c 06CB:7817")
        if len(devices[1]) != 0:
            self.screen_entry.set_text(devices[1])
        self.grid.attach(self.screen_entry, 1, 4, 50, 1)

        # [1.5] add stylus entry
        self.stylus_label = Gtk.Label(label="Stylus ID")
        self.stylus_label.props.margin_right = 10
        self.stylus_label.set_valign(Gtk.Align.CENTER)
        self.grid.attach(self.stylus_label, 0, 5, 1, 1)
        self.stylus_entry = Gtk.Entry()
        self.stylus_entry.set_placeholder_text("Keep this blank if no stylus is present")
        if len(devices) > 4 and len(devices[4]) != 0:
            self.stylus_entry.set_text(devices[4])
        self.grid.attach(self.stylus_entry, 1, 5, 50, 1)

        # [2] add touchpad entry (move down by 1 row)
        self.touchpad_label = Gtk.Label(label="Touchpad ID")
        self.touchpad_label.props.margin_right = 10
        self.touchpad_label.set_valign(Gtk.Align.CENTER)
        self.grid.attach(self.touchpad_label, 0, 6, 1, 1)
        self.touchpad_entry = Gtk.Entry()
        self.touchpad_entry.props.margin_top = margin
        self.touchpad_entry.set_placeholder_text("e.g. ELAN Touchpad")
        if len(devices[0]) != 0:
            self.touchpad_entry.set_text(devices[0])
        self.grid.attach(self.touchpad_entry, 1, 6, 50, 1)

        # [3] add check button (move down by 1 row)
        self.display_check = Gtk.CheckButton(label="Lock Touchscreen, Touchpad, and Stylus ID to save")
        if len(devices) > 3 and len(devices[3]) != 0:
            self.display_check.set_active(bool(devices[3]))
        self.display_check.connect("clicked", self.on_check_changed)
        self.grid.attach(self.display_check, 1, 7, 1, 1)

        # [4] add display entry (move down by 1 row)
        self.display_entry = Gtk.Entry()
        self.display_entry.props.margin_top = margin
        self.display_entry.set_placeholder_text("e.g. Video Bus")
        if len(devices[2]) != 0:
            self.display_entry.set_text(devices[2])
        self.display_entry.set_sensitive(False)

        # [5] button layout (move down by 1 row)
        self.buttons_grid = Gtk.Grid()
        self.buttons_grid.props.margin_top = margin
        self.grid.attach(self.buttons_grid, 1, 9, 1, 1)

        # [1] add buttons with style names
        left = self.create_button(self.buttons_grid, "Left", None, "left-btn")
        normal = self.create_button(self.buttons_grid, "Normal", left, "normal-btn")
        right = self.create_button(self.buttons_grid, "Right", normal, "right-btn")
        invert = self.create_button(self.buttons_grid, "Invert", right, "invert-btn")

        # Add CSS for button colors
        css = b"""
        .left-btn { background: #2196F3; color: white; }
        .normal-btn { background: #4CAF50; color: white; }
        .right-btn { background: #FF9800; color: white; }
        .invert-btn { background: #F44336; color: white; }
        .autodetect-btn { background: #009688; color: white; }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gtk.Window.get_screen(self),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Add Ayatana AppIndicator (system tray icon) if available
        if HAS_APPINDICATOR:
            self.indicator = AyatanaAppIndicator3.Indicator.new(
                "io.github.archisman_panigrahi.screen-orientation-manager",
                "io.github.archisman_panigrahi.screen-orientation-manager",  # icon name, or use a path to an icon file
                AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_menu(self.build_tray_menu())
        else:
            self.indicator = None

        # finally
        self.on_check_changed(self.display_check)

        # Attach the buttons grid at row 8
        self.grid.attach(self.buttons_grid, 1, 9, 1, 1)

    def create_button(self, grid, label, sibling, style_name=None):
        button = Gtk.Button(label=label)
        button.connect("clicked", self.on_click)
        if style_name:
            button.get_style_context().add_class(style_name)
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
        about.set_version("1.5.3")
        about.set_comments(
            "This program allows you to rotate the touchscreen,\n"
            "display, touchpad and stylus orientation of\n"
            "your convertible laptop or tablet running X11.\n"
        )
        about.set_website("https://github.com/archisman-panigrahi/screen-orientation-manager")
        about.set_website_label("Homepage")
        about.set_authors([
            "Archisman Panigrahi (@archisman-panigrahi)",
            "Based on work by Ruben Barkow (@rubo77)",
            "and Rahul Pillai (@theGeekyLad)"
        ])
        about.set_artists([
            "Archisman Panigrahi and @GuLinux"
        ])
        about.set_logo_icon_name("io.github.archisman_panigrahi.screen-orientation-manager")
        about.run()
        about.destroy()

    def on_click(self, widget):
        label = str(widget.get_label())
        print(label)
        self.encache(
            self.touchpad_entry.get_text(),
            self.screen_entry.get_text(),
            self.display_entry.get_text(),
            str(self.display_check.get_active()),
            self.stylus_entry.get_text()
        )
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
            self.stylus_entry.set_sensitive(False)
            self.display_entry.set_sensitive(True)
        else:
            self.screen_entry.set_sensitive(True)
            self.touchpad_entry.set_sensitive(True)
            self.stylus_entry.set_sensitive(True)
            self.display_entry.set_sensitive(False)

    def create_message_dialog(self, title, message):
        message_dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        message_dialog.format_secondary_text(message)
        # Make secondary text selectable
        for child in message_dialog.get_message_area().get_children():
            if isinstance(child, Gtk.Label):
                child.set_selectable(True)
        message_dialog.run()
        message_dialog.destroy()

    def rotate(self, rotation):
        proc = subprocess.Popen(['sh', os.path.join(script_dir,'rotation-scripts/' + rotation + '.sh'), self.touchpad_entry.get_text(), self.screen_entry.get_text(), self.display_entry.get_text(), self.stylus_entry.get_text()], stdout=subprocess.PIPE).wait()

    def encache(self, touchpad, touchscreen, display, checked, stylus=""):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as file:
            file.write(
                touchpad + "\n" +
                touchscreen + "\n" +
                display + "\n" +
                checked + "\n" +
                stylus + "\n"
            )

    def popcache(self):
        devices = ["", "", "", "", ""]
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                lines = file.readlines()
                for i in range(min(5, len(lines))):
                    devices[i] = lines[i].strip()
        return devices

    def on_window_close(self, *args):
        self.encache(
            self.touchpad_entry.get_text(),
            self.screen_entry.get_text(),
            self.display_entry.get_text(),
            str(self.display_check.get_active()),
            self.stylus_entry.get_text()
        )
        # If tray is available, hide window instead of quitting
        if hasattr(self, 'indicator') and self.indicator is not None:
            self.hide()
            return True  # Prevent window from closing
        else:
            Gtk.main_quit()
            return False  # Allow the window to close

    def on_quit(self, widget):
        self.on_window_close()  # Save config before quitting
        Gtk.main_quit()

    def on_tray_activate(self, icon):
        # Show or raise the window when tray icon is clicked
        if not self.is_visible():
            self.show_all()
        else:
            self.present()

    def on_tray_popup(self, icon, button, time):
        menu = Gtk.Menu()

        show_item = Gtk.MenuItem(label="Show/Hide")
        show_item.connect("activate", self.toggle_window)
        menu.append(show_item)

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        menu.append(quit_item)

        menu.show_all()
        menu.popup(None, None, None, None, button, time)

    def toggle_window(self, widget):
        if self.is_visible():
            self.hide()
        else:
            self.show_all()

    def build_tray_menu(self):
        menu = Gtk.Menu()

        show_item = Gtk.MenuItem(label="Show/Hide")
        show_item.connect("activate", self.toggle_window)
        menu.append(show_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Add rotation options
        for label, rot in [("Normal", "n"), ("Left", "l"), ("Right", "r"), ("Invert", "i")]:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", lambda w, r=rot: self.rotate(r))
            menu.append(item)

        menu.append(Gtk.SeparatorMenuItem())

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        menu.append(quit_item)

        menu.show_all()
        return menu

    def on_autodetect_clicked(self, widget):
        known_configs_path = os.path.join(script_dir, "known-configs.txt")
        if not os.path.exists(known_configs_path):
            self.create_message_dialog("Autodetect Error", "known-configs.txt not found.")
            return

        # Get computer name from /sys/firmware/devicetree/base/model
        try:
            with open("/sys/firmware/devicetree/base/model", "r") as f:
                computer_name = f.read().strip()
        except Exception:
            try:
                with open("/sys/devices/virtual/dmi/id/product_name", "r") as f:
                    computer_name = f.read().strip()
            except Exception as e:
                self.create_message_dialog("Autodetect Error", f"Could not read model: {e}")
                return

        # Read known configs
        with open(known_configs_path, "r") as f:
            lines = [line.rstrip("\n") for line in f]

        # Find the config block for this computer
        configs = []
        i = 0
        while i < len(lines):
            if lines[i].startswith("#"):
                device_name = lines[i][1:].strip()
                i += 1
                # Skip blank lines after comment
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
                # If device_name matches computer_name, parse the next 5 lines as config
                if device_name and device_name in computer_name:
                    # Read up to 5 lines, fill missing with ""
                    block = []
                    for _ in range(5):
                        if i < len(lines) and not lines[i].startswith("#"):
                            block.append(lines[i])
                            i += 1
                        else:
                            block.append("")
                    config = {
                        "device_name": device_name,
                        "touchpad": block[0],
                        "touchscreen": block[1],
                        "display": block[2],
                        "lock": block[3],
                        "stylus": block[4],
                    }
                    configs.append(config)
            else:
                i += 1

        if not configs:
            self.create_message_dialog(
                f"Configuration not known for {computer_name}",
                "To add configuration for your device, open a GitHub issue\n\n"
                "https://github.com/archisman-panigrahi/screen-orientation-manager/issues/\n\n"
                "Meanwhile, run `xinput list` to find your touchscreen,\n\n"
                "touchpad, and stylus ID and enter them manually in the app."
            )
            return

        # Use the first matching config
        config = configs[0]
        self.touchpad_entry.set_text(config["touchpad"])
        self.screen_entry.set_text(config["touchscreen"])
        self.display_entry.set_text(config["display"])
        self.display_check.set_active(config["lock"].lower() == "true")
        self.stylus_entry.set_text(config["stylus"])
        # Save to config file
        self.encache(
            config["touchpad"],
            config["touchscreen"],
            config["display"],
            config["lock"],
            config["stylus"]
        )
        self.create_message_dialog("Autodetect", f"Configuration for '{config['device_name']}' loaded.")

def _load_config_devices():
    # Returns tuple (touchpad, touchscreen, display, stylus)
    devices = ["", "", "", "", ""]
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            lines = [l.strip() for l in f.readlines()]
            for i in range(min(5, len(lines))):
                devices[i] = lines[i]
    # touchpad, touchscreen, display, _, stylus
    return devices[0], devices[1], devices[2], devices[4]

def _perform_headless_rotation(letter):
    touchpad, touchscreen, display, stylus = _load_config_devices()
    script_path = os.path.join(script_dir, 'rotation-scripts', f'{letter}.sh')
    subprocess.Popen(
        ['sh', script_path, touchpad, touchscreen, display, stylus],
        stdout=subprocess.PIPE
    ).wait()

def _parse_args():
    parser = argparse.ArgumentParser(
        description="Screen Orientation Manager for X11"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--normal", action="store_true", help="Rotate to normal orientation")
    group.add_argument("--left", action="store_true", help="Rotate to left orientation")
    group.add_argument("--right", action="store_true", help="Rotate to right orientation")
    group.add_argument("--invert", action="store_true", help="Rotate to inverted orientation")
    parser.add_argument("--tray", action="store_true",
                        help="Start in tray without showing the window")
    parser.add_argument("--persist", action="store_true",
                        help="Keep the GUI running after applying rotation")
    # Also allow a single positional argument: normal|left|right|invert
    parser.add_argument("rotation", nargs="?", choices=["normal", "left", "right", "invert"],
                        help="Rotation (alternative positional form)")
    return parser.parse_args()

def _determine_rotation(args):
    if args.normal or args.rotation == "normal":
        return "n"
    if args.left or args.rotation == "left":
        return "l"
    if args.right or args.rotation == "right":
        return "r"
    if args.invert or args.rotation == "invert":
        return "i"
    return None

if __name__ == "__main__":
    args = _parse_args()
    rotation_letter = _determine_rotation(args)
    keep_running = args.persist or args.tray

    if rotation_letter and not keep_running:
        # Headless one-shot rotation and exit (no extra tray instance)
        _perform_headless_rotation(rotation_letter)
        sys.exit(0)

    # Start GUI
    win = ScreenOrientationManager()
    win.connect("delete-event", win.on_window_close)
    win.connect("destroy", Gtk.main_quit)
    if not args.tray:
        win.show_all()

    # If a rotation was requested with --persist, perform it after GUI init
    if keep_running and rotation_letter:
        # Use a timeout to allow the GUI to initialize before performing rotation
        GObject.timeout_add(100, _perform_headless_rotation, rotation_letter)

    Gtk.main()
