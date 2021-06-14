"""
Build all spec files which exists and which don't already have
equivalent built RPMs in the build directory.

"""
import os
import glob
import subprocess
import typing
from pathlib import Path

from .logger import log

def name_version_release(spec_fh: typing.Iterable[str]) -> typing.Dict[str, str]:
    """
    Take the name, version and release number from the given filehandle pointing at a spec file.
    """
    content = {}
    for line in spec_fh:
        if line.startswith('Name:') and 'name' not in content:
            content['name'] = line[5:].strip()
        elif line.startswith('Version:') and 'version' not in content:
            content['version'] = line[8:].strip()
        elif line.startswith('Release:') and 'release' not in content:
            content['release'] = line[8:].strip()
    return content


def build_new(rpmbuild_dir: str, rpm_directory: str) -> None:
    """We rely on spec naming conventions to check that the build RPMs actually exist."""
    build_dir = Path(rpmbuild_dir).resolve()
    specs_directory = build_dir / "SPECS"
    for spec in sorted(glob.glob(os.path.join(specs_directory, '*.spec'))):
        rpm_name = spec[:-5]
        with open(spec, 'r') as fh:
            spec_info = name_version_release(fh)
        rpm_name = '{name}-{version}-{release}.x86_64.rpm'.format(**spec_info)

        rpm = Path(rpm_directory) / "x86_64" / rpm_name
        if not rpm.exists():
            log.info(f"Building {spec} to {rpm}")
            subprocess.check_call([
                'rpmbuild', '-bb',
                '--define', "_topdir {}".format(build_dir),
                spec, '--force'
            ])
        else:
            log.info(f"RPM {rpm} already exists, skipping.")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('rpmbuild_dir', help='The location of the rpmbuild directory.')
    parser.add_argument('rpm_dir', help='The location to look for existing RPMs.')

    args = parser.parse_args()

    build_new(args.rpmbuild_dir, args.rpm_dir)

