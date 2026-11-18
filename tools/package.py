#!/usr/bin/env python3
"""Validate native themes and write reproducible archives and their index."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package(source, output):
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for directory in sorted((ROOT / "themes").iterdir()):
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError("themes/ must contain regular theme directories only")
        result = subprocess.run(
            ["go", "-C", str(source.resolve()), "run", "./src/cmd/themecheck", "-json", str(directory)],
            check=True, capture_output=True, text=True,
        )
        metadata, = json.loads(result.stdout)
        if metadata["id"] != directory.name:
            raise ValueError("theme ID must match its directory")
        # Version and ID come from the validator. Keep archive names within output.
        version = metadata["version"]
        if not version or any(c not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-" for c in version):
            raise ValueError("version must be usable in an archive filename")
        filename = metadata["id"] + "-" + version + ".zip"
        target = output / filename
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(directory).as_posix(), (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, path.read_bytes(), compresslevel=9)
        raw = target.read_bytes()
        entries.append({**metadata, "file": filename, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    if not entries:
        raise ValueError("no themes found")
    (output / "index.json").write_text(json.dumps({"format": 1, "themes": entries}, indent=2) + "\n")
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stargate", type=Path, required=True, help="Stargate source with native theme support")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    for entry in package(args.stargate, args.output):
        print(entry["file"] + " " + entry["sha256"])


if __name__ == "__main__":
    main()
