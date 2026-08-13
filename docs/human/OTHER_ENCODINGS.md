# Other Human-Readable Encodings

Language Project includes a few compact communication encodings that are useful offline:

```bash
language-project human morse --text "SOS"
language-project human morse --decode --text "... --- ..."
language-project human braille --text "abc"
language-project human braille --decode --text "⠁⠃⠉"
language-project human nato --text "A22"
```

The Braille helper is deliberately a simple Grade-1 Latin-letter bridge, not a full contracted Braille translator. Morse covers the common ITU Latin letters, digits and punctuation bundled in the tool.
