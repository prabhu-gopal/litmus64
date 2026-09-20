#!/usr/bin/env python3
"""Deterministic fixture "test suite" run by the template plugin's
existing_suite task. Not a real test framework -- it exists so the plugin
has something real to execute without depending on any external toolchain.
"""


def add(a, b):
    return a + b


def is_palindrome(s):
    return s == s[::-1]


CHECKS = [
    ("add(2, 2) == 4", add(2, 2) == 4),
    ("add(-1, 1) == 0", add(-1, 1) == 0),
    ("is_palindrome('level')", is_palindrome("level")),
]


def main() -> int:
    passed = sum(1 for _, ok in CHECKS if ok)
    total = len(CHECKS)
    for name, ok in CHECKS:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
    print(f"RESULT: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
