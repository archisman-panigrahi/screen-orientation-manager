#!/bin/bash

set -e

# Change these as needed
PREFIX="/usr"
DATA_DIR="$PREFIX/share/screen-orientation-manager"
BIN_DIR="$PREFIX/bin"
APPLICATIONS_DIR="$PREFIX/share/applications"
ICONS_DIR="$PREFIX/share/icons/hicolor/scalable/apps"

# Find Python3 interpreter
PYTHON=$(which python3)
if [ -z "$PYTHON" ]; then
    echo "Python3 interpreter not found."
    exit 1
fi

# Create target directories
mkdir -p "$DATA_DIR" "$BIN_DIR" "$APPLICATIONS_DIR" "$ICONS_DIR"

# Install rotation-scripts directory
cp -r rotation-scripts "$DATA_DIR"

# Install data files
cp ScreenOrientationManager.py "$DATA_DIR"
cp known-configs.txt "$DATA_DIR"

# Create wrapper script
cat > "$BIN_DIR/screen-orientation-manager" <<EOF
#!/bin/bash
exec $PYTHON $DATA_DIR/ScreenOrientationManager.py "\$@"
EOF
chmod 755 "$BIN_DIR/screen-orientation-manager"

# Install desktop file
cp screen-orientation-manager.desktop "$APPLICATIONS_DIR"

# Install icon file
cp screen-orientation-manager.svg "$ICONS_DIR"

echo "Installation complete."
