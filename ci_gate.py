"""Scan the running local sandbox and fail the pipeline on confirmed risk or incomplete results."""
import argparse
import json
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control-url', default='http://127.0.0.1:8000')
    parser.add_argument('--apis',default='orders',help='Comma-separated registered API IDs')
    parser.add_argument('--report',default='reports/ci-result.json')
    args=parser.parse_args()
    parsed=urllib.parse.urlsplit(args.control_url)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
        parser.error('The CI gate accepts only a loopback SentinelAPI controller URL')
    base=args.control_url.rstrip('/')
    session=''
    def call(path,body=None):
        request=urllib.request.Request(base+path, data=json.dumps(body).encode() if body is not None else None,
                                      headers={'Content-Type':'application/json','X-Session':session})
        with urllib.request.urlopen(request,timeout=8) as response:
            return json.load(response)
    try:
        session=call('/bootstrap')['session']
        scan=call('/control/scan',{'api_ids':args.apis.split(','),'budget':1000})
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            state=call('/control/state')
            current=next(s for s in state['scans'] if s['id']==scan['id'])
            if current['status'] not in ('queued','running'):break
            time.sleep(.3)
        else:
            raise TimeoutError('Scan did not complete in 180 seconds')
        findings=[f for f in state['findings'] if f.get('scan_id')==scan['id']]
        blocked=[f for f in findings if f['confidence']=='Confirmed' and f['severity'] in ('High','Critical')]
        code=2 if current['status']!='completed' else 1 if blocked else 0
        report={'gate':'PASS' if code==0 else 'BLOCK', 'exit_code':code, 'scan':current, 'findings':findings,
                'note':'Findings at scan time block deployment even if an automatic repair subsequently resolves them.'}
        target=Path(args.report); target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(f'{report["gate"]}: {len(blocked)} confirmed high/critical findings; scan {current["status"]}. Report: {target}')
        return code
    except Exception as exc:
        print('BLOCK: scan unavailable or incomplete: '+str(exc),file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())
