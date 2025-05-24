# <img src="screen-orientation-manager.svg" align="left" width="128" height="128">

## Screen Orientation Manager for touchscreen tablets (e.g. Surface RT/Touch screen ARM Chromebooks) running GNU/Linux with X11

You can use this app to easily rotate the touchsceen input, display orientation, touchpad and stylus input in one go.

![screenshot1](Screenshots/screenshot1.png)
![screenshot2](Screenshots/screenshot2.png)

Based on [theGeekyLad/GtkExperiments](https://github.com/theGeekyLad/GtkExperiments)

Tested in Surface RT [running Raspberry Pi OS](https://openrt.gitbook.io/open-surfacert/surface-rt/linux/root-filesystem/distros/raspberry-pi-os) and [Lenovo Chromebook 300e](https://velvet-os.github.io/) running Debian Trixie.

**Note**: You need to be on an **Xorg** session for results as unfortunately _Wayland isn't supported_ at the moment.

### Installation

#### Raspberry Pi OS/Debian/Ubuntu

Download the prebuilt .deb package from [GitHub Releases](https://github.com/archisman-panigrahi/surface-RT-screen-rotator/releases/), and install it with

```
sudo apt install /path/to/downloaded_installer.deb
```
Or use a graphical installer like GDebi to install the .deb file.

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

### Autodetect

If you want autodetect to work on your device, please add the device information to https://github.com/velvet-os/imagebuilder/issues/334.
Devices supported by autodetect so far:

- Google Hana (Lenovo Chromebook 300e)
- Google Scarlet (Acer Chromebook Tab 10)
- Google Wormdingler (Lenovo Chromebook Duet 3)


### Credits

- Thanks to @rubo77, for this project builds upon his shell script.
- Thanks to @theGeekyLad, as this project is a slightly modified version of their python application.
- The icon is based on GuLinux/ScreenRotator. Thanks to @GuLinux.
