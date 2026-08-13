dnl Language Project Termux field guide for M4
dnl Module id m4
dnl Official Termux package set m4
dnl Runtime command m4
dnl GitHub Linguist group M4
dnl Purpose practical implementation guidance and reusable design notes for this language module
dnl This file is source level reference material stored beside the practical tools so each language remains a substantive part of the repository
dnl 
dnl M4 recipe group 1 Safe file inspection
dnl Task 001 Open inputs read only first and report clear errors for missing or inaccessible paths.
dnl Task 002 Stream large files in bounded chunks so the utility stays usable on memory constrained Android devices.
dnl Task 003 Report byte count line count and a stable content digest without changing the source file.
dnl Task 004 Treat arbitrary input as bytes unless the operation explicitly requires UTF 8 text.
dnl Check 1 Safe file inspection output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Integrity and verification
dnl Task 005 Use SHA 256 for persistent file integrity and keep non cryptographic fingerprints clearly labeled supplemental.
dnl Task 006 Verify destination size and digest after copy backup archive extraction or restoration.
dnl Task 007 Use temporary output followed by atomic rename when replacing an existing file.
dnl Task 008 Record runtime and compiler versions when producing results intended for later comparison.
dnl Check 1 Integrity and verification output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Text processing
dnl Task 009 Support line counting word counting whitespace checks and deterministic filtering without network access.
dnl Task 010 Preserve newline style unless the user explicitly requests normalization.
dnl Task 011 When normalizing text make the intended UTF 8 and LF or CRLF policy visible in the report.
dnl Task 012 For searches return path line number and a stable match representation suitable for scripts.
dnl Check 1 Text processing output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Structured data
dnl Task 013 Validate JSON CSV TSV or configuration input before writing transformed output.
dnl Task 014 Keep a no modification validation mode so a file can be checked safely before conversion.
dnl Task 015 Prefer machine readable output for aggregation by the Language Project control plane.
dnl Task 016 Reject malformed records explicitly instead of silently dropping fields.
dnl Check 1 Structured data output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Project analysis
dnl Task 017 Count files bytes and source lines by extension while skipping build cache and version control directories.
dnl Task 018 Scan for TODO FIXME HACK BUG and NOTE markers and preserve file and line context.
dnl Task 019 Summarize the largest files and duplicate candidates before any cleanup action is offered.
dnl Task 020 Keep analysis deterministic so two runs on unchanged source can be compared directly.
dnl Check 1 Project analysis output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Backup and restore
dnl Task 021 Create backups under HOME Language Project backups rather than inside the Git checkout.
dnl Task 022 Include a manifest with relative paths sizes and SHA 256 values for important backups.
dnl Task 023 Validate archive member paths before extraction to prevent traversal outside the destination.
dnl Task 024 Never report a backup healthy until its container and expected file digests verify.
dnl Check 1 Backup and restore output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Termux integration
dnl Task 025 Store generated files only beneath HOME Language Project using build state results reports cache tmp downloads backups bundles or workspace.
dnl Task 026 Do not require root privileges for ordinary Language Project features.
dnl Task 027 Detect the real runtime on the current device and disable only the unavailable module instead of failing the project.
dnl Task 028 Keep package installation explicit and use the official Termux package name recorded by the registry.
dnl Check 1 Termux integration output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Performance work
dnl Task 029 Use monotonic clocks for elapsed time and wall clock timestamps only for human facing session metadata.
dnl Task 030 Warm persistent workers before latency comparisons so interpreter startup does not dominate tiny workloads.
dnl Task 031 Report median percentile minimum maximum mean and throughput when enough samples exist.
dnl Task 032 Bound parallelism to available CPU and memory instead of spawning an unbounded process set.
dnl Check 1 Performance work output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Cross language workflows
dnl Task 033 Keep transform protocols deterministic so another verified language can independently validate the result.
dnl Task 034 Use length prefixed or line safe machine protocols and never interpret user benchmark text as source code.
dnl Task 035 Make every reversible transform provide an exact inverse and confirm byte perfect round trip recovery.
dnl Task 036 When a runtime fails mid workflow record the failure and use the project recovery policy rather than hiding the error.
dnl Check 1 Cross language workflows output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Security boundaries
dnl Task 037 Benchmark input is opaque data and must never be evaluated simply because it resembles code.
dnl Task 038 Trusted source execution is a separate opt in command and should use argument arrays rather than shell interpolation.
dnl Task 039 Network helpers should default to bounded timeouts and explicit destinations.
dnl Task 040 Potentially destructive operations use preview mode unless the user supplies the documented apply option.
dnl Check 1 Security boundaries output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Diagnostics
dnl Task 041 Return nonzero status on real failure and keep diagnostics concise enough to understand from a phone terminal.
dnl Task 042 Expose runtime package command and module identity in self tests.
dnl Task 043 Keep stdout stable for automation and send verbose diagnostics to stderr where practical.
dnl Task 044 A doctor check should inspect state without creating generated files beside repository source.
dnl Check 1 Diagnostics output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 1 Portable design
dnl Task 045 Quote paths because Android storage names can contain spaces and non ASCII characters.
dnl Task 046 Do not assume GNU desktop filesystem paths when HOME and PREFIX already describe the Termux environment.
dnl Task 047 Prefer standard library capabilities before adding a heavy dependency for a small utility.
dnl Task 048 Make optional acceleration improve speed without changing correctness of the fallback path.
dnl Check 1 Portable design output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Safe file inspection
dnl Task 049 Open inputs read only first and report clear errors for missing or inaccessible paths.
dnl Task 050 Stream large files in bounded chunks so the utility stays usable on memory constrained Android devices.
dnl Task 051 Report byte count line count and a stable content digest without changing the source file.
dnl Task 052 Treat arbitrary input as bytes unless the operation explicitly requires UTF 8 text.
dnl Check 2 Safe file inspection output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Integrity and verification
dnl Task 053 Use SHA 256 for persistent file integrity and keep non cryptographic fingerprints clearly labeled supplemental.
dnl Task 054 Verify destination size and digest after copy backup archive extraction or restoration.
dnl Task 055 Use temporary output followed by atomic rename when replacing an existing file.
dnl Task 056 Record runtime and compiler versions when producing results intended for later comparison.
dnl Check 2 Integrity and verification output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Text processing
dnl Task 057 Support line counting word counting whitespace checks and deterministic filtering without network access.
dnl Task 058 Preserve newline style unless the user explicitly requests normalization.
dnl Task 059 When normalizing text make the intended UTF 8 and LF or CRLF policy visible in the report.
dnl Task 060 For searches return path line number and a stable match representation suitable for scripts.
dnl Check 2 Text processing output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Structured data
dnl Task 061 Validate JSON CSV TSV or configuration input before writing transformed output.
dnl Task 062 Keep a no modification validation mode so a file can be checked safely before conversion.
dnl Task 063 Prefer machine readable output for aggregation by the Language Project control plane.
dnl Task 064 Reject malformed records explicitly instead of silently dropping fields.
dnl Check 2 Structured data output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Project analysis
dnl Task 065 Count files bytes and source lines by extension while skipping build cache and version control directories.
dnl Task 066 Scan for TODO FIXME HACK BUG and NOTE markers and preserve file and line context.
dnl Task 067 Summarize the largest files and duplicate candidates before any cleanup action is offered.
dnl Task 068 Keep analysis deterministic so two runs on unchanged source can be compared directly.
dnl Check 2 Project analysis output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Backup and restore
dnl Task 069 Create backups under HOME Language Project backups rather than inside the Git checkout.
dnl Task 070 Include a manifest with relative paths sizes and SHA 256 values for important backups.
dnl Task 071 Validate archive member paths before extraction to prevent traversal outside the destination.
dnl Task 072 Never report a backup healthy until its container and expected file digests verify.
dnl Check 2 Backup and restore output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Termux integration
dnl Task 073 Store generated files only beneath HOME Language Project using build state results reports cache tmp downloads backups bundles or workspace.
dnl Task 074 Do not require root privileges for ordinary Language Project features.
dnl Task 075 Detect the real runtime on the current device and disable only the unavailable module instead of failing the project.
dnl Task 076 Keep package installation explicit and use the official Termux package name recorded by the registry.
dnl Check 2 Termux integration output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Performance work
dnl Task 077 Use monotonic clocks for elapsed time and wall clock timestamps only for human facing session metadata.
dnl Task 078 Warm persistent workers before latency comparisons so interpreter startup does not dominate tiny workloads.
dnl Task 079 Report median percentile minimum maximum mean and throughput when enough samples exist.
dnl Task 080 Bound parallelism to available CPU and memory instead of spawning an unbounded process set.
dnl Check 2 Performance work output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Cross language workflows
dnl Task 081 Keep transform protocols deterministic so another verified language can independently validate the result.
dnl Task 082 Use length prefixed or line safe machine protocols and never interpret user benchmark text as source code.
dnl Task 083 Make every reversible transform provide an exact inverse and confirm byte perfect round trip recovery.
dnl Task 084 When a runtime fails mid workflow record the failure and use the project recovery policy rather than hiding the error.
dnl Check 2 Cross language workflows output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Security boundaries
dnl Task 085 Benchmark input is opaque data and must never be evaluated simply because it resembles code.
dnl Task 086 Trusted source execution is a separate opt in command and should use argument arrays rather than shell interpolation.
dnl Task 087 Network helpers should default to bounded timeouts and explicit destinations.
dnl Task 088 Potentially destructive operations use preview mode unless the user supplies the documented apply option.
dnl Check 2 Security boundaries output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Diagnostics
dnl Task 089 Return nonzero status on real failure and keep diagnostics concise enough to understand from a phone terminal.
dnl Task 090 Expose runtime package command and module identity in self tests.
dnl Task 091 Keep stdout stable for automation and send verbose diagnostics to stderr where practical.
dnl Task 092 A doctor check should inspect state without creating generated files beside repository source.
dnl Check 2 Diagnostics output remains deterministic local recoverable and compatible with the current Termux runtime
dnl M4 recipe group 2 Portable design
dnl Task 093 Quote paths because Android storage names can contain spaces and non ASCII characters.
dnl Task 094 Do not assume GNU desktop filesystem paths when HOME and PREFIX already describe the Termux environment.
dnl Task 095 Prefer standard library capabilities before adding a heavy dependency for a small utility.
dnl Task 096 Make optional acceleration improve speed without changing correctness of the fallback path.
dnl Check 2 Portable design output remains deterministic local recoverable and compatible with the current Termux runtime

dnl Language Project field guide continues through module tools and examples
