# Worker Protocol

Every executable language worker is an independent persistent process controlled through standard input and standard output.

Commands:

```text
PING
E <lower-or-upper-case hex>
D <lower-or-upper-case hex>
QUIT
```

Responses:

```text
PONG
<hex result>
ERR
```

The orchestrator validates output length and hexadecimal syntax after every transform. Workers are deliberately small so the benchmark measures language/runtime implementation overhead without requiring external network services or a language-specific dependency ecosystem.

The reversible transforms are demonstrations, not cryptography. User data is treated as bytes and is never evaluated as program source.

## Runtime implementation rules

Each registered worker owns the persistent protocol loop in its declared programming language. A worker may invoke a standard Termux utility that is explicitly declared in its package requirements when that is the practical native implementation for that language—for example, shell workers use `tr` from `coreutils` for their byte-safe hexadecimal mapping. This keeps large payloads usable without pretending the utility is a separate programming-language stage.

Workers must be deterministic, reversible, line-oriented, and safe for arbitrary binary input after the orchestrator converts the payload to hexadecimal. A worker is not activated merely because its executable exists: setup requires `PING`, encode, decode, and multiple round-trip test vectors to pass within the configured timeout.
