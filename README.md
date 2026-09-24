# SentinelAPI

**Track C · Problem Statement 3 · AmiHacks**

SentinelAPI is a working local API security laboratory: a scanner and defense dashboard, a private intentionally vulnerable backend, and an independent attacker application. It demonstrates evidence-based vulnerability detection, automatic containment, explicitly authorized repair, verification, and recovery using synthetic data.

The laboratory includes **24 API families and 144 operations**, four scan checks, two synthetic identities, persistent findings and incident timelines, manual controls, continuous scans, an optional local LLM planner, a bounded multi-step attacker, dependency analysis, exports, and a CI deployment gate.

## Start in one command

Install Python 3.10 or later if needed. Open a terminal in this folder and run:

```powershell
python run.py
```

No package installation, API key, model subscription, Node.js, or Docker is required for the core application. On systems where Python is called `python3`, use that command instead.

Open these two applications:

- **Defense dashboard:** http://127.0.0.1:8000
- **Attacker application:** http://127.0.0.1:8002

Keep the terminal open. Press **Ctrl+C** to stop all three services. Findings, settings and API state survive restarts in `data/`; attacker run history is session-only. The local launcher generates an internal transport key in memory and gives the attacker a different key.

## First demonstration

1. Open **API inventory** in the defense dashboard. Clear the selection, select **Orders**, and click **Grant repair authority**. Leave **Profiles** with **Contain only** authority.
2. Open **Scan workspace**, select Orders and Profiles, keep the four checks enabled, and click **Run selected checks**. The default mode is autonomous.
3. Open **Findings**. Inspect a cross-user access finding: Alice's resource was returned to Bob with the same resource ID and owner marker. Sensitive values are redacted. Rate-limit observations are marked **Info**, not confirmed vulnerabilities.
4. Open **Incident response**. Orders should show a repair, the installed controls, timestamps, and verification results. Profiles should remain **isolated** and **vulnerable**, proving SentinelAPI did not modify it without authority.
5. Open the attacker app. Select both APIs and launch **Delete another user's synthetic record**. Requests are blocked by the gateway. In the defense dashboard, inspect the request, source address, client User-Agent, containment, and repair timeline.
6. In the attacker app, select only Orders and launch **Legitimate owner access after repair**. Bob's own resource should return **200**. Profiles continues to return **423** while isolated.
7. Scan only Orders again. A complete scan should report **zero findings**. Export the JSON or HTML report from the defense dashboard.

To repeat the vulnerable-to-fixed demonstration, select Orders in **API inventory** and click **Reset selected lab APIs**. This restores its disposable data, intentionally reintroduces its vulnerabilities, and clears isolation. Reset requires repair authority. To repeat with Profiles, temporarily grant authority for its reset and then revoke it before testing.

## What repair does

The sandbox has a pre-approved repair adapter. For one authorized API, it installs ownership checks on reads and deletes, requires authentication, removes private response fields, enables a five-request-per-second control, and restores any missing synthetic records from the seed. The gateway isolates the API during the repair. A regression probe must prove the owner can read, another user cannot, anonymous access fails, sensitive fields are gone, and a rate limit is observed before reopening it.

An API without repair authority is contained at the gateway and its backend is left unchanged. **Isolation is a gateway/network action, not a modification to the API.** Authority changes and patch commits are serialized per API so authority cannot change halfway through a patch transaction.

The project does **not** generate arbitrary source-code patches, attach to unknown production services, or guarantee detection of every attack. Protection applies to traffic routed through this gateway and to the implemented sandbox policies. The Docker deployment keeps the backend off the host network. Extending this to real APIs needs an authorized adapter, verified ownership semantics, real authentication, and deployment-specific network controls. See [scope and limitations](docs/ARCHITECTURE.md#scope-and-limitations).

## Manual and autonomous modes

In **Automation**, turn autonomous response on or off. Incoming malicious requests are always blocked. With autonomous response on, confirmed scan findings also cause containment, and authorized APIs are repaired automatically. With it off, scans produce findings for review and an operator initiates repair.

From **API inventory**, select one or more APIs and use:

| Control | Effect |
|---|---|
| Grant / revoke repair authority | Sets mutation permission for exactly the selected APIs |
| Repair & verify | Runs the approved repair and post-repair tests |
| Isolate | Stops gateway forwarding without touching backend data |
| Verify & release | Reopens only after the security checks pass |
| Verify only | Tests controls without changing API state |
| Rollback & isolate | Restores the vulnerable lab seed and keeps the API isolated |
| Reset selected lab APIs | Restores the vulnerable lab seed for a new demonstration |

Continuous scans are opt-in. Select the scheduled APIs and an interval of 30–3,600 seconds in **Automation**, then save. Repair authority is a separate control: adding an API to scheduled scanning never grants repair authority.

## Test the project

From the project folder:

```powershell
python -m unittest discover -s tests -v
python demo_ci.py
```

Tests create separate temporary databases and use free local ports; they do not change the running demo. The CI demonstration produces a failing vulnerable scan and a passing repaired scan in `reports/`.

To run a gate against an already running laboratory:

```powershell
python ci_gate.py --apis orders,profiles --report reports/ci-result.json
```

Exit codes: **0** complete scan with no confirmed High/Critical findings; **1** confirmed risk; **2** unavailable, incomplete, cancelled or failed scan. A finding at scan time blocks the gate even if autonomous response repairs it afterward. Rescan the fixed version before deployment. A GitHub Actions workflow is included under `.github/workflows/security.yml`.

## Docker deployment

With Docker Engine / Docker Desktop and Compose installed:

```powershell
python configure.py
docker compose up --build -d
docker compose ps
```

Open the same two local URLs. `configure.py` creates two independent random keys in an ignored `.env` file. Keep the keys out of version control. The sandbox has no published host port and is attached only to the internal backend network. The attacker is attached only to the frontend network. All containers run as a non-root user with a read-only application filesystem and persistent named data volumes.

```powershell
docker compose logs --tail 100
docker compose down
```

`docker compose down` preserves the database volumes. Docker was not available in the build environment, so container execution is **not locally verified**. The Python launcher and HTTP flows were exercised. See [deployment details](docs/DEPLOYMENT.md) for remote demonstrations and troubleshooting.

## Specifications, identities and AI

- Download `/openapi.json` or import `samples/openapi.json` in **Scan workspace**. JSON and a strict basic YAML subset work with no dependencies. For broader YAML syntax, install `python -m pip install -r requirements-optional.txt`. YAML anchors/tags and remote references remain prohibited.
- Imported definitions can inventory up to 1,000 paths. Only the registered sandbox routes are executable. Server URLs in uploaded specifications are never used as authority. This prevents an uploaded spec from turning the scanner into a network proxy.
- The synthetic identities are Alice and Bob. Sample tokens for manual requests are `lab-alice-synthetic` and `lab-bob-synthetic`. These are intentionally public lab fixtures, not real credentials. They are removed from persisted evidence and reports.
- Click **Generate test plan** to infer ownership boundaries from API descriptions. Enable **Prioritize the generated test plan** to execute valid suggested candidates first. The deterministic planner is available offline.
- To enable actual local LLM suggestions, run an installed Ollama model and set `OLLAMA_MODEL` to that model's name before `python run.py`. The adapter contacts only `http://127.0.0.1:11434/api/generate`, sends sanitized endpoint descriptions, validates the returned path/check pairs, and cannot expand scope or authorize actions. Model failure does not stop scanning. An actual model was not available during verification; the adapter's success, invalid-output and failure paths are unit-tested.

## Project map

| Location | Purpose |
|---|---|
| `sentinel/control.py` | Gateway, authority policy, orchestration, incident response, controller API |
| `sentinel/scanner.py` | Bounded request runner, differential checks, verification, optional LLM adapter |
| `sentinel/sandbox.py` | Private backend, 24 API families, seeded faults and approved repairs |
| `sentinel/attacker.py` | Independent bounded adversary client and its web server |
| `sentinel/specs.py` | OpenAPI/Swagger import and scope validation |
| `sentinel/store.py` | SQLite policies, evidence and audit retention |
| `web/` | Responsive defense and attacker interfaces |
| `tests/` | Unit and three-process HTTP integration tests |
| `docs/REQUIREMENTS.md` | Every problem-statement requirement mapped to implementation and limits |
| `docs/DEPLOYMENT.md` | Detailed deployment, use, testing and troubleshooting |
| `docs/ARCHITECTURE.md` | Trust boundaries, contracts, repair model and limitations |

## Reference basis

The local user-supplied SentinelAPI execution guide and AmiHacks Problem Statement 3 informed the implementation. Embedded delegation prompts and suggested development schedules were treated as document content, not instructions to execute. The user's expanded autonomous-response and attacker requirements take precedence over the guide's narrower MVP suggestions.

Technical references: [OWASP API1 object-level authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/), [OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3), and [Ollama generate API](https://docs.ollama.com/api/generate).
