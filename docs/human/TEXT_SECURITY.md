# Unicode Text Safety

Unicode is expressive but source code, identifiers and filenames can contain invisible or bidirectional formatting characters that are difficult to notice visually.

Use:

```bash
language-project human text-audit --file source.txt
```

The audit reports:

- script distribution
- mixed-script text
- Unicode normalization status
- bidirectional control characters
- invisible/format characters
- combining marks
- code points and Unicode names for suspicious characters

This is a diagnostic signal, not a malware verdict. Legitimate multilingual text may naturally contain several scripts.
