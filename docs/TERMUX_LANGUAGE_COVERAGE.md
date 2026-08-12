# Termux Language Coverage

Language Project tracks **94 distinct programming/scripting language families and executable programmable DSLs** represented by packages in the official Termux aarch64 package inventory snapshot used for this release on **2026-08-12**.

- **34 worker-tier modules**: persistent reversible workers used by the benchmark/polyglot chain.
- **60 native-module tier entries**: additional official Termux language/runtime packages with practical source, metadata, examples and runtime probes.
- **85 module entries map to a current GitHub Linguist language label**.
- Those entries collapse to **75 unique GitHub language groups**, because several Termux-supported dialects/implementations intentionally share one GitHub language family (for example shell or Lisp families).
- **9 Termux-supported languages are not separately representable by current GitHub Linguist**; they remain fully present in the project but are prevented from being misclassified as an unrelated GitHub language.

The snapshot uses **language families**, not package/runtime inflation. Multiple versions or implementations of the same language are not counted as extra languages merely to increase the number. For example, multiple Lua/JavaScript/Scheme/Common-Lisp implementations can exist in Termux while Language Project represents the underlying language family only once unless it is a genuinely distinct language/dialect with its own useful module.

Package availability is not the same as an active persistent worker. A language enters the high-speed reversible worker chain only after its worker protocol succeeds on the actual Android device. The broader 94-module coverage layer can still provide source, package planning, runtime status and practical module assets.

## Commands

```bash
language-project supported list
language-project supported status
language-project supported packages
language-project supported install swift cobol groovy
language-project supported install-all
language-project supported balance
language-project supported audit
```

`install-all` can require significant storage because toolchains such as Swift, .NET, Java and Haskell are large. Packages are installed individually so one failed/unavailable package does not abort the rest of the installation pass. Generated files and logs remain under `$HOME/Language Project/`.

## GitHub language percentages

`language-project supported balance` runs the repository's conservative source-byte guardrail. It targets **>= 0.2% for every GitHub-Linguist-recognized language group represented by the project** while still counting the Python orchestration layer in the denominator.

GitHub itself remains authoritative after a push because GitHub Linguist decides the final repository language bar. Languages unsupported by GitHub Linguist cannot truthfully be made to appear as their own percentage; `.gitattributes` therefore prevents those modules from being incorrectly attributed to another language.
