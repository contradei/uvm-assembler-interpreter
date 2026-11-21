"""Audit every stage from isolated git archives without changing checkout."""

import ast
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from radon.complexity import cc_visit


def run(arguments, directory):
    """Run a checked subprocess and show its output if it fails."""
    result = subprocess.run(arguments, cwd=directory, capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout + result.stderr


def check_nodes(tree, path):
    """Enforce function size, docstrings, argument count and comparisons."""
    function_limit = 40
    argument_limit = 7
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            size = node.end_lineno - node.lineno + 1
            assert size <= function_limit, (path, node.name)
            assert len(node.args.args) <= argument_limit, (path, node.name)
            assert ast.get_docstring(node), (path, node.name)
        if isinstance(node, ast.Compare):
            for value in [node.left] + node.comparators:
                if isinstance(value, ast.Constant):
                    assert type(value.value) not in (int, float), path


def check_complexity(source, path):
    """Inspect methods and nested functions as well as top-level functions."""
    blocks = list(cc_visit(source))
    limit = 10
    maximum = 0
    while blocks:
        block = blocks.pop()
        assert block.complexity <= limit, (path, block.name)
        maximum = max(maximum, block.complexity)
        blocks.extend(getattr(block, 'methods', []))
        blocks.extend(getattr(block, 'closures', []))
    return maximum


def check_files(directory):
    """Require the project structure and validate tracked text sources."""
    for name in ('README.md', '.gitignore', 'src', 'tests', 'run.bat'):
        assert (directory / name).exists(), name
    maximum = 0
    file_limit = 1000
    for path in directory.rglob('*'):
        if not path.is_file():
            continue
        source = path.read_text(encoding='utf-8')
        lines = source.splitlines()
        assert len(lines) <= file_limit, path
        line_limit = 80 if path.suffix == '.py' else 120
        assert all(len(line) <= line_limit for line in lines), path
        if path.suffix == '.py':
            check_nodes(ast.parse(source), path)
            maximum = max(maximum, check_complexity(source, path))
    return maximum


def check_commit(repository, commit):
    """Extract one snapshot, inspect it, run its own tests and lint it."""
    archive = subprocess.check_output(
        ['git', 'archive', '--format=zip', commit], cwd=repository)
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        with zipfile.ZipFile(io.BytesIO(archive)) as stream:
            stream.extractall(directory)
        maximum = check_files(directory)
        output = run([sys.executable, '-m', 'unittest', 'discover',
                      '-s', 'tests', '-v'], directory)
        folders = [name for name in ('src', 'tests', 'scripts')
                   if (directory / name).is_dir()]
        run([sys.executable, '-m', 'flake8', *folders, '--select', 'E,F,N',
             '--ignore', 'E402,W503', '--max-line-length', '80'], directory)
        summary = [line for line in output.splitlines()
                   if line.startswith(('Ran ', 'OK'))]
        print(commit[:7], f'complexity={maximum}', '; '.join(summary),
              flush=True)


def main():
    """Audit the ancestry of HEAD, preserving the user's working tree."""
    repository = Path(__file__).resolve().parents[1]
    commits = run(['git', 'rev-list', '--reverse', 'HEAD'], repository)
    for commit in commits.splitlines():
        check_commit(repository, commit)


if __name__ == '__main__':
    main()
