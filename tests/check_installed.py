"""Check the wheel outside the checkout, without any model call."""
import os
import subprocess
import sys
import tempfile

code = '''
from pathlib import Path
import cli.main
from core.ai.prompts.prompt_engine import load_prompt
assert 'site-packages' in Path(cli.main.__file__).resolve().parts
for name in ['reconcile_pmm','populate_vision','module_pmm','drift_compare','clarify_vision','apply_clarifications']:
    assert load_prompt(name).strip(), name
print('Installed CLI and all six prompt resources are available.')
'''
environment = dict(os.environ, PYTHONNOUSERSITE='1')
environment.pop('PYTHONPATH', None)
with tempfile.TemporaryDirectory() as directory:
    subprocess.run([sys.executable, '-c', code], cwd=directory, env=environment, check=True)
    subprocess.run([sys.executable, '-m', 'cli.main', '--help'], cwd=directory, env=environment, check=True,
                   stdout=subprocess.DEVNULL)
