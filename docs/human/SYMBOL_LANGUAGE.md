# Programming Symbol Narration

Language Project includes a programming-symbol lexicon for punctuation and common multi-character operators.

```bash
language-project human symbols-describe --text 'if (a >= b) { x++; }'
language-project human symbols-describe --locale el --text 'x += 1;'
```

Narrated bracket tokens can be converted back:

```bash
language-project human symbols-parse --text '[open parenthesis]x[close parenthesis]'
```

English and Greek have bundled localized symbol labels. Unsupported locales fall back to canonical operator names instead of inventing translations. The lexicon is stored as data and can be extended without changing the engine.
