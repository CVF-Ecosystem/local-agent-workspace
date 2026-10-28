#!/usr/bin/env python3
"""Read-only storage audit for loose Python scripts; Python 3.8+, standard library.

No inspected script is imported or executed. No file is written or moved.
Exit 0: no directory exceeds --max-loose within scanned scope; 1: exceeded;
2: invalid input or incomplete inspection. This is not a safety/content audit.
"""
import argparse
import hashlib
import os
import re
import stat
import sys


ROOT_SKIP = {
    "skills", "tools", ".agent", ".cvf", "en", "archive", "tests", "roadmap",
    "packs", "release_templates", "dist",
}
STORAGE_SKIP = {
    "scripts", "_scratch", "_nguon_dung", "__pycache__", ".git",
    ".venv", "venv", "node_modules",
}
ONCE = re.compile(
    r"(^|_)(inspect|check|test|tmp|temp|debug|try|scratch|probe|dump)(_|\.|$)",
    re.I,
)
REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def plain_stat(path):
    """Reject links/reparse points without resolving their targets."""
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or (
        getattr(info, "st_file_attributes", 0) & REPARSE_POINT
    ):
        raise OSError("link/reparse point not inspected")
    return info


def checked_root(folder):
    # Keep '..' until after checking ancestors: normpath first could hide a link.
    path = os.path.join(os.getcwd(), os.fspath(folder))
    pending = path
    while True:
        info = plain_stat(pending)
        if not stat.S_ISDIR(info.st_mode):
            raise OSError("root/ancestor is not a directory")
        parent = os.path.dirname(pending)
        if parent == pending or not parent:
            break
        pending = parent
    return os.path.abspath(path)


def fingerprint(path):
    """Read bytes only. Rechecks reduce mistakes; this is not a race-proof boundary."""
    before = plain_stat(path)
    if not stat.S_ISREG(before.st_mode):
        raise OSError("not a regular file")
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise OSError("file changed before reading")
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
        after_read = os.fstat(stream.fileno())
    after = plain_stat(path)
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
    if any(getattr(before, key) != getattr(after_read, key) or
           getattr(before, key) != getattr(after, key) for key in fields):
        raise OSError("file changed while reading")
    return digest.hexdigest()


def audit(folder, max_loose=0):
    if max_loose < 0:
        raise ValueError("max_loose must be non-negative")
    result = {"files": [], "duplicates": [], "skipped": [], "errors": [],
              "over": [], "exit_code": 0}
    try:
        root = checked_root(folder)
    except (OSError, ValueError) as exc:
        result["errors"].append("root: " + str(exc))
        result["exit_code"] = 2
        return result

    hashes = {}

    def relative(path):
        return os.path.relpath(path, root)

    def walk_error(exc):
        result["errors"].append(str(exc))

    for directory, dirs, files in os.walk(root, topdown=True, onerror=walk_error,
                                          followlinks=False):
        try:
            plain_stat(directory)
        except OSError as exc:
            result["errors"].append(relative(directory) + ": " + str(exc))
            dirs[:] = []
            continue
        retained = []
        for name in sorted(dirs):
            path = os.path.join(directory, name)
            # Explicitly excluded areas are not inspected, including their links.
            if name.lower() in STORAGE_SKIP or (
                directory == root and name.lower() in ROOT_SKIP
            ):
                result["skipped"].append(relative(path))
                continue
            try:
                plain_stat(path)
            except OSError as exc:
                result["errors"].append(relative(path) + ": " + str(exc))
                continue
            retained.append(name)
        dirs[:] = retained
        scripts = sorted(name for name in files if name.lower().endswith(".py"))
        if len(scripts) > max_loose:
            result["over"].append((relative(directory), len(scripts)))
        for name in scripts:
            path = os.path.join(directory, name)
            rel = relative(path)
            hint = "one-off? / dung mot lan?" if ONCE.search(name) else (
                "job script? / script cua viec?"
            )
            result["files"].append((rel, hint))
            try:
                digest = fingerprint(path)
            except OSError as exc:
                result["errors"].append(rel + ": " + str(exc))
                continue
            hashes.setdefault(digest, []).append(rel)
    result["duplicates"] = [
        sorted(paths) for _, paths in sorted(hashes.items()) if len(paths) > 1
    ]
    result["exit_code"] = 2 if result["errors"] else (1 if result["over"] else 0)
    return result


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", default=".")
    parser.add_argument("--max-loose", type=nonnegative, default=0,
                        help="allowed loose files per directory (default 0; legacy 3)")
    args = parser.parse_args(argv)
    result = audit(args.folder, args.max_loose)
    print("Storage audit only / Chi kiem vi tri luu; no script execution.")
    print("Root exclusions: " + ", ".join(sorted(ROOT_SKIP)))
    print("Exclusions at any depth: " + ", ".join(sorted(STORAGE_SKIP)))
    for path in result["skipped"]:
        print("SKIPPED: " + path)
    for path, hint in result["files"]:
        print("LOOSE: {} [{}; suggestion only]".format(path, hint))
    for paths in result["duplicates"]:
        print("IDENTICAL BYTES (SHA-256; not reuse approval): " + " | ".join(paths))
    for directory, count in result["over"]:
        print("OVER THRESHOLD: {}: {} > {}".format(directory, count, args.max_loose))
    for error in result["errors"]:
        print("NOT INSPECTED / CHUA KIEM: " + error)
    if result["exit_code"] == 2:
        print("INCOMPLETE / CHUA KIEM DU; no clean result.")
    elif result["exit_code"] == 1:
        print("REVIEW NEEDED / CAN XEM XET within scanned scope.")
    else:
        print("WITHIN THRESHOLD in scanned scope only; not a safety/content verdict.")
    print("Limits: exclusions, filename hints, exact bytes only; concurrent path changes "
          "are not fully guarded. No automatic move/delete/promotion.")
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
