import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'create_repositories.py'


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('bootstrap', SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def manifest(self, directory, entries=None):
        path = Path(directory) / 'repositories.json'
        path.write_text(json.dumps({'owner': 'lambdawalker', 'repositories': entries or [
            {'name': 'names.api.wikidata', 'description': 'Wikidata client', 'optional': False},
            {'name': 'names.api.demographics', 'description': 'Optional client', 'optional': True},
        ]}), encoding='utf-8')
        return path

    def run_script(self, path, *args):
        return subprocess.run(['python', str(SCRIPT), '--manifest', str(path), *args],
                              text=True, capture_output=True)

    def test_dry_run_needs_no_gh_and_excludes_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_script(self.manifest(directory), '--gh', '/missing/gh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('lambdawalker/names.api.wikidata', result.stdout)
        self.assertNotIn('names.api.demographics', result.stdout)
        self.assertIn('--public', result.stdout)

    def test_optional_and_only_select_exact_repositories(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_script(self.manifest(directory), '--include-optional',
                                     '--only', 'names.api.demographics')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('names.api.demographics', result.stdout)
        self.assertNotIn('names.api.wikidata', result.stdout)

    def test_unknown_selection_fails_before_gh(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_script(self.manifest(directory), '--only', 'typo')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unknown', result.stderr)

    def test_invalid_and_duplicate_names_fail(self):
        for names in [('bad/name',), ('valid', 'VALID')]:
            with self.subTest(names=names), tempfile.TemporaryDirectory() as directory:
                path = self.manifest(directory, [
                    {'name': name, 'description': 'test', 'optional': False} for name in names])
                self.assertNotEqual(self.run_script(path).returncode, 0)

    def fake_runner(self, probe_code=404, login='lambdawalker', create_code=0):
        calls = []

        def run(argv, **kwargs):
            calls.append(argv)
            if argv[1:3] == ['auth', 'status']:
                return subprocess.CompletedProcess(argv, 0, '', '')
            if argv[1:3] == ['api', 'user']:
                return subprocess.CompletedProcess(argv, 0, login + '\n', '')
            if argv[1:3] == ['api', '--include']:
                return subprocess.CompletedProcess(argv, 0 if probe_code == 200 else 1,
                    f'HTTP/2.0 {probe_code} Result\n\n{{}}', '')
            if argv[1:3] == ['repo', 'create']:
                return subprocess.CompletedProcess(argv, create_code, '', 'creation failed')
            raise AssertionError(argv)

        return run, calls

    def apply(self, runner):
        return self.module.apply_repositories('gh', 'lambdawalker', [
            {'name': 'names.api.wikidata', 'description': 'Wikidata client', 'optional': False}], runner)

    def test_existing_repository_is_not_modified(self):
        runner, calls = self.fake_runner(probe_code=200)
        self.apply(runner)
        self.assertFalse(any(c[1:3] == ['repo', 'create'] for c in calls))

    def test_missing_repository_is_created_public_with_mit(self):
        runner, calls = self.fake_runner()
        self.apply(runner)
        create = next(c for c in calls if c[1:3] == ['repo', 'create'])
        self.assertIn('--public', create)
        self.assertEqual(create[create.index('--license') + 1], 'mit')

    def test_access_and_network_errors_never_trigger_creation(self):
        for code in (401, 403, 429, 500, 0):
            with self.subTest(code=code):
                runner, calls = self.fake_runner(probe_code=code)
                with self.assertRaises(RuntimeError):
                    self.apply(runner)
                self.assertFalse(any(c[1:3] == ['repo', 'create'] for c in calls))

    def test_wrong_account_fails_before_creating(self):
        runner, calls = self.fake_runner(login='someone-else')
        with self.assertRaises(RuntimeError):
            self.apply(runner)
        self.assertFalse(any(c[1:3] == ['repo', 'create'] for c in calls))

    def test_failed_creation_is_not_reported_as_success(self):
        runner, _ = self.fake_runner(create_code=1)
        with self.assertRaises(RuntimeError):
            self.apply(runner)


if __name__ == '__main__':
    unittest.main()
