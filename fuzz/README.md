# Fuzz targets

`cargo-fuzz`. Targets are added under `fuzz_targets/` as each parser lands.

Planned: receipt parsing · canonical JSON (JCS) · the AST diff engine · policy evaluation · the
plugin JSON contract.

The bar is narrow and absolute: **these must never panic.** A verification tool that crashes on
hostile input has failed at its own premise, and a panic in receipt parsing is reachable from any
untrusted diff.
