#!/data/data/com.termux/files/usr/bin/bash
set -e
language-project human status
language-project human languages Greek --limit 10
language-project human script Greek
language-project human detect-script --text 'Hello κόσμε Привет مرحبا 你好'
language-project human translate --from en --to el --text 'hello file success'
language-project human encode codepoints --text 'Γεια 👋'
language-project human symbols-describe --locale el --text 'if (a >= b) { x++; }'

language-project human glottolog-search Greek --level language --limit 5
language-project human db-stats
language-project human codepoint U+03BB
language-project human source-literal rust --text 'Γεια 👋'
language-project human name-to-text 'GREEK SMALL LETTER LAMDA | SPACE | LATIN CAPITAL LETTER A'
