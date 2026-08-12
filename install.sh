#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/Language Project"
APP="$BASE/app"
STAGE="$HOME/.language-project-install-stage.$$"

printf '%s\n' "Language Project — Termux installer / upgrader"
printf '%s\n' "Runtime home: $BASE"

if ! command -v pkg >/dev/null 2>&1; then
  echo "ERROR: Termux pkg was not found. Run this inside Termux."
  exit 1
fi

pkg update -y || true
pkg install -y python coreutils curl git || {
  echo "ERROR: Could not install the required core packages."
  exit 1
}

mkdir -p \
  "$BASE" \
  "$BASE/build" \
  "$BASE/state/checkpoints" \
  "$BASE/results" \
  "$BASE/bundles" \
  "$BASE/backups" \
  "$BASE/reports" \
  "$BASE/logs" \
  "$BASE/cache" \
  "$BASE/tmp" \
  "$BASE/downloads" \
  "$BASE/workspace"

# Android shared storage is commonly unsuitable for executing compiled binaries.
# Keep the installed application itself and every generated runtime artifact in
# Termux private home storage under "$HOME/Language Project".
if [ "$SRC" != "$APP" ]; then
  echo "Installing application source into: $APP"
  rm -rf "$STAGE"
  mkdir -p "$STAGE"
  cp -a "$SRC"/. "$STAGE"/

  # Do not copy local development artefacts into the installed application.
  rm -rf \
    "$STAGE/.git" \
    "$STAGE/__pycache__"
  find "$STAGE" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
  find "$STAGE" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete 2>/dev/null || true

  OLD="$BASE/.previous-app.$$"
  rm -rf "$OLD"
  if [ -d "$APP" ]; then mv "$APP" "$OLD"; fi
  if mv "$STAGE" "$APP"; then
    rm -rf "$OLD"
  else
    echo "ERROR: Could not install application source."
    rm -rf "$APP"
    [ -d "$OLD" ] && mv "$OLD" "$APP" || true
    rm -rf "$STAGE"
    exit 1
  fi
fi

export LANGUAGE_PROJECT_HOME="$BASE"
ROOT="$APP"
ENTRY="$ROOT/cli/Language.py"

# Compiled outputs are device-specific and are rebuilt every installation.
rm -rf "$BASE/build"
mkdir -p "$BASE/build" "$BASE/state/checkpoints" "$BASE/results" "$BASE/bundles" \
         "$BASE/backups" "$BASE/reports" "$BASE/logs" "$BASE/cache" "$BASE/tmp" \
         "$BASE/downloads" "$BASE/workspace"
rm -f "$BASE/state/active.json" "$BASE/state/calibration.json" "$BASE/state/polytools.json"

if [ ! -f "$ENTRY" ]; then
  echo "ERROR: Installed entrypoint is missing: $ENTRY"
  exit 1
fi

echo "Running core self-test..."
python "$ROOT/scripts/selftest.py" || { echo "ERROR: core self-test failed."; exit 1; }

echo "Verifying packaged manifest..."
python "$ROOT/scripts/verify_manifest.py" || { echo "ERROR: project manifest verification failed."; exit 1; }

if ! python "$ROOT/scripts/setup.py" --install --refresh-catalog; then
  echo
  echo "ERROR: No executable language workers passed verification."
  echo "Repair command: LANGUAGE_PROJECT_HOME=\"$BASE\" python \"$ROOT/scripts/setup.py\" --install"
  exit 1
fi

# Re-index preserved/new benchmark JSON into the persistent SQLite database.
python "$ENTRY" db rebuild >/dev/null 2>&1 || true

mkdir -p "$PREFIX/bin"
for CMD in language-project language; do
  cat > "$PREFIX/bin/$CMD" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
export LANGUAGE_PROJECT_HOME="$BASE"
exec python "$ENTRY" "\$@"
EOF
  chmod +x "$PREFIX/bin/$CMD"
done

cat > "$PREFIX/bin/langtool" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
export LANGUAGE_PROJECT_HOME="$BASE"
exec python "$ENTRY" langtools "\$@"
EOF
chmod +x "$PREFIX/bin/langtool"

cat > "$PREFIX/bin/language-project-home" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
printf '%s\n' "$BASE"
EOF
chmod +x "$PREFIX/bin/language-project-home"

echo
echo "Language Project installed successfully."
echo "Application: $APP"
echo "Runtime/data home: $BASE"
echo "Run: language-project"
echo "Alias: language"
echo "Native tools: langtool list"
echo "Storage path: language-project-home"
echo "Workspace report: language-project langtools workspace-report ~/YourProject --output \"$BASE/reports/workspace.json\""
