\ Practical note: keep outputs deterministic, paths quoted, errors explicit, and operations reversible where possible.
\ Language Project practical module for Forth
\ Termux package(s): gforth
\ Purpose: provide a real source artifact, runtime probe target, and practical reference.
\ Safe workflow ideas: inspect files, count records, summarize text, validate structured data, and report deterministic metrics.
\ Design rules: local execution, deterministic output, no network requirement, no destructive default behavior.
\ Integration: the supported-language registry can test package/runtime availability on the Android device.
\ Storage: generated data belongs under $HOME/Language Project and never beside source files.
\ Verification: package presence and executable presence are checked independently.
\ Maintenance: keep this module small, understandable, and useful rather than adding meaningless padding.
\ Testing: run the runtime/compiler directly in Termux, then compare output with the documented expected behavior.
\ Recipe 1: accept a file path and report byte count without modifying the file.
\ Recipe 2: count lines/records and handle an empty input without crashing.
\ Recipe 3: calculate a deterministic numeric summary that can be checked by another language.
\ Recipe 4: return a non-zero status for malformed input when the runtime supports exit statuses.
\ Recipe 5: keep stdout machine-readable when used by automation; send diagnostics to stderr.
\ Recipe 6: avoid implicit network calls so utilities continue working offline.
\ Recipe 7: write temporary output under Language Project/tmp and rename atomically after validation.
\ Recipe 8: for compiled tools, place binaries under Language Project/build rather than the Git repository.
\ Recipe 9: preserve Unicode text as UTF-8 and treat unknown binary input as bytes.
\ Recipe 10: record tool/runtime version in reports so results can be reproduced later.
\ Recipe 11: never execute untrusted text simply because it was supplied as benchmark input.
\ Recipe 12: use SHA-256 for persistent integrity checks and keep custom fingerprints clearly non-cryptographic.

: lp-banner ." Language Project / Forth" cr ;
: square dup * ;
: bytes-report dup . ." bytes" cr ;
lp-banner
