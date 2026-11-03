# SPDX-License-Identifier: MIT
"""Pinned upstream API metadata. No live catalog lookup at runtime."""
from .forge import Asset

# tool, Rust target, approved archive size, upstream API SHA-256
ROWS = [
    ("rg", "aarch64-unknown-linux-gnu", 1869959, "2b661c6ef508e902f388e9098d9c4c5aca72c87b55922d94abdba830b4dc885e"),
    ("rg", "x86_64-unknown-linux-musl", 2263077, "1c9297be4a084eea7ecaedf93eb03d058d6faae29bbc57ecdaf5063921491599"),
    ("rg", "aarch64-apple-darwin", 1777930, "378e973289176ca0c6054054ee7f631a065874a352bf43f0fa60ef079b6ba715"),
    ("rg", "x86_64-apple-darwin", 1894127, "64811cb24e77cac3057d6c40b63ac9becf9082eedd54ca411b475b755d334882"),
    ("rg", "aarch64-pc-windows-msvc", 1675460, "00d931fb5237c9696ca49308818edb76d8eb6fc132761cb2a1bd616b2df02f8e"),
    ("rg", "x86_64-pc-windows-msvc", 1810687, "124510b94b6baa3380d051fdf4650eaa80a302c876d611e9dba0b2e18d87493a"),
    ("fd", "aarch64-unknown-linux-gnu", 1575492, "66f297e404400a3358e9a0c0b2f3f4725956e7e4435427a9ae56e22adbe73a68"),
    ("fd", "x86_64-unknown-linux-gnu", 1710062, "c3c2bc79f838e780173fc8f18b337ec273e7ba17c7ff8f551be29fc3c19b7916"),
    ("fd", "aarch64-unknown-linux-musl", 1608477, "996b9b1366433b211cb3bbedba91c9dbce2431842144d925428ead0adf32020b"),
    ("fd", "x86_64-unknown-linux-musl", 1759301, "2b6bfaae8c48f12050813c2ffe1884c61ea26e750d803df9c9114550a314cd14"),
    ("fd", "aarch64-apple-darwin", 1337349, "0570263812089120bc2a5d84f9e65cd0c25e4a4d724c80075c357239c74ae904"),
    ("fd", "x86_64-apple-darwin", 1430203, "50d30f13fe3d5914b14c4fff5abcbd4d0cdab4b855970a6956f4f006c17117a3"),
    ("fd", "aarch64-pc-windows-msvc", 1416342, "bf9b1e31bcac71c1e95d49c56f0d872f525b95d03854e94b1d4dd6786f825cc5"),
    ("fd", "x86_64-pc-windows-msvc", 1490905, "318aa2a6fa664325933e81fda60d523fff29444129e91ebf0726b5b3bcd8b059"),
]

CATALOG = {}
for tool, triple, size, digest in ROWS:
    windows = "windows" in triple
    arch = triple.split("-", 1)[0]
    system = "windows" if windows else ("darwin" if "apple" in triple else ("linux-musl" if "musl" in triple else "linux-glibc"))
    key = system + "-" + arch
    version = "15.1.0" if tool == "rg" else "v10.3.0"
    name = ("ripgrep-" if tool == "rg" else "fd-") + version + "-" + triple
    extension = ".zip" if windows else ".tar.gz"
    repo = "BurntSushi/ripgrep" if tool == "rg" else "sharkdp/fd"
    asset = Asset("https://github.com/" + repo + "/releases/download/" + version + "/" + name + extension, digest, version)
    CATALOG.setdefault(tool, {})[key] = (asset, size, name + "/" + tool + (".exe" if windows else ""))
# Upstream publishes its static musl x86_64 build for glibc Linux as well.
CATALOG["rg"]["linux-glibc-x86_64"] = CATALOG["rg"]["linux-musl-x86_64"]
