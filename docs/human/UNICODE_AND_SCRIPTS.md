# Unicode, Scripts And Alphabets

The bundled Unicode 17 data lets Language Project identify script ranges, blocks, code point names and character properties offline.

`human alphabet` is a convenience name: it enumerates letter-category characters assigned to a Unicode script. Some writing systems are abjads, abugidas, syllabaries, logographic systems or mixed systems rather than alphabets.

Useful examples:

```bash
language-project human scripts cyrillic
language-project human script Cyrillic
language-project human alphabet Cyrillic --limit 200
language-project human detect-script --file document.txt
language-project human text-audit --file suspicious.txt
```

`text-audit` flags mixed scripts, bidirectional controls, invisible format characters and combining marks. This is useful for source-code review, filenames, domains copied into notes, and Unicode debugging.
