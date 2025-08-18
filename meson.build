project('screen-orientation-manager', meson_version: '>=0.45.1')

py3 = import('python')
gnome = import('gnome')

# Find Python3 interpreter
python = py3.find_installation()

# Define data directory
data_dir = join_paths(get_option('prefix'), 'share', 'screen-orientation-manager')

# Install the entire media directory (recursively)
install_subdir('rotation-scripts', install_dir: data_dir)
install_data('ScreenOrientationManager.py', install_dir: data_dir)
install_data('known-configs.txt', install_dir: data_dir)

# Create a wrapper script in /usr/bin
configure_file(
  input: 'screen-orientation-manager_wrapper.in',
  output: 'screen-orientation-manager',
  configuration: {
    'python': python.full_path(),
    'script': join_paths(data_dir, 'ScreenOrientationManager.py')
  },
  install: true,
  install_mode: 'rwxr-xr-x',  # Ensure the file is executable
  install_dir: join_paths(get_option('prefix'), 'bin')
)

# Install the desktop file
install_data('io.github.archisman_panigrahi.screen-orientation-manager.desktop', install_dir: join_paths(get_option('prefix'), 'share', 'applications'))

# Install the icon to the hicolor directory
install_data('io.github.archisman_panigrahi.screen-orientation-manager.svg', install_dir: join_paths(get_option('prefix'), 'share', 'icons/hicolor/scalable/apps'))

