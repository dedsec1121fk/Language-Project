# Diagnostics

`language-project doctor` performs non-destructive checks for the Termux package manager, Python, project write permissions, safe private-storage placement, runtime state, manifest integrity, and a live round-trip against one verified worker when possible. It also prints the device snapshot used by benchmark reports.

`language-project setup --install` is the repair/re-detection path. It may install packages and rebuild workers, so Doctor is intentionally kept separate.
