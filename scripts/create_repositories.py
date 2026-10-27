#!/usr/bin/env python3
"""Preview or create the companion repositories using the user's GitHub CLI login."""

import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys


def load_manifest(path, include_optional=False, only=None):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    owner = data.get('owner', '')
    if not isinstance(owner, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', owner):
        raise ValueError('Invalid GitHub owner in manifest')
    entries = data.get('repositories')
    if not isinstance(entries, list) or not entries:
        raise ValueError('Manifest requires a non-empty repositories array')
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('Repository entries must be objects')
        name = entry.get('name', '')
        if (not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}', name)
                or name.lower() in seen):
            raise ValueError('Invalid or duplicate repository name: ' + str(name))
        if not isinstance(entry.get('description'), str) or not entry['description'].strip():
            raise ValueError('Missing description for ' + name)
        if not isinstance(entry.get('optional', False), bool):
            raise ValueError('optional must be a boolean for ' + name)
        seen.add(name.lower())
    requested = set(only or [])
    unknown = requested - {e['name'] for e in entries}
    if unknown:
        raise ValueError('Unknown repository selection: ' + ', '.join(sorted(unknown)))
    selected = [e for e in entries if (include_optional or not e.get('optional', False))
                and (not requested or e['name'] in requested)]
    if requested - {e['name'] for e in selected}:
        raise ValueError('Optional repositories require --include-optional')
    if not selected:
        raise ValueError('No repositories selected')
    return owner, selected


def create_command(gh, owner, entry):
    return [gh, 'repo', 'create', f"{owner}/{entry['name']}", '--public',
            '--description', entry['description'], '--add-readme', '--license', 'mit']


def apply_repositories(gh, owner, entries, runner=subprocess.run):
    def run(args):
        return runner(args, text=True, capture_output=True, timeout=120)

    auth = run([gh, 'auth', 'status', '--hostname', 'github.com'])
    if auth.returncode:
        raise RuntimeError('GitHub CLI is not authenticated. Run: gh auth login --hostname github.com')
    user = run([gh, 'api', 'user', '--hostname', 'github.com', '--jq', '.login'])
    if user.returncode or user.stdout.strip().lower() != owner.lower():
        raise RuntimeError(f'Authenticate as {owner} first; this script creates personal-account repositories only.')
    for entry in entries:
        full_name = f"{owner}/{entry['name']}"
        probe = run([gh, 'api', '--include', '--hostname', 'github.com', f'repos/{full_name}'])
        statuses = re.findall(r'^HTTP/\S+\s+(\d{3})\b', probe.stdout, re.MULTILINE)
        status = int(statuses[-1]) if statuses else None
        if probe.returncode == 0 and status == 200:
            print(f'SKIP existing: https://github.com/{full_name}')
            continue
        if status != 404:
            raise RuntimeError(f'Cannot check {full_name} (HTTP {status or "unknown"}); stopped without creating it.')
        created = run(create_command(gh, owner, entry))
        if created.returncode:
            raise RuntimeError(f'Creation failed for {full_name}; earlier successes remain. '
                               'Inspect GitHub and rerun; existing repositories will be skipped.')
        print(f'CREATED: https://github.com/{full_name}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'repositories.json')
    parser.add_argument('--apply', action='store_true', help='Actually create missing repositories')
    parser.add_argument('--include-optional', action='store_true', help='Include demographic enrichment client')
    parser.add_argument('--only', nargs='+', metavar='REPO', help='Select exact repository names from the manifest')
    parser.add_argument('--gh', default='gh', help='GitHub CLI executable path')
    args = parser.parse_args(argv)
    try:
        owner, entries = load_manifest(args.manifest, args.include_optional, args.only)
        if not args.apply:
            print('DRY RUN: no GitHub calls or changes. Displayed commands use POSIX quoting; '
                  'the script itself also runs on Windows.')
            for entry in entries:
                print(shlex.join(create_command(args.gh, owner, entry)))
            print('\nRerun with --apply to create missing public repositories with README and MIT license.')
            return 0
        apply_repositories(args.gh, owner, entries)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
