"""SECRET-1 falsifiability: prove the gitleaks scan can actually detect.

The CI job (validate.yml `secret-scan`) runs `gitleaks detect --no-git` over
the tree, which should always pass on a healthy repo — so on its own it never
demonstrates that detection works. This test seeds a syntactically valid,
high-entropy GitHub PAT shape into a temp dir and asserts gitleaks flags it
(exit 1), plus the inverse (clean dir scans clean, exit 0).

Skips cleanly when no gitleaks binary is on PATH (local machines); CI for
this suite runs on the same runner class that has the pinned binary when the
secret-scan job provides it, and the seeded-detection contract was verified
against gitleaks 8.30.1 at introduction time.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import tempfile
import unittest

GITLEAKS = shutil.which("gitleaks")

# Shape-valid GitHub PAT: ghp_ + exactly 36 high-entropy alphanumerics.
# gitleaks filters low-entropy strings, so this must not use repetition.
FAKE_PAT = "ghp_" + "w9Xk2mQp7vRt4nLs8bYf3cZh6dJg1aEu5oIz"
assert len(FAKE_PAT) == 40


def _scan(path: pathlib.Path) -> int:
    return subprocess.run(
        [GITLEAKS, "detect", "--source", str(path), "--no-git", "--exit-code", "1"],
        capture_output=True,
    ).returncode


@unittest.skipUnless(GITLEAKS, "gitleaks not on PATH")
class TestSecretScan(unittest.TestCase):
    def test_seeded_secret_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "config.env").write_text(f'token = "{FAKE_PAT}"\n')
            self.assertEqual(_scan(pathlib.Path(d)), 1)

    def test_clean_dir_scans_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "notes.md").write_text("nothing secret here\n")
            self.assertEqual(_scan(pathlib.Path(d)), 0)


if __name__ == "__main__":
    unittest.main()
