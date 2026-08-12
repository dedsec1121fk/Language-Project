#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo '--- Encode / decode ---'
ENC="$(language-project tools codec base64 --text 'Language Project')"
echo "$ENC"
language-project tools codec base64 --decode --text "$ENC"

echo '--- Secure UUID ---'
language-project tools generate --kind uuid

echo '--- README hash ---'
language-project tools hash --file "$HOME/Language Project/app/README.md"

echo '--- Project storage summary ---'
language-project tools storage "$HOME/Language Project" --top 5
