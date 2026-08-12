# Reproducibility

For meaningful comparisons, use the same device, Termux package versions, payload, worker set, warm-up count, benchmark mode, and profile. Android scheduler activity, thermal throttling, battery state, background applications, and VM garbage collection can all affect wall-clock timings.

Language Project records a device snapshot and richer distribution statistics because a single fastest sample is not representative. For repeated testing, prefer median and P95 values and compare multiple sessions with `language-project compare`.

The `stress` mode uses a supplied random seed so its generated binary payload sequence can be reproduced.
