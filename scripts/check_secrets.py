"""Triagem do historico Git, sem imprimir valores de segredos. Nao e auditoria."""
import re
import subprocess
import sys

PATTERNS = {
    "github_token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    "github_pat": re.compile(rb"github_pat_[A-Za-z0-9_]{50,}"),
    "google_api_key": re.compile(rb"AIza[A-Za-z0-9_-]{30,}"),
    "aws_access_key": re.compile(rb"AKIA[A-Z0-9]{16}"),
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "url_with_password": re.compile(rb"https?://[^\s/:]+:[^\s/@]+@"),
}


def git(*arguments):
    result = subprocess.run(["git", *arguments], capture_output=True, check=True, timeout=60, shell=False)
    return result.stdout


def main():
    objects = git("rev-list", "--objects", "--all").splitlines()
    checked = 0
    findings = []
    for item in objects:
        object_id = item.split(b" ", 1)[0].decode("ascii")
        if git("cat-file", "-t", object_id).strip() != b"blob":
            continue
        data = git("cat-file", "blob", object_id)
        checked += 1
        for label, pattern in PATTERNS.items():
            if pattern.search(data):
                findings.append((object_id, label))
    if findings:
        for object_id, label in findings:
            print("BLOCKED", object_id, label, "[REDACTED]")
        return 1
    print("No matching credential patterns in", checked, "reachable Git blobs. Not a security audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
