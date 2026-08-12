#!/data/data/com.termux/files/usr/bin/bash
set -u
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Language-Project"
STAGE="$HOME/.language-project-stage.$$"

echo "Language Project — Termux installer / upgrader"
if ! command -v pkg >/dev/null 2>&1; then
  echo "ERROR: Termux pkg was not found. Run this inside Termux."
  exit 1
fi

pkg update -y || true
pkg install -y python coreutils curl || { echo "Could not install required core packages."; exit 1; }

# Shared Android storage commonly has noexec behavior and is unsuitable for compiled workers.
if [ "$SRC" != "$DEST" ]; then
  echo "Staging project in Termux private storage..."
  rm -rf "$STAGE"; mkdir -p "$STAGE" || exit 1
  cp -a "$SRC"/. "$STAGE"/ || { rm -rf "$STAGE"; exit 1; }

  # Preserve user-generated local data across upgrades without preserving stale binaries.
  if [ -d "$DEST" ]; then
    echo "Preserving previous results, bundles, database, and unfinished checkpoints..."
    mkdir -p "$STAGE/results" "$STAGE/bundles" "$STAGE/state/checkpoints"
    [ -d "$DEST/results" ] && cp -a "$DEST/results"/. "$STAGE/results"/ 2>/dev/null || true
    [ -d "$DEST/bundles" ] && cp -a "$DEST/bundles"/. "$STAGE/bundles"/ 2>/dev/null || true
    [ -f "$DEST/state/history.sqlite3" ] && cp -a "$DEST/state/history.sqlite3" "$STAGE/state/history.sqlite3" || true
    [ -d "$DEST/state/checkpoints" ] && cp -a "$DEST/state/checkpoints"/. "$STAGE/state/checkpoints"/ 2>/dev/null || true
  fi

  rm -rf "$DEST" && mv "$STAGE" "$DEST" || { echo "ERROR: Could not install into $DEST"; exit 1; }
fi
ROOT="$DEST"

# Generated binaries and runtime detection are always rebuilt for this device.
rm -rf "$ROOT/build"
mkdir -p "$ROOT/build" "$ROOT/results" "$ROOT/bundles" "$ROOT/state" "$ROOT/state/checkpoints"
touch "$ROOT/build/.gitkeep" "$ROOT/results/.gitkeep" "$ROOT/bundles/.gitkeep" "$ROOT/state/.gitkeep"
rm -f "$ROOT/state/active.json" "$ROOT/state/calibration.json" "$ROOT/state/polytools.json"

echo "Running core static self-test..."
python "$ROOT/scripts/selftest.py" || { echo "ERROR: core self-test failed."; exit 1; }

echo "Verifying packaged file manifest..."
python "$ROOT/scripts/verify_manifest.py" || { echo "ERROR: project manifest verification failed."; exit 1; }

if ! python "$ROOT/scripts/setup.py" --install --refresh-catalog; then
  echo
  echo "ERROR: No executable language workers passed verification."
  echo "Run: python $ROOT/scripts/setup.py --install"
  exit 1
fi

# Re-index preserved/new JSON results into the local SQLite control-plane database.
python "$ROOT/Language.py" db rebuild >/dev/null 2>&1 || true

mkdir -p "$PREFIX/bin"
for CMD in language-project language; do
 cat > "$PREFIX/bin/$CMD" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec python "$ROOT/Language.py" "\$@"
EOF
 chmod +x "$PREFIX/bin/$CMD"
done
cat > "$PREFIX/bin/langtool" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
exec python "$ROOT/Language.py" langtools "\$@"
EOF
chmod +x "$PREFIX/bin/langtool"

echo
echo "Installed in: $ROOT"
echo "Run: language-project"
echo "Alias: language"
echo "Dashboard: language-project dashboard"
echo "Catalog stats: language-project catalog stats"
echo "Recommended calibration: language-project calibrate"
echo "Native tools: language-project langtools list  (or: langtool list)"
echo "All-language workspace report: language-project langtools workspace-report ~/YourProject"
