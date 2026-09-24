"""CI demonstration: isolated fresh services, risky gate fails, repaired gate passes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request

def main():
    # Reuse the tested process fixture with unique free ports and temporary databases.
    from tests.test_system import IntegrationTests, call
    IntegrationTests.setUpClass()
    fixture=IntegrationTests
    headers={'X-Session':fixture.session}
    try:
        call(fixture.control,'/control/settings',{'autonomous':False},headers)
        command=[sys.executable,'ci_gate.py','--control-url',fixture.control,'--apis','orders']
        blocked=subprocess.run(command+['--report','reports/vulnerable.json']).returncode
        if blocked!=1:raise RuntimeError('Vulnerable API did not block the pipeline')
        call(fixture.control,'/control/policy',{'api_ids':['orders'],'repair':True},headers)
        code,data=call(fixture.control,'/control/action',{'api_ids':['orders'],'action':'repair'},headers)
        if code!=200 or data['results'][0]['status']!='repaired':raise RuntimeError('Repair failed')
        passed=subprocess.run(command+['--report','reports/repaired.json']).returncode
        if passed!=0:raise RuntimeError('Repaired API did not pass the pipeline')
        print('CI proof complete: vulnerable blocked; repaired passed.')
    finally:
        IntegrationTests.tearDownClass()

if __name__=='__main__':main()
