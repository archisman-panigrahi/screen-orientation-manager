# <img src="screen-orientation-manager.svg" align="left" width="128" height="128">

## Screen Orientation Manager for touchscreen tablets and convertible laptops running GNU/Linux with X11

You can use this app to easily rotate the touchscreen input, display orientation, touchpad and stylus input in one go.

### Why?

While automatic rotation of input devices works seamlessly in GNOME and KDE on Wayland, many entry-level devices use lightweight desktop environments like XFCE, MATE, or LXDE, which rely on X11 and lack support for automatic touchscreen input rotation. As a result, when the screen is rotated, touch inputs can become misaligned (e.g., after rotating the screen, touching the top-left corner might register as a tap in the bottom-right). This app resolves that issue. It also runs in the system tray, making it easy to access when using the device in tablet mode.

If you want us to add autodetect support for your device, please open an issue in [GitHub issues](https://github.com/archisman-panigrahi/surface-RT-screen-rotator/issues).

![screenshot1](Screenshots/screenshot1.png)
![screenshot2](Screenshots/screenshot2.png)

Based on [theGeekyLad/GtkExperiments](https://github.com/theGeekyLad/GtkExperiments)

**Note**: You need to be on an **Xorg** session for results as unfortunately _Wayland isn't supported_ at the moment.

### Installation

#### Raspberry Pi OS/Debian/Ubuntu

Download the prebuilt .deb package from [GitHub Releases](https://github.com/archisman-panigrahi/surface-RT-screen-rotator/releases/), and install it with

```
sudo apt install /path/to/downloaded_installer.deb
```
Or use a graphical installer like GDebi to install the .deb file.

In Ubuntu, you can use the official PPA

```
sudo add-apt-repository ppa:apandada1/screen-orientation-manager
sudo apt update
sudo screen-orientation-manager
```

#### Arch Linux

You can get it from the [AUR](https://aur.archlinux.org/packages/screen-orientation-manager-git)
```
yay -S screen-orientation-manager-git
```

#### Other operating systems

This project uses the Meson build system for configuration and installation.
Build Instructions:

- Ensure you have Meson and Ninja installed on your system.
- Install gtk3
- Navigate to the project directory.
- Run the following commands to build and install the application:
```
meson setup builddir --prefix=/usr
sudo meson install -C builddir
```
To uninstall, run
```
sudo meson uninstall -C builddir
```
Running the Application

After installation, you can run the application using:
```
screen-orientation-manager
```

### Different device?

By default, the app uses the touchscreen and touchpad ID for Lenovo Chromebook 300e (HANA).
If you are using a different device, you can find the touchscreen name by running the command `xinput list`. Then edit the textbox in the app, and enter the appropriate touchscreen name.

### Autodetect configuration

If you want autodetect to work on your device, please add the device information to either https://github.com/velvet-os/imagebuilder/issues/334, or at https://github.com/archisman-panigrahi/surface-RT-screen-rotator/issues so that we can add its configuration to the app.

Devices supported by autodetect so far:

- Google Hana (Lenovo Chromebook 300e)
- Google Scarlet (Acer Chromebook Tab 10)
- Google Wormdingler (Lenovo Chromebook Duet 3)
- Blooguard (HP Chromebook x360 14a-ca0/14b-ca0)


### Credits

- Thanks to @rubo77, for this project builds upon his shell script.
- Thanks to @theGeekyLad, as this project is a slightly modified version of their python application.
- The icon is based on GuLinux/ScreenRotator. Thanks to @GuLinux.
