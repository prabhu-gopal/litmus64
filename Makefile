.PHONY: dev check fmt lint test conformance determinism demo

dev:            ## one command, no README archaeology
	@bash .devcontainer/setup.sh

check:          ## everything CI runs, in CI order
	cargo xtask check

fmt:
	cargo fmt --all
lint:
	cargo clippy --workspace --all-targets --all-features -- -D warnings
test:
	cargo test --workspace --all-features
conformance:
	cargo xtask conformance
determinism:
	cargo xtask determinism
demo:
	cargo run -p lx-cli -- demo
