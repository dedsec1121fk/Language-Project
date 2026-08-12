# Resumable Checkpoint Chains

`language-project checkpoint` is a reliability-oriented execution mode. Unlike the high-speed persistent chain, it writes an atomic JSON checkpoint after each successful language stage.

The checkpoint stores:

- session ID,
- original payload in hex,
- original SHA-256,
- current transformed payload,
- exact language order,
- encode/decode phase,
- next stage index,
- completed-stage timing records,
- status and timestamps.

If the Termux session closes, Android kills the process, or the user intentionally stops the run, resume with:

```bash
language-project resume state/checkpoints/<session>.json
```

For testing the mechanism without killing Termux:

```bash
language-project checkpoint --text "resume me" --stop-after 5
language-project checkpoints
language-project resume state/checkpoints/<session>.json
```

Checkpoint mode starts a worker for each stage independently. That is slower than the prewarmed benchmark chain by design; its purpose is recoverability, not peak throughput.
