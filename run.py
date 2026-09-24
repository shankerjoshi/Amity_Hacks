"""One-command, dependency-free local launcher. Python 3.10+."""
import os
import secrets
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    for port in (8000, 8001, 8002):
        try:
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', port))
        except OSError:
            raise SystemExit(f'Port {port} is already in use. Stop the existing demo or the application using that port first.')
    env = os.environ.copy()
    env.setdefault('SENTINEL_INTERNAL_KEY', secrets.token_urlsafe(36))
    children = []
    try:
        for module, port in [('sandbox', 8001), ('control', 8000), ('attacker', 8002)]:
            child_env = {**env, 'PORT': str(port), 'PYTHONUNBUFFERED': '1'}
            if module == 'attacker':
                child_env['SENTINEL_INTERNAL_KEY'] = secrets.token_urlsafe(36)
            children.append(subprocess.Popen([sys.executable, '-m', 'sentinel.'+module], cwd=ROOT, env=child_env))
            for _ in range(50):
                if children[-1].poll() is not None:
                    raise RuntimeError(module+' failed to start; check whether its port is already in use')
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=.3) as response:
                        if response.status == 200: break
                except Exception:
                    time.sleep(.1)
            else:
                raise RuntimeError(module+' failed its startup health check')
        print('\nSentinelAPI: http://127.0.0.1:8000\nAttacker lab: http://127.0.0.1:8002\nPress Ctrl+C to stop all services.\n', flush=True)
        while all(p.poll() is None for p in children):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for child in children:
            child.terminate()
        for child in children:
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: child.kill()

if __name__ == '__main__':
    main()
