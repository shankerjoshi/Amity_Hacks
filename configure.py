from pathlib import Path
import secrets

target = Path(__file__).resolve().parent / '.env'
if target.exists():
    print('.env already exists; keeping the existing keys.')
else:
    target.write_text('SENTINEL_INTERNAL_KEY='+secrets.token_urlsafe(48)+'\nATTACKER_STARTUP_KEY='+secrets.token_urlsafe(48)+'\n')
    try: target.chmod(0o600)
    except OSError: pass
    print('Created separate controller and attacker startup keys in .env. Do not commit this file.')
