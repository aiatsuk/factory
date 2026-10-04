#!/usr/bin/env python3
"""Release helper: read the version, check a tag against it, print release notes.

Usage:
  python3 scripts/release.py version
  python3 scripts/release.py check --tag vX.Y.Z
  python3 scripts/release.py notes --tag vX.Y.Z
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Every version location kept in sync (see ai-factory.json update.versionLocations).
# Each entry is (file, JSON key path). The first entry is the primary version file.
VERSION_FILES: list[tuple[str, tuple[object, ...]]] = [
    ("ai-factory.json", ("package", "version")),
    (".codex-plugin/plugin.json", ("version",)),
    (".claude-plugin/plugin.json", ("version",)),
    (".claude-plugin/marketplace.json", ("plugins", 0, "version")),
]

# The release tag recorded in the metadata, which must equal "v" + version.
RELEASE_TAG_FILE: tuple[str, tuple[object, ...]] = ("ai-factory.json", ("package", "releaseTag"))

CHANGELOG = "CHANGELOG.md"
TAG_RE = re.compile(r"^v(\d+\.\d+\.\d+)$")


class ReleaseError(Exception):
    pass


def read_json_value(root: Path, file_name: str, keys: tuple[object, ...]) -> object:
    path = root / file_name
    try:
        value: object = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ReleaseError(f"{file_name}: file not found") from None
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"{file_name}: invalid JSON ({exc})") from None
    for key in keys:
        try:
            value = value[key]  # type: ignore[index]
        except (KeyError, IndexError, TypeError):
            pointer = "/".join(str(k) for k in keys)
            raise ReleaseError(f"{file_name}: missing /{pointer}") from None
    return value


def primary_version(root: Path) -> str:
    file_name, keys = VERSION_FILES[0]
    return str(read_json_value(root, file_name, keys))


def parse_tag(tag: str) -> str:
    match = TAG_RE.match(tag)
    if not match:
        raise ReleaseError(f"tag {tag!r} is not of the form vX.Y.Z")
    return match.group(1)


def changelog_section(root: Path, version: str) -> str:
    path = root / CHANGELOG
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise ReleaseError(f"{CHANGELOG}: file not found") from None
    heading = f"## {version} — "
    start = None
    for index, line in enumerate(lines):
        if line.startswith(heading):
            start = index + 1
            break
    if start is None:
        raise ReleaseError(f"{CHANGELOG}: no '## {version} — ' section")
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    body = "\n".join(lines[start:end]).strip("\n")
    if not body.strip():
        raise ReleaseError(f"{CHANGELOG}: section {version} is empty")
    return body + "\n"


def check(root: Path, tag: str) -> list[str]:
    version = parse_tag(tag)
    problems: list[str] = []
    for file_name, keys in VERSION_FILES:
        try:
            found = read_json_value(root, file_name, keys)
        except ReleaseError as exc:
            problems.append(str(exc))
            continue
        if found != version:
            problems.append(f"{file_name}: version {found!r}, expected {version!r}")
    file_name, keys = RELEASE_TAG_FILE
    try:
        found_tag = read_json_value(root, file_name, keys)
        if found_tag != tag:
            problems.append(f"{file_name}: releaseTag {found_tag!r}, expected {tag!r}")
    except ReleaseError as exc:
        problems.append(str(exc))
    try:
        changelog_section(root, version)
    except ReleaseError as exc:
        problems.append(str(exc))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="print the current version")
    for name, text in (("check", "verify version files and changelog"), ("notes", "print release notes")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("--tag", required=True, help="release tag, vX.Y.Z")
    args = parser.parse_args(argv)
    root: Path = args.root

    try:
        if args.command == "version":
            print(primary_version(root))
        elif args.command == "check":
            problems = check(root, args.tag)
            if problems:
                print(f"release check failed for {args.tag}:", file=sys.stderr)
                for problem in problems:
                    print(f"  - {problem}", file=sys.stderr)
                return 1
            print(f"release check passed for {args.tag}")
        else:
            sys.stdout.write(changelog_section(root, parse_tag(args.tag)))
    except ReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
