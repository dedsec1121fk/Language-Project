# Translation And Reversible Text Bridges

Language Project deliberately separates **semantic translation** from **reversible representation conversion**.

## Semantic translation

`human translate` uses a bundled, high-confidence exact glossary. It can pivot between any two languages that have the same glossary entry. Unknown text is preserved instead of guessed.

```bash
language-project human translate --from en --to el --text "hello file success"
```

This is not advertised as universal machine translation. Accurate free-form translation for every living, historical, signed, constructed and low-resource language cannot realistically be embedded in a small Termux repository without very large language models/dictionaries and substantial storage.

## Universal reversible bridges

Every Unicode string can be converted to and restored from:

- Unicode code points (`U+0393 U+03B5 ...`)
- `\\uXXXX` / `\\UXXXXXXXX` source-code escapes
- UTF-8 hexadecimal bytes
- UTF-8 binary bytes
- decimal Unicode scalar values
- numeric HTML entities
- URL percent encoding
- JSON-style Unicode escapes

```bash
language-project human encode codepoints --text "Γεια 👋"
language-project human encode unicode --text "Γεια 👋"
language-project human decode codepoints "U+0393 U+03B5 U+03B9 U+03B1"
```

These are lossless representation conversions, not semantic translations.

## Programming-language source literals

Language Project can turn arbitrary Unicode text into source-code-friendly literals for several common languages without evaluating the output:

```bash
language-project human source-literal python --text "Γεια 👋"
language-project human source-literal rust --text "Γεια 👋"
language-project human source-literal javascript --text "Γεια 👋"
language-project human source-literal c --text "Γεια 👋"
language-project human source-literal bash --text "Γεια 👋"
```

This complements the generic reversible codepoint/hex/binary/HTML/URL/JSON bridges. It is representation conversion, not semantic translation.

Unicode names can also be converted back to text:

```bash
language-project human name-to-text "GREEK SMALL LETTER LAMDA | SPACE | LATIN CAPITAL LETTER A"
language-project human codepoint U+03BB
```
