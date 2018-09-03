#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2018 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""
Simple package script generator.
"""

import argparse
import re
import shutil
import string
import subprocess
from pathlib import Path

from buildkit.common import (ENCODING, BuildkitAbort, get_logger, validate_and_get_ini,
                             get_chromium_version, get_release_revision)
from buildkit.third_party import schema

# Constants

_ROOT_DIR = Path(__file__).resolve().parent
_PACKAGING_ROOT = _ROOT_DIR / 'packaging'
_PKGMETA = _PACKAGING_ROOT / 'pkgmeta.ini'
_TEMPLATE_SUFFIX = '.ungoogin'
_PKGMETA_SCHEMA = schema.Schema({
    schema.Optional(schema.And(str, len)): {
        schema.Optional('depends'): schema.And(str, len),
        schema.Optional('buildkit_copy'): schema.And(str, len),
    }
})

# Classes


class _BuildFileStringTemplate(string.Template):
    """
    Custom string substitution class

    Inspired by
    http://stackoverflow.com/questions/12768107/string-substitutions-using-templates-in-python
    """

    pattern = r"""
    {delim}(?:
      (?P<escaped>{delim}) |
      _(?P<named>{id})      |
      {{(?P<braced>{id})}}   |
      (?P<invalid>{delim}((?!_)|(?!{{)))
    )
    """.format(
        delim=re.escape("$ungoog"), id=string.Template.idpattern)


# Methods


def _process_templates(template_files, build_file_subs):
    """
    Recursively substitute '$ungoog' strings in template_files and
        remove the suffix

    template_files is an iterable of pathlib.Path
    """
    for old_path in template_files:
        new_path = old_path.with_name(old_path.stem)
        old_path.replace(new_path)
        with new_path.open('r+', encoding=ENCODING) as new_file:
            content = _BuildFileStringTemplate(new_file.read()).substitute(**build_file_subs)
            new_file.seek(0)
            new_file.write(content)
            new_file.truncate()


def _get_current_commit():
    """
    Returns a string of the current commit hash.

    It assumes "git" is in PATH, and that buildkit is run within a git repository.

    Raises BuildkitAbort if invoking git fails.
    """
    result = subprocess.run(
        ['git', 'rev-parse', '--verify', 'HEAD'],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        cwd=str(Path(__file__).resolve().parent))
    if result.returncode:
        get_logger().error('Unexpected return code %s', result.returncode)
        get_logger().error('Command output: %s', result.stdout)
        raise BuildkitAbort()
    return result.stdout.strip('\n')


def _get_package_dir_list(package, pkgmeta):
    """
    Returns a list of pathlib.Path to packaging directories to be copied,
        ordered by dependencies first.

    Raises FileNotFoundError if a package directory cannot be found.
    """
    package_list = list()
    current_name = package
    while current_name:
        package_list.append(_PACKAGING_ROOT / current_name)
        if not package_list[-1].exists(): #pylint: disable=no-member
            raise FileNotFoundError(package_list[-1])
        if current_name in pkgmeta and 'depends' in pkgmeta[current_name]:
            current_name = pkgmeta[current_name]['depends']
        else:
            break
    package_list.reverse()
    return package_list


def _get_package_files(package_dir_list):
    """Yields tuples of relative and full package file paths"""
    resolved_files = dict()
    for package_dir in package_dir_list:
        for file_path in package_dir.rglob('*'):
            relative_path = file_path.relative_to(package_dir)
            resolved_files[relative_path] = file_path
    yield from sorted(resolved_files.items())


def _get_buildkit_copy(package, pkgmeta):
    """
    Returns a pathlib.Path relative to the output directory to copy buildkit and bundles to,
        otherwise returns None if buildkit does not need to be copied.
    """
    while package:
        if package in pkgmeta:
            if 'buildkit_copy' in pkgmeta[package]:
                return Path(pkgmeta[package]['buildkit_copy'])
            if 'depends' in pkgmeta[package]:
                package = pkgmeta[package]['depends']
            else:
                break
        else:
            break
    return None


def _validate_and_get_args(parser):
    """
    Helper for main()

    Validates and returns arguments
    """
    args = parser.parse_args()
    if not args.destination.parent.exists():
        parser.error('Destination parent directory "{}" does not exist'.format(
            args.destination.parent))
    if not _PACKAGING_ROOT.exists(): #pylint: disable=no-member
        parser.error('Cannot find "packaging" directory next to this script')
    packaging_dir = _PACKAGING_ROOT / args.name
    if not packaging_dir.exists():
        parser.error('Packaging "{}" does not exist'.format(args.name))
    if not _PKGMETA.exists(): #pylint: disable=no-member
        parser.error('Cannot find pkgmeta.ini in packaging directory')
    return args


def _copy_buildkit_files(args, pkgmeta, files, dirs):
    """Helper for main()"""
    buildkit_copy_relative = _get_buildkit_copy(args.name, pkgmeta)
    if buildkit_copy_relative is None:
        return
    for file_name in files:
        if not (args.destination / buildkit_copy_relative).exists():
            (args.destination / buildkit_copy_relative).mkdir()
        shutil.copy(
            str(_ROOT_DIR / file_name), str(args.destination / buildkit_copy_relative / file_name))
    for dir_name in dirs:
        if (args.destination / buildkit_copy_relative / dir_name).exists():
            shutil.rmtree(str(args.destination / buildkit_copy_relative / dir_name))
        shutil.copytree(
            str(_ROOT_DIR / dir_name), str(args.destination / buildkit_copy_relative / dir_name))


def main():
    """CLI Entrypoint"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', help='Name of packaging to generate')
    parser.add_argument('destination', type=Path, help='Directory to store packaging files')
    args = _validate_and_get_args(parser)

    if not args.destination.exists():
        args.destination.mkdir()

    # Copy packaging files to destination
    pkgmeta = validate_and_get_ini(_PKGMETA, _PKGMETA_SCHEMA)
    template_files = set()
    for relative_path, actual_path in _get_package_files(_get_package_dir_list(args.name, pkgmeta)):
        target_path = args.destination / relative_path
        if actual_path.is_dir():
            if not target_path.exists():
                target_path.mkdir()
            shutil.copymode(str(actual_path), str(target_path))
        else:
            shutil.copy(str(actual_path), str(target_path))
            if target_path.suffix.lower() == _TEMPLATE_SUFFIX:
                template_files.add(target_path)

    # Substitute template files
    packaging_subs = dict(
        chromium_version=get_chromium_version(),
        release_revision=get_release_revision(),
        current_commit=_get_current_commit(),
    )
    _process_templates(template_files, packaging_subs)

    # Copy buildkit and config files, if necessary
    _copy_buildkit_files(
        args,
        pkgmeta,
        files=('version.ini', 'run_buildkit_cli.py'),
        dirs=('buildkit', 'config_bundles', 'patches'))


if __name__ == '__main__':
    main()
