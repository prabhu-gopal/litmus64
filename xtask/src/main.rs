//! SPDX-License-Identifier: FSL-1.1-ALv2
//!
//! Repo automation. Every task here is also a CI step, so `cargo xtask check`
//! reproduces CI locally in the same order.

fn main() {
    // Tasks (CODEBASE.md §10, §14):
    //   check             everything CI runs, in CI order
    //   arch-check        §2 dependency laws: verdict ⊥ llm, no std::process
    //                     outside lx-sandbox, no T1 crate depends on T2+
    //   schema-gen        regenerate spec/receipt-v0.1.schema.json + plugin schema
    //   schema-check      assert generated schema matches the committed one
    //   capability-check  assert `lx capabilities` matches spec/capability.md
    //   conformance       run spec/conformance/**
    //   determinism       run every fixture twice, assert byte-identical
    //   license-check     SPDX header matches the LICENSING.md tier table
    //   corpus sync       fetch benchmark repos by URL + commit (never vendored)
    //   dogfood           lx check on this repo, commit the receipt to examples/
    //   bench             Litmus64-Bench
    unimplemented!("xtask")
}
