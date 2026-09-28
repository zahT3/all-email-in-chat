"""Reject private work journals in the Git index and built distributions."""

import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath


def private_path(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return any(part in {"00_工作日志.md", "local", ".impeccable", "node_modules"} for part in parts)


def main():
    tracked = subprocess.check_output(["git", "ls-files", "-z"], text=True).split("\0")
    problems = [f"git:{name}" for name in tracked if private_path(name)]
    archives = sorted(Path("dist").glob("*.whl")) + sorted(Path("dist").glob("*.tar.gz"))
    if not any(path.suffix == ".whl" for path in archives) or not any(
        path.name.endswith(".tar.gz") for path in archives
    ):
        raise SystemExit("Build the wheel and sdist before checking publication contents.")
    for archive in archives:
        if archive.suffix == ".whl":
            with zipfile.ZipFile(archive) as package:
                members = package.namelist()
        else:
            with tarfile.open(archive) as package:
                members = package.getnames()
        problems.extend(f"{archive.name}:{name}" for name in members if private_path(name))
    if problems:
        raise SystemExit("Private files found in publication inputs:\n" + "\n".join(problems))
    print(f"Publication contents checked: Git index and {len(archives)} archives are clear.")


if __name__ == "__main__":
    main()
