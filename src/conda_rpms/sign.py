from pathlib import Path
import subprocess
from typing import Any, List

from .logger import log


def find_rpm_deps(rpm: Path) -> List[str]:
    """For a given rpm, return all its named dependencies."""
    namespace = rpm.name.split("-")[0]
    proc = subprocess.run(["rpm", "-qpR", rpm], capture_output=True)
    lines = proc.stdout.decode().splitlines()
    deps = [line for line in lines if line.startswith(namespace)]
    return deps

def _sign_rpm(rpm: Path, *args: str) -> None:
    log.info(f"Signing {rpm.name}.")
    proc = subprocess.run(["rpmsign", "--addsign", *args, rpm], capture_output=True)
    log.debug(proc.stdout.decode())
    log.debug(proc.stderr.decode())
    proc.check_returncode()

def sign_rpm(rpm: Path, *args: str, include_dependencies=True) -> None:
    """Sign an rpm.

    If `include_dependencies` is True (the default), also inspect the
    rpm for its dependencies and sign those rpms too, assumed to be
    found next to the parent rpm file.

    By default, no args are passed to `rpmsign`, instead it is assumed
    that a `~/.rpmmacros` file is available containing configuration.
    Alternatively, any command line arguments can be given as additional
    arguments to this function.

    Returns None, raises error on non-zero exit code from `rpmsign`.
    """
    rpms = [rpm]
    if include_dependencies:
        rpm_dir = rpm.parent
        deps = find_rpm_deps(rpm)

        for d in deps:
            # look in the same directory as `rpm` and find
            # all the `.rpm` files that match the dependency name
            matches = list(sorted(rpm_dir.glob(f'{d}*.rpm')))
            rpms.extend(matches)

    for rpm in rpms:
        _sign_rpm(rpm, *args)

if __name__ == "__main__":
    import argparse
    from textwrap import dedent
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "rpm", help="The rpm file to sign."
    )
    parser.add_argument(
        "--no-deps", action='store_true',
        help=dedent(
            r"""Set this to only sign the passed argument and ignore dependencies.

            By default, rpms are inspected for their dependecies
            and these are signed too (assumed to be found next to the
            passed rpm)."""
            )
    )

    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        log.setLevel("DEBUG")

    rpm = Path(args.rpm).resolve()
    sign_rpm(rpm, include_dependencies=(not args.no_deps))