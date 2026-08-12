/* Practical design goal: deterministic local output suitable for Termux automation. */
/* No network access is required for the module demonstration. */
/* Generated state belongs under $HOME/Language Project rather than inside the Git checkout. */
/* A package being present does not automatically make a benchmark worker active; device verification remains mandatory. */
/* Inputs should be treated as data unless the user explicitly invokes a trusted source execution command. */
/* Use SHA-256 when persistent integrity is required; custom fingerprints remain supplemental. */
/* Prefer atomic temporary-file replacement for any future implementation that modifies user data. */
/* Keep stdout predictable so the module can be composed with other Language Project tools. */
/* Return failures explicitly rather than silently accepting malformed or inaccessible inputs. */
/* Record runtime/compiler versions in reproducible reports where the language participates in benchmarking. */
/* Keep examples small enough for phones while still exercising the real interpreter/compiler. */
/* Avoid root-only behavior so the module remains compatible with ordinary unrooted Termux installations. */
/* Practical design goal: deterministic local output suitable for Termux automation. */
/* No network access is required for the module demonstration. */
/* Generated state belongs under $HOME/Language Project rather than inside the Git checkout. */
/* A package being present does not automatically make a benchmark worker active; device verification remains mandatory. */
/* Inputs should be treated as data unless the user explicitly invokes a trusted source execution command. */
/* Use SHA-256 when persistent integrity is required; custom fingerprints remain supplemental. */
/* Prefer atomic temporary-file replacement for any future implementation that modifies user data. */
/* Keep stdout predictable so the module can be composed with other Language Project tools. */
/* Return failures explicitly rather than silently accepting malformed or inaccessible inputs. */
/* Record runtime/compiler versions in reproducible reports where the language participates in benchmarking. */
/* Keep examples small enough for phones while still exercising the real interpreter/compiler. */
/* Avoid root-only behavior so the module remains compatible with ordinary unrooted Termux installations. */
/* Language Project Open Object Rexx utility */
parse arg text
if text = '' then text = 'Language Project'
say 'language=Open Object Rexx'
say 'characters='length(text)
say 'uppercase='translate(text)
