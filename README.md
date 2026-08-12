# Language Project

**One input. Every verified Termux language. Forward and backward. Timed. Plus a massive global programming-language catalog.**

Language Project is a Termux-native polyglot execution, resilience, orchestration, and benchmarking platform. It keeps two intentionally separate layers:

1. **Execution layer** — real worker source code for languages that have a direct Termux runtime/toolchain candidate and can pass a live on-device round-trip self-test.
2. **Global catalog layer** — a large A–Z index of programming languages, dialects, historical languages, DSLs, and experimental/esoteric languages. Catalog entries are metadata; they never get counted as executable unless a real worker exists and passes Termux verification.

The bundled snapshot contains **1,323 cataloged language names** and **34 executable worker implementations/candidates**. The catalog is refreshable because no static repository can truthfully guarantee “every language ever created”: new and obscure languages continue to appear, and Esolang Wiki alone contains thousands of experimental languages. The refresh engine merges current public indexes without weakening the rule that the benchmark chain contains only verified Termux workers.

## What Happens To Your Input

```text
INPUT BYTES
   ↓
worker 01 encode → timed
   ↓
worker 02 encode → timed
   ↓
...
   ↓
last worker encode → timed
   ↓
reverse worker decode → timed
   ↓
...
   ↓
worker 01 decode → timed
   ↓
RECOVERED BYTES
   ↓
SHA-256 + byte-for-byte integrity verification
```

Workers are persistent/prewarmed processes. Compiled workers are built during setup, not during a benchmark. The orchestrator records startup time separately from encode/decode stage wall time.

## Advanced Architecture

Language Project is now more than a serial benchmark. The worker protocol stays intentionally tiny, while the Python control plane provides scheduling, resilience, observability, historical analysis, and reproducible benchmark workflows.

<details>
<summary><strong>Execution Engine</strong></summary>

- Automatic Termux package installation and per-runtime live self-testing.
- Android shared-storage safe install: the project relocates itself to `$HOME/Language-Project` before executing compiled binaries.
- Persistent/prewarmed worker processes over a strict stdin/stdout protocol.
- Text and arbitrary binary-file input, including zero-byte payload handling.
- Forward + reverse chains with byte-for-byte and SHA-256 integrity verification.
- Registry, fastest-known, deterministic-random, and four adaptive device-calibrated orderings.
- Multi-round runs, warm-up passes, watchdogs, and fail-closed runtime verification.
- Optional local plugin hooks, disabled by default so they cannot silently distort normal benchmark runs.

</details>

<details>
<summary><strong>Adaptive Scheduler</strong></summary>

- Device-specific calibration over multiple payload sizes.
- Builds `adaptive-balanced`, `adaptive-latency`, `adaptive-throughput`, and `adaptive-stable` worker orders.
- Scores latency, jitter, startup cost, and throughput rather than relying on one timing sample.
- Calibration is persisted separately in `state/calibration.json` and fingerprinted for reproducibility.
- Dry-run execution planner shows the exact language order, runtime versions, transformation count, and a rough metric-based estimate before a run starts.

</details>

<details>
<summary><strong>Resilience And Integrity Laboratory</strong></summary>

- Differential audit across deterministic binary test vectors.
- Repeated encode-output determinism checks per worker.
- Controlled Chaos mode that restarts workers during encode/decode stages and verifies recovery.
- Atomic resumable checkpoint chains that can continue after the Termux process exits.
- Multi-order Consensus mode: complete all-language chains run in different deterministic random orders and must all recover the same hash.
- Stress/Endurance mode using deterministic binary payloads across repeated complete chains.

</details>

<details>
<summary><strong>Parallelism And Topology Laboratory</strong></summary>

- Serial Language Race for directly comparable per-worker timings.
- Parallel Language Race for simultaneous worker pressure.
- Multi-size Matrix mode for scaling behavior.
- Braided Topology mode distributes every active language across independent reversible lanes and executes the lanes concurrently.
- Round-robin, contiguous, and deterministic-shuffle lane placement.
- Lane balance ratio, wall-clock critical path, median/P95 timings, jitter, and throughput.
- Full Showcase and declarative multi-step Scenario workflows.

</details>

<details>
<summary><strong>Observability And Statistics</strong></summary>

- P50/median, P90, P95, P99, mean, minimum, maximum, standard deviation, and jitter percentage.
- Per-language startup/prewarm timing and payload throughput.
- Input/encoded entropy observations.
- Optional live resource sampling for process RSS, available memory, CPU utilization estimate, load average, and readable Android thermal zones.
- Device snapshots with Android/Termux/runtime metadata.
- Environment provenance containing registry, manifest, active-state, and calibration hashes plus runtime versions.
- Environment fingerprint for comparing runs produced under different runtime/toolchain states.

</details>

<details>
<summary><strong>Persistent Performance Database</strong></summary>

- Every saved benchmark can be indexed into a local SQLite database using Python's standard library.
- Session table for mode, bytes, worker count, integrity, duration, device data, and full metadata.
- Stage table for historical per-language median/P95/throughput measurements.
- Historical leaderboard across many sessions.
- Mode-filtered recent-run queries.
- Database rebuild from canonical JSON result files.
- Performance regression gate for CI-style comparison against the previous comparable result.

</details>

<details>
<summary><strong>Reports, Bundles And Reproducibility</strong></summary>

- JSON machine-readable reports.
- CSV rankings/matrices where tabular output applies.
- Markdown summaries.
- Offline HTML result pages for advanced benchmark modes.
- Result history browsing and comparisons.
- Portable ZIP session bundles with a SHA-256 `BUNDLE-MANIFEST.json`.
- Manifest hashing/verification for project source files.
- Declarative `config/scenarios.json` workflows for confidence, presentation, and resilience runs.

</details>

<details>
<summary><strong>Global Language Catalog</strong></summary>

- A–Z catalog browser and substring search.
- One metadata JSON file per cataloged language under `catalog/languages/`.
- Best-effort live refresh from multiple public language indexes.
- README A–Z catalog regeneration after refresh.
- Strict separation between catalog records and verified Termux workers.

</details>

## Install In Termux

```bash
termux-setup-storage   # only if the ZIP is in shared storage
cd ~/storage/downloads/Language-Project
bash install.sh
```

The installer stages the project into `$HOME/Language-Project`, installs core dependencies, attempts all registered runtime packages, rebuilds device-specific compiled workers, performs live protocol and round-trip tests, refreshes the catalog on a best-effort basis, reindexes saved results into SQLite, and creates both `language-project` and `language` commands. On upgrades it preserves previous `results/`, `bundles/`, the SQLite history database, and unfinished checkpoints while discarding stale compiled binaries/runtime detection.

Some runtimes/toolchains are large. Package availability can differ by Android architecture and can change in Termux repositories, so **the active language count is always measured on the user's device**.

## Run

```bash
language-project
```

Direct input:

```bash
language-project run --text "DedSec Project"
```

File input:

```bash
language-project run --file ~/storage/downloads/example.bin
```

Advanced run:

```bash
language-project run --text "Language Project" --rounds 3 --warmups 2 --order random --seed 1121
```

Benchmark suite:

```bash
language-project bench --sizes 16 256 4096 65536 --repeats 3
```

Independent language race:

```bash
language-project race --text "Language Project" --iterations 10 --warmups 2
```

Parallel race:

```bash
language-project parallel-race --text "Language Project" --iterations 12 --parallel 8
```

Multi-size matrix:

```bash
language-project matrix --sizes 16 256 4096 65536 1048576 --iterations 5
```

Endurance/stress chain:

```bash
language-project stress --size 4096 --cycles 50 --seed 1121
```

One-command showcase:

```bash
language-project showcase --text "Language Project" --profile showcase
```

Heavy profile:

```bash
language-project showcase --file ~/storage/downloads/example.bin --profile extreme
```

Benchmark profiles, device snapshot, and saved-result history:

```bash
language-project profiles
language-project snapshot
language-project history --limit 20
language-project compare
```

Runtime status:

```bash
language-project list
language-project doctor
language-project audit
language-project verify
```

Catalog:

```bash
language-project catalog stats
language-project catalog search "Lisp"
language-project catalog list --letter A
language-project catalog refresh
```

## Advanced Control-Plane Commands

<details>
<summary><strong>Adaptive Calibration And Planning</strong></summary>

```bash
language-project calibrate --sizes 64 4096 65536 --iterations 4 --warmups 2
language-project calibration --strategy balanced
language-project run --text "adaptive" --order adaptive-balanced
language-project plan --bytes 4096 --rounds 3 --order adaptive-throughput
```

</details>

<details>
<summary><strong>Differential, Chaos And Consensus Validation</strong></summary>

```bash
language-project differential --vectors 32 --max-size 4096 --seed 1121
language-project chaos --text "survive" --cycles 12 --restart-rate 0.20 --seed 1121
language-project consensus --text "same result" --replicas 3 --seed 1121
```

</details>

<details>
<summary><strong>Resumable Checkpointing</strong></summary>

```bash
language-project checkpoint --text "resume me" --stop-after 5
language-project checkpoints
language-project resume state/checkpoints/<session>.json
```

</details>

<details>
<summary><strong>Braided Topology Lab</strong></summary>

```bash
language-project topology --text "braid" --lanes 4 --iterations 5 --strategy round-robin
language-project topology --file ~/storage/downloads/example.bin --lanes 6 --strategy shuffle --seed 1121
```

</details>

<details>
<summary><strong>Scenarios</strong></summary>

```bash
language-project scenarios
language-project scenario confidence --text "Language Project"
language-project scenario presentation --text "Language Project"
language-project scenario resilience --text "Language Project"
```

</details>

<details>
<summary><strong>SQLite History And Regression Gate</strong></summary>

```bash
language-project db stats
language-project db recent --limit 20
language-project db leaderboard --limit 30 --min-samples 2
language-project db rebuild
language-project regression --mode chain --threshold 15
```

</details>

<details>
<summary><strong>Dashboard, Telemetry And Bundles</strong></summary>

```bash
language-project dashboard
language-project run --text "observe me" --telemetry
language-project bundle
language-project bundle results/run-example.json --name demo.zip
```

</details>

<details>
<summary><strong>Architecture Documentation</strong></summary>

- `docs/ADVANCED_ARCHITECTURE.md` — planes, result lifecycle, and reproducibility model.
- `docs/ADAPTIVE_SCHEDULER.md` — device calibration and adaptive order strategies.
- `docs/CHECKPOINTS.md` — interruption-safe resumable chains.
- `docs/CHAOS_TESTING.md` — controlled worker restart resilience.
- `docs/DIFFERENTIAL_AUDIT.md` — deterministic corpus verification.
- `docs/TOPOLOGY.md` — braided concurrent lane execution.
- `docs/CONSENSUS.md` — complete-chain multi-order agreement.
- `docs/TELEMETRY.md` — resource sampling model.
- `docs/DATABASE.md` — SQLite session and stage history.
- `docs/REGRESSION_GATES.md` — historical CI-style performance checks.
- `docs/SCENARIOS.md` — declarative multi-step workflows.
- `docs/BUNDLES.md` — portable result bundle format.
- `docs/PLUGINS.md` — optional local extension hooks.

</details>

## Worker Protocol

Every executable worker implements:

```text
PING       -> PONG
E <hex>    -> reversibly transformed hex
D <hex>    -> inverse-transformed hex
QUIT       -> clean process exit
```

The existing workers use small deterministic reversible transforms designed for interoperability and speed measurement. They are **not cryptography**. User input is never evaluated as source code.

## Executable Termux Workers

Bash, AWK, C, C++, Python, JavaScript, Perl, Ruby, Lua, PHP, Tcl, Go, Rust, Java, Scheme (Guile), Erlang, Elixir, Nim, Zig, Prolog (SWI), Haskell, D, Kotlin, Scala, Dart, Fortran, Racket, Crystal, Common Lisp (ECL), POSIX sh (Dash), Z shell, fish, sed, jq.

A source file existing in `languages/` is still not enough to count. `scripts/setup.py` must install/find the runtime, build if required, start the worker, pass protocol tests, and successfully round-trip multiple test vectors. Only then is it written to `state/active.json`.

## Global Programming-Language Catalog

The following section is deliberately collapsible. It is a **catalog**, not a claim that all entries execute in Termux. The bundled snapshot merges GitHub Linguist programming entries, Pygments language lexers, and a curated historical/experimental index. Running `language-project catalog refresh` can expand/update it from PLDB plus several other live public indexes. The refresh process follows MediaWiki pagination, so large esoteric-language indexes are not truncated to a single result page; after refresh, it also regenerates the collapsible README catalog automatically.

<!-- LANGUAGE-CATALOG:START -->

Bundled catalog snapshot: **1,323 unique language/dialect names**. Entries here are catalog records; only on-device verified workers participate in the execution chain.

<details>
<summary><strong>Symbols / Numbers — 3 cataloged names</strong></summary>

05AB1E · 1C Enterprise · 4D

</details>

<details>
<summary><strong>A — 74 cataloged names</strong></summary>

A+ · A-0 System · ABAP · ABAP CDS · ABC · ABNF · ACC · ActionScript · ActionScript 3 · Actor · Ada · ADL · AdvPL · Agda · AGS Script · Aheui · AIDL · Aiken · AL · Aleo · ALGOL · ALGOL 58 · ALGOL 60 · ALGOL 68 · ALGOL W · Alice ML · Alloy · Alma-0 · Alpine Abuild · AmbientTalk · AMDGPU · Amiga E · AMPL · Analitik · AngelScript · Angular2 · Answer Set Programming · ANSYS parametric design language · ANTLR · ANTLR With ActionScript Target · ANTLR With C# Target · ANTLR With CPP Target · ANTLR With Java Target · ANTLR With ObjectiveC Target · ANTLR With Perl Target · ANTLR With Python Target · ANTLR With Ruby Target · Apache Pig Latin · ApacheConf · Apex · APL · Apollo Guidance Computer · AppleScript · APT · Arc · Arduino · ARexx · ArnoldC · Arrow · Arturo · ASCII armored · ASL · ASN.1 · ASP.NET · AspectJ · aspx-cs · aspx-vb · Assembly · Asymptote · ATS · Augeas · AutoHotkey · AutoIt · Awk

</details>

<details>
<summary><strong>B — 46 cataloged names</strong></summary>

B (Formal Method) · B4X · Babbage · Ballerina · BAML · BARE · Base Makefile · Bash · Bash Session · BASIC · Batchfile · BBC Basic · BBCode · BC · BCPL · Bdd · BeanShell · Beef · Befunge · Berry · BETA · BibTeX · BibTeX Style · Bicep · Bison · BitBake · BLISS · BlitzBasic · BlitzMax · Blockly · BlooP · Blueprint · Bluespec · Bluespec BH · BNF · Boa · Boo · Boogie · Boomerang · Bosque · BQN · Brainfuck · BrighterScript · Brightscript · BST · BUGS

</details>

<details>
<summary><strong>C — 120 cataloged names</strong></summary>

C · C Shell · C# · C* · C++ · C-- · c-objdump · C/AL · C2hs Haskell · C3 · ca65 assembler · Cadence · cADL · Cairo · Cairo Zero · CameLIGO · CAmkES · Caml · Cangjie · CAP CDS · Cap'n Proto · CapDL · Carbon · CartoCSS · Catrobat · Cayenne · CBM BASIC V2 · CDDL · Cecil · CEEMAC · CESIL · Ceylon · CFEngine3 · cfstatement · ChaiScript · Chapel · Charity · Charmci · Cheetah · Chef · CHILL · CHIP-8 · ChucK · Cilk · Circom · Cirru · Claire · Clarion · Clarity · Classic ASP · Clay · Clean · Click · Clipper · CLIPS · CLIST · Clojure · ClojureScript · CLU · Clue · CMake · CMS-2 · COBOL · COBOLFree · CobolScript · Cobra · CodeQL · CoffeeScript · ColdFusion · ColdFusion CFC · Coldfusion HTML · COMAL · COMAL-80 · COMIT · Common Intermediate Language · Common Lisp · Common Workflow Language · COMPASS · Component Pascal · COMTRAN · Concurrent Pascal · Cool · CORAL 66 · COWSEL · CPL · cplint · cpp-objdump · CPSA · CQL · Crmsh · Croc · Cryptol · Crystal · Csound · Csound Document · Csound Orchestra · Csound Score · CSS · CSS+Django/Jinja · CSS+Genshi Text · CSS+Lasso · CSS+Mako · CSS+mozpreproc · CSS+Myghty · CSS+PHP · CSS+Ruby · CSS+Smarty · CSS+UL4 · Cuda · CUE · Cuneiform · Curl · Curry · CWeb · Cybil · Cyclone · Cycript · Cypher · Cython · Céu

</details>

<details>
<summary><strong>D — 42 cataloged names</strong></summary>

D · d-objdump · Dafny · Darcs Patch · Dart · Daslang · DASM16 · Datalog · DATATRIEVE · DataWeave · Dax · dBase · dc · DCL · Debian Control file · Debian Sourcelist · Debian Sources file · Delphi · DenizenScript · Desktop file · Devicetree · dg · Dhall · DIBOL · Diff · DIGITAL Command Language · DinkC · Django/Jinja · DM · Docker · Dockerfile · Dogescript · Draco · DRAKON · DTD · DTrace · Duel · Dune · Dylan · Dylan session · DylanLID · DYNAMO

</details>

<details>
<summary><strong>E — 43 cataloged names</strong></summary>

E · E-mail · Earl Grey · Earthly · Ease · Easy PL/I · Easytrieve · EASYTRIEVE PLUS · EBNF · eC · ECL · ECLiPSe · EdgeQL · Edinburgh IMP · EGL · Eiffel · ELAN · Elixir · Elixir iex session · Elm · Elpi · Elvish · Elvish Transcript · Emacs Lisp · EmacsLisp · Embedded Ragel · EmberScript · Emerald · Epigram · EQ · ERB · Erlang · Erlang erl session · Esterel · Etoys · Euclid · Euler · Euphoria · EusLisp · Evoque · EXEC 2 · execline · Ezhil

</details>

<details>
<summary><strong>F — 45 cataloged names</strong></summary>

F · F# · F* · Factor · FALSE · Fancy · Fantom · Faust · Felix · Fennel · FFP · Fift · Filebench WML · Filterscript · FIRRTL · fish · Fjölnir · FL · Flatline · Flavors · Flix · FlooP · FloScript · FLOW-MATIC · Fluent · FLUX · FOCAL · FOCUS · FOIL · FORMAC · Forth · Fortran · Fortran Free Form · FortranFixed · Fortress · FoxPro · FP · Franz Lisp · FreeBASIC · Freefem · FreeMarker · Frege · FStar · FunC · Futhark

</details>

<details>
<summary><strong>G — 50 cataloged names</strong></summary>

G-code · Game Maker Language · GAML · GAMS · GAP · GAP session · GAS · GCC Machine Description · GDB · GDScript · GDShader · Genero 4gl · Genie · Genshi · Genshi Text · Gentoo Ebuild · Gentoo Eclass · GEORGE · Gettext Catalog · Gherkin · Gleam · Glimmer JS · Glimmer TS · GLSL · Glyph · Gno · Gnuplot · Go · GOAL · GolfScript · Golo · GOM · GoodData-CL · GoogleSQL · Gosu · Gosu Template · GOTRAN · GPSS · Grace · Grammatical Framework · GraphQL · Graphviz · GRASS · Grasshopper · Groff · Groovy · Groovy Server Pages · GSC · GSQL · Gödel

</details>

<details>
<summary><strong>H — 49 cataloged names</strong></summary>

Hack · HAGGIS · HAL/S · Halide · Haml · Handlebars · Harbour · Hare · Hartmann pipelines · Haskell · Haxe · HCL · Hermes · Hexagony · Hexdump · High Level Assembly · HIP · HiveQL · HLSL · HolyC · hoon · Hop · Hope · Hopscotch · HSAIL · Hspec · HTML · HTML + Angular2 · HTML+Cheetah · HTML+Django/Jinja · HTML+Evoque · HTML+Genshi · HTML+Handlebars · HTML+Lasso · HTML+Mako · HTML+Myghty · HTML+PHP · HTML+Smarty · HTML+Twig · HTML+UL4 · HTML+Velocity · HTTP · Hume · Hurl · Hxml · Hy · Hybris · HyperTalk · HyPhy

</details>

<details>
<summary><strong>I — 28 cataloged names</strong></summary>

IBM RPG · Icon · IDL · Idris · Igor · IGOR Pro · IL Assembly · ImageJ Macro · Imba · ImHex Pattern Language · Inform · Inform 6 · Inform 6 template · Inform 7 · INI · Ink · Inno Setup · Instruction List · INTERCAL · Io · Ioke · IPython · IPython console session · IRC logs · Isabelle · Isabelle ROOT · ISLISP · ISPC

</details>

<details>
<summary><strong>J — 61 cataloged names</strong></summary>

J · J# · J++ · Jac · JADE · JAGS · Jai · JAL · Janet · Janus · Jasmin · JASS · Java · Java Server Page · Java Server Pages · Java Template Engine · JavaFX Script · JavaScript · JavaScript+Cheetah · JavaScript+Django/Jinja · JavaScript+ERB · JavaScript+Genshi Text · JavaScript+Lasso · JavaScript+Mako · Javascript+mozpreproc · JavaScript+Myghty · JavaScript+PHP · JavaScript+Ruby · JavaScript+Smarty · Javascript+UL4 · JCL · JEAN · Jelly · Jess · JetBrains MPS · JFlex · Jison · Jison Lex · JMESPath · Join Java · Jolie · JOSS · Joule · JOVIAL · Joy · jq · JSGF · JSLT · JSON · JSON-LD · JSON5 · JSONBareObject · JSONiq · Jsonnet · JSX · Julia · Julia console · Julia REPL · Just · Juttle · Jython

</details>

<details>
<summary><strong>K — 23 cataloged names</strong></summary>

K · Kaitai Struct · KakouneScript · Kal · Karel · KCL · Kconfig · KEE · KerboScript · Kernel log · KFramework · KIF · KiXtart · Kodu · Kojo · Koka · KoLmafia ASH · KornShell · Kotlin · KRC · KRL · Kuin · Kusto

</details>

<details>
<summary><strong>L — 56 cataloged names</strong></summary>

LabVIEW · Ladder · Lambdapi · Langium · LANSA · Lasso · LC-3 · LDAP configuration file · LDIF · Lean · Lean 4 · Lean4 · Leo · LessCss · Lex · LFE · Lighttpd configuration file · LigoLANG · LIL · LilyPond · Limbo · LINC · Linear Programming · Lingo · Linker Script · LINQ · liquid · Liquidsoap · Lisp · Literate Agda · Literate CoffeeScript · Literate Cryptol · Literate Haskell · Literate Idris · LiveCode · LiveCode Script · LiveScript · LLL · LLVM · LLVM-MIR · LLVM-MIR Body · Lobster · Logo · Logos · Logtalk · LOLCODE · LookML · LoomScript · LotusScript · LPC · LSE · LSL · Lua · Luau · Lucid · Lustre

</details>

<details>
<summary><strong>M — 89 cataloged names</strong></summary>

M · M4 · M4Sugar · Macaulay2 · Machine code · MAD · MAD/I · Magik · Magma · Makefile · Mako · Malbolge · Maple · MAPPER · MAQL · MARK-IV · Markdown · Mary · Mask · Mason · MATH-MATIC · Mathematica · Mathematical Programming System · MATLAB · Matlab session · Maude · Max · Maxima · MAXScript · mcfunction · MCSchema · MDL · MEL · Mercury · Mesa · Meson · Metal · MeTTa · Microcode · Microsoft Power Fx · MIIS · MIME · MIMIC · MiniD · MiniScript · MiniZinc · Mint · MIPS · Mirah · Miranda · mIRC Script · MIVA Script · ML · MLIR · Model 204 · Modelica · Modula · Modula-2 · Modula-3 · Module Management System · MoinMoin/Trac Wiki markup · Mojo · Monkey · Monkey C · Monte · MOO · Moocode · MoonBit · MoonScript · Mortran · Mosel · Motoko · Motorola 68K Assembly · Mouse · Move · mozhashpreproc · mozpercentpreproc · MPD · MQL · MQL4 · MQL5 · Mscgen · MSDOS Session · MUF · MUMPS · mupad · MXML · Myghty · MySQL

</details>

<details>
<summary><strong>N — 43 cataloged names</strong></summary>

Napier88 · Nasal · NASL · NASM · NCL · Nearley · Neko · NELIAC · Nemerle · nesC · NESL · NestedText · NetLinx · NetLinx+ERB · NetLogo · NetRexx · NewLisp · NEWP · Newspeak · NewtonScript · Nextflow · Nginx configuration file · Nial · Nickel · Nim · Nimrod · Nit · Nix · NMODL · Node.js REPL console session · Noir · Nord Programming Language · Notmuch · NQC · NSIS · Nu · Numba_IR · NumPy · Nushell · NuSMV · NWScript · NXC · NXT-G

</details>

<details>
<summary><strong>O — 47 cataloged names</strong></summary>

Oak · Oberon · OBJ2 · objdump · objdump-nasm · Object Lisp · Object Pascal · Object REXX · Objective-C · Objective-C++ · Objective-J · ObjectLOGO · ObjectScript · Obliq · OCaml · occam · occam-π · Octave · Odin · OMG Interface Definition Language · Omgrofl · OMNeT++ MSG · OMNeT++ NED · OmniMark · ooc · Ook! · Opa · Opal · Open Policy Agent · OpenCL · OpenEdge ABL · OpenQASM · OpenRC runscript · OpenSCAD · OPL · OPS5 · OptimJ · Orc · ORCA/Modula-2 · Org Mode · Oriel · Orwell · OverpassQL · OverPy · Ox · Oxygene · Oz

</details>

<details>
<summary><strong>P — 111 cataloged names</strong></summary>

P · P4 · PacmanConf · Pact · Pan · Papyrus · ParaSail · PARI/GP · Parrot · Parrot Assembly · Parrot Internal Representation · Pascal · Pascal Script · Pawn · PCASTL · PCF · PDDL · PDL · PEARL · PEG · PEG.js · PeopleCode · Pep8 · Perl · Perl6 · Pharo · Phix · PHP · Pico · PicoLisp · Pict · Piet · Pig · PigLatin · Pike · PILOT · Pizza · PkgConfig · Pkl · PL-11 · PL/0 · PL/B · PL/C · PL/I · PL/M · PL/P · PL/pgSQL · PL/S · PL/SQL · PL360 · PLANC · Plankalkül · Planner · PLEX · PLEXIL · PLpgSQL · PLSQL · Plus · PogoScript · Pointless · Polar · Pony · POP-11 · POP-2 · PortablE · Portugol · POSIX sh (Dash) · PostgreSQL console (psql) · PostgreSQL EXPLAIN dialect · PostgreSQL SQL dialect · PostScript · POV-Ray SDL · POVRay · Power Query · PowerBuilder · PowerShell · PowerShell Session · Praat · Pro*C · Processing · Procfile · Prograph · Project Verona · Prolog · PROMAL · Promela · PromQL · Propeller Spin · Properties · PROSE · PROTEL · Protocol Buffer · PRQL · PsySH console session for PHP · PTX · Pug · Puppet · Pure · Pure Data · PureBasic · PureScript · PyPy Log · Pyret · Python · Python 2.x · Python 2.x Traceback · Python console · Python console session · Python Traceback · Python+UL4 · P′′

</details>

<details>
<summary><strong>Q — 16 cataloged names</strong></summary>

q · Q# · Qalb · QBasic · Qlik · QMake · QML · QPL · Qt Script · QtScript · Quake · QuakeC · Quantum Computation Language · QuickBASIC · Quint · QVTO

</details>

<details>
<summary><strong>R — 65 cataloged names</strong></summary>

R · R++ · Racket · Ragel · Ragel in C Host · Ragel in CPP Host · Ragel in D Host · Ragel in Java Host · Ragel in Objective C Host · Ragel in Ruby Host · Raku · RAPID · Rapira · Rascal · RAScript · Ratfiv · Ratfor · Raw token data · rc · RConsole · Rd · REALbasic · Reason · ReasonLIGO · ReasonML · Rebol · Red · Redcode · Redscript · REFAL · reg · Rego · Relax-NG Compact · Rell · Ren'Py · RenderScript · ReScript · ResourceBundle · reStructuredText · REXX · Rez · RHTML · Ride · Ring · Rita · Roboconf Graph · Roboconf Instances · RobotFramework · Roc · Rockstar · Rocq · Rocq Prover · Rouge · RouterOS Script · RPC · RPG · RPGLE · RPL · RPMSpec · RQL · RSL · RTL/2 · Ruby · Ruby irb session · Rust

</details>

<details>
<summary><strong>S — 125 cataloged names</strong></summary>

S · S-Lang · S-PLUS · S/SL · S2 · S3 · SA-C · SabreTalk · Sage · Sail · SAKO · Salt · SARL · SAS · SASL · Sass · Sather · Savi · Sawzall · SBL · Scala · Scalate Server Page · Scaml · scdoc · Scenic · Scheme · Scilab · Scratch · ScratchJr · Script.NET · SCSS · sed · Seed7 · Self · SenseTalk · SequenceL · Serpent · SETL · ShaderLab · Shakespeare Programming Language · Shell · ShellSession · Shen · ShExC · Short Code · Sieve · SIGNAL · Silver · SiMPLE · SIMPOL · SIMSCRIPT · Simula · Simulink · Singularity · SISAL · SKILL · Slang · Slash · Slice · Slim · SLIP · Slurm · Smali · SMALL · Smalltalk · SmartGameFormat · Smarty · Smithy · SML · SmPL · SMT · Snakemake · Snap! · SNBT · Snobol · Snowball · SOL · Solidity · Soong · SOPHAEROS · Sophia · Source · SourcePawn · SP/k · SPARK · SPARQL · Speakeasy · Speedcode · Spice · SPIN · SPITBOL · SPL · SPS · SQF · SQL · SQL+Jinja · sqlite3con · SQLPL · SQR · Squeak · SquidConf · Squirrel · SR · Srcinfo · Stan · Standard ML · Starlark · Starlogo · Stata · Stateflow · Strand · Strongtalk · Structured Text · Subtext · SuperCollider · Superplan · SuperTalk · SurrealQL · Sway · Swift · SWIG · SYCL · SYMPL · Systemd · SystemVerilog

</details>

<details>
<summary><strong>T — 63 cataloged names</strong></summary>

T · TableGen · TACL · Tact · TADS · TADS 3 · Tal · Talon · TAP · Tape · TASM · Tcl · Tcsh · Tcsh Session · Tea · Teal · TECO · TELCOMP · Tera Term macro · Termcap · Terminfo · Terra · Terraform · TeX · Text only · Text output · ThingsDB · Thrift · TI Program · tiddler · Tl-b · TL-Verilog · TLA · TLS Presentation Language · TMG · Todotxt · Toit · Tolk · Tom · TOML · TPU · TRAC · TrafficScript · Transact-SQL · Tree-sitter Query · Treetop · TSQL · TSX · TTCN · TTM · Turing · Turtle · TUTOR · Twig · TXL · Tynker · TypeScript · TypeSpec · Typographic Number Theory · TypoScript · TypoScriptCssData · TypoScriptHtmlData · Typst

</details>

<details>
<summary><strong>U — 19 cataloged names</strong></summary>

Ubercode · ucode · UCSD Pascal · UL4 · Umple · Unicon · Uniface · Unified Parallel C · UNITY · Unix Assembly · Unix/Linux config files · Unlambda · Uno · UnrealScript · Untyped Plutus Core · UrbiScript · urlencoded · UrWeb · USD

</details>

<details>
<summary><strong>V — 30 cataloged names</strong></summary>

V · Vala · VB.net · VBA · VBScript · VCL · VCLSnippets · VCTreeStatus · Velocity · Verifpal · Verilog · Verse · VGL · VHDL · Vim Script · VimL · Viper · Visual Basic .NET · Visual Basic 6.0 · Visual DataFlex · Visual DialogScript · Visual FoxPro · Visual J++ · Visual LISP · Visual Objects · Visual Prolog · Visual Prolog Grammar · Volt · Vue · Vyper

</details>

<details>
<summary><strong>W — 19 cataloged names</strong></summary>

WATFIV · WATFOR · WDiff · WDL · Web IDL · WebAssembly · WebGPU Shading Language · WebIDL · WGSL · Whiley · Whitespace · Wikitext · wisp · Witcher Script · Wolfram Language · Wollok · World of Warcraft TOC · Wren · Wyvern

</details>

<details>
<summary><strong>X — 34 cataloged names</strong></summary>

X++ · X10 · xBase · XBL · XC · XL · Xmake · XML · XML+Cheetah · XML+Django/Jinja · XML+Evoque · XML+Lasso · XML+Mako · XML+Myghty · XML+PHP · XML+Ruby · XML+Smarty · XML+UL4 · XML+Velocity · Xod · Xojo · Xonsh · Xorg · XOTcl · XPL · XPL0 · XProc · XQuery · XS · XSB · XSLT · Xtend · xtlang · XUL+mozpreproc

</details>

<details>
<summary><strong>Y — 8 cataloged names</strong></summary>

Yacc · YAML · YAML+Jinja · YANG · YARA · Yorick · YQL · Yul

</details>

<details>
<summary><strong>Z — 14 cataloged names</strong></summary>

Z shell · Z++ · ZAP · Zeek · ZenScript · Zephir · ZetaLisp · Zig · ZIL · Zimpl · Zone · Zonnon · ZOPL · ZPL

</details>

<!-- LANGUAGE-CATALOG:END -->

## Project Structure

```text
Language-Project/
├── Language.py
├── install.sh
├── uninstall.sh
├── languages.json                 # executable worker registry
├── languages/                     # real worker source files only
├── catalog/
│   ├── known_languages.json       # global catalog snapshot
│   ├── SOURCES.md
│   └── languages/                 # one metadata JSON per cataloged name
├── core/
│   ├── engine.py
│   ├── registry.py
│   └── catalog.py
├── scripts/
│   ├── setup.py
│   ├── refresh_catalog.py
│   ├── verify_manifest.py
│   └── quick-test.sh
├── docs/
│   ├── ARCHITECTURE.md
│   └── BENCHMARKING.md
├── build/
├── state/
├── results/
├── README.md
├── SECURITY.md
├── CONTRIBUTING.md
└── LICENSE
```

## Accuracy Rule

Language Project never labels the global catalog as “all languages proven runnable in Termux.” Those are different claims. The catalog aims for broad, refreshable world coverage; the execution engine is conservative and only activates workers that pass on the device.
