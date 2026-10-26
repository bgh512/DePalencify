#!/usr/bin/env bash
# Creates a clickable DePalencify icon the first time it runs (and again if the folder is moved). Safe to run every time.
# Mac:   DePalencify.app on the Desktop.   Linux: an entry in the applications menu and an icon on the Desktop.
cd "$(dirname "$0")/.." || exit 0
DIR="$PWD"
MARK=".shortcut_made"
[ "$(cat "$MARK" 2>/dev/null)" = "$DIR" ] && exit 0

case "$(uname -s)" in
Darwin)
    APP="$HOME/Desktop/DePalencify.app"
    rm -rf "$APP"
    mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" || exit 0
    cat > "$APP/Contents/MacOS/DePalencify" <<LAUNCH
#!/bin/bash
exec open -a Terminal "$DIR/run.command"
LAUNCH
    chmod +x "$APP/Contents/MacOS/DePalencify"
    cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>DePalencify</string>
<key>CFBundleDisplayName</key><string>DePalencify</string>
<key>CFBundleIdentifier</key><string>uk.depalencify.launcher</string>
<key>CFBundleExecutable</key><string>DePalencify</string>
<key>CFBundleIconFile</key><string>DePalencify</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>1.0</string>
<key>LSUIElement</key><false/>
</dict></plist>
PLIST
    ICONSET="$(mktemp -d)/DePalencify.iconset"
    mkdir -p "$ICONSET"
    for size in 16 32 128 256 512; do
        sips -z $size $size assets/icon.png --out "$ICONSET/icon_${size}x${size}.png" >/dev/null 2>&1
        sips -z $((size * 2)) $((size * 2)) assets/icon.png --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null 2>&1
    done
    iconutil -c icns "$ICONSET" -o "$APP/Contents/Resources/DePalencify.icns" >/dev/null 2>&1
    touch "$APP"
    echo "Created a DePalencify icon on your Desktop."
    ;;
Linux)
    ENTRY="[Desktop Entry]
Type=Application
Name=DePalencify
Comment=Convert chamber .paf files to figures and data
Exec=bash \"$DIR/run.sh\"
Path=$DIR
Icon=$DIR/assets/icon.png
Terminal=true
Categories=Science;Education;"
    MENU="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
    DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null)"
    [ -n "$DESKTOP_DIR" ] || DESKTOP_DIR="$HOME/Desktop"
    mkdir -p "$MENU" 2>/dev/null
    for place in "$MENU" "$DESKTOP_DIR"; do
        [ -d "$place" ] || continue
        printf '%s\n' "$ENTRY" > "$place/DePalencify.desktop" && chmod +x "$place/DePalencify.desktop"
        command -v gio >/dev/null 2>&1 && gio set "$place/DePalencify.desktop" metadata::trusted true >/dev/null 2>&1
    done
    echo "Created a DePalencify icon in your applications menu and on your Desktop."
    ;;
*) exit 0 ;;
esac
printf '%s' "$DIR" > "$MARK"
exit 0
