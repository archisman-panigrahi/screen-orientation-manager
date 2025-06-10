#!/bin/bash
# filepath: bump-version.sh

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <new_version> <changelog_message>"
    exit 1
fi

NEW_VERSION="$1"
CHANGELOG_MSG="$2"
PYFILE="ScreenOrientationManager.py"
CHANGELOG="debian/changelog"
DIST="noble"

# Update version in ScreenOrientationManager.py
sed -i -E "s/(about\.set_version\(\s*\")[^\"]+(\")/\1$NEW_VERSION\2/" "$PYFILE"

# Get maintainer name and email
NAME=$(git config user.name)
EMAIL=$(git config user.email)
if [ -z "$NAME" ]; then NAME="${DEBFULLNAME:-Your Name}"; fi
if [ -z "$EMAIL" ]; then EMAIL="${DEBEMAIL:-you@example.com}"; fi

# Get current date in RFC 2822 format
DATE=$(date -R)

# Prepare changelog entry
ENTRY="surface-RT-screen-rotator ($NEW_VERSION) $DIST; urgency=medium

  * $CHANGELOG_MSG

 -- $NAME <$EMAIL>  $DATE
"

# Prepend to changelog
if [ -f "$CHANGELOG" ]; then
    TMPFILE=$(mktemp)
    echo "$ENTRY" > "$TMPFILE"
    cat "$CHANGELOG" >> "$TMPFILE"
    mv "$TMPFILE" "$CHANGELOG"
else
    echo "$ENTRY" > "$CHANGELOG"
fi

echo "Version updated to $NEW_VERSION in $PYFILE and changelog updated."