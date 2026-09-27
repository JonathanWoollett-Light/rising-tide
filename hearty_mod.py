"""Run hearty on the mod: fix and format it, or check it (the pre-commit hook does).

hearty (https://github.com/JonathanWoollett-Light/hearty, `cargo install hearty`) formats the script files under
mod_folder's common/, events/ and history/ - canonical field order, events in id order, short blocks joined onto one
line - removes fields set to their default, and lints for missing localisation. It cannot skip a file, and the seven
files we override must stay OWB's bytes plus the edits CLAUDE.md > Overriding OWB lists; formatted, they would also
fail its lint on OWB's own keys, which live in OWB's folder. So this script runs hearty on a mirror of mod_folder
without them, and copies back what hearty changed.

    python hearty_mod.py            fix and format mod_folder in place, then lint it
    python hearty_mod.py --check    check the formatting and lint the working tree; changes nothing
    python hearty_mod.py --staged   the same on what is staged for commit; nothing to do if no script file is

hearty's version check of descriptor.mod caches HOI4's latest version in .hearty-cache (gitignored) for a day.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOD = 'mod_folder'
# What hearty reads: the script folders, the localisation and descriptor.mod.
PARTS = ('descriptor.mod', 'common', 'events', 'history', 'localisation')
# CLAUDE.md > Overriding OWB: OWB's files with our edits, left exactly as they are.
OVERRIDES = {
    'common/characters/MLT.txt',
    'common/continuous_focus/generic.txt',
    'common/national_focus/Mirelurk Tribe (MLT) Focus.txt',
    'common/script_enums.txt',
    'common/technologies/tech_naval.txt',
    'events/nf_mlt.txt',
    'history/countries/MLT - Mirelurk Tribe.txt',
}


def find_hearty():
    found = shutil.which('hearty')
    if found:
        return found
    cargo = Path.home() / '.cargo' / 'bin' / ('hearty.exe' if os.name == 'nt' else 'hearty')
    return str(cargo) if cargo.exists() else None


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def mod_paths(listing):
    """The paths (relative to mod_folder, with /) of a NUL-separated git listing, the overrides left out."""
    paths = []
    for entry in listing.split(b'\0'):
        if entry:
            path = entry.decode('utf-8')[len(MOD) + 1:]
            if path not in OVERRIDES:
                paths.append(path)
    return paths


def mirror_worktree(dest):
    """Copies mod_folder's PARTS from the working tree into dest, tracked or not, the overrides left out."""
    src = ROOT / MOD
    for part in PARTS:
        if (src / part).is_file():
            shutil.copy2(src / part, dest / part)
            continue
        for folder, _, files in os.walk(src / part):
            for name in files:
                path = Path(folder, name)
                rel = path.relative_to(src).as_posix()
                if rel not in OVERRIDES:
                    (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest / rel)


def mirror_index(dest):
    """Copies mod_folder's PARTS as they are staged into dest, the overrides left out."""
    listing = git('ls-files', '-z', '--', *('%s/%s' % (MOD, part) for part in PARTS))
    paths = ['%s/%s' % (MOD, path) for path in mod_paths(listing)]
    # checkout-index writes each file to <prefix><path>, and every path starts with mod_folder/.
    subprocess.run(['git', 'checkout-index', '-z', '--stdin', '--prefix=%s/' % dest.parent.as_posix()],
                   cwd=ROOT, check=True, input=b'\0'.join(p.encode('utf-8') for p in paths))


def copy_back(mirror):
    """Writes every script file hearty changed in the mirror back into mod_folder; returns how many."""
    changed = 0
    for folder, _, files in os.walk(mirror):
        for name in files:
            path = Path(folder, name)
            target = ROOT / MOD / path.relative_to(mirror)
            data = path.read_bytes()
            if not target.exists() or target.read_bytes() != data:
                target.write_bytes(data)
                changed += 1
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='check and lint the working tree; change nothing')
    mode.add_argument('--staged', action='store_true', help='check and lint what is staged (the pre-commit hook)')
    args = parser.parse_args()

    if args.staged:
        staged = git('diff', '--cached', '--name-only', '-z', '--', *('%s/%s' % (MOD, part) for part in PARTS))
        if not mod_paths(staged):
            return 0

    hearty = find_hearty()
    if hearty is None:
        print('hearty is not installed: cargo install hearty (https://github.com/JonathanWoollett-Light/hearty)',
              file=sys.stderr)
        return 1

    env = dict(os.environ)
    env.setdefault('HEARTY_CACHE_DIR', str(ROOT / '.hearty-cache'))
    with tempfile.TemporaryDirectory(prefix='hearty_mod_') as tmp:
        mirror = Path(tmp) / MOD
        mirror.mkdir()
        if args.staged:
            mirror_index(mirror)
        else:
            mirror_worktree(mirror)
        flags = ['--check', '--lint'] if args.check or args.staged else ['--fix', '--format', '--lint']
        # Run from the mirror's parent, so that hearty names each file mod_folder/..., as in the repo.
        code = subprocess.run([hearty, *flags, MOD], cwd=tmp, env=env).returncode
        if args.check or args.staged:
            if code:
                print('\nRun `python hearty_mod.py` to fix and format mod_folder (OWB\'s overrides are left alone), '
                      'then stage the result.', file=sys.stderr)
        else:
            changed = copy_back(mirror)
            print('Wrote %d file(s) back into %s.' % (changed, MOD))
    return code


if __name__ == '__main__':
    sys.exit(main())
