# Requirement coverage

This checklist maps **Track C / Problem Statement 3 / SentinelAPI** and the user's expanded request to the delivered implementation. The source document contains an inconsistent Track A body heading; this project uses Track C. The execution guide's proposed stack, delegation prompts, schedule and narrow-MVP exclusions are guidance, not extra user instructions.

“Implemented” below means implemented for the supplied synthetic sandbox. It does not mean arbitrary production APIs are supported. The optional actual-model path is explicitly distinguished from deterministic functionality.

## Current situation and pain points

| Source requirement | Implemented response | How to verify |
|---|---|---|
| Manual, infrequent reviews that do not scale with deployment velocity | One-click scans, persistent scan history, continuous scheduler, CI gate; manual operation remains available | Run a manual scan; enable continuous scans; run `demo_ci.py` |
| Generic scanners miss authorization logic | Differential Alice/Bob requests require matching resource ID and explicit owner proof | Open a confirmed BOLA finding; inspect baseline and probe |
| No continuous automated signal | Live gateway telemetry, immediate containment, opt-in continuous scans and autonomous repairs | Launch attacker scenario, inspect incident timeline; enable schedule |
| Enterprise tools are unaffordable | Local core has no paid service or external dependency requirement | Start with Python only and no model key |
| Findings lack reproduction and severity context | Severity, confidence, redacted request pairs, response comparison, exact field paths and remediation | Open finding details and export report |

## Objective

The system ingests OpenAPI/Swagger definitions and observes its gateway traffic. It automatically tests the registered sandbox APIs for owner authorization, forbidden response fields, missing authentication and rate-limit signals. It produces severity-ranked, actionable findings and records the remediation lifecycle. Arbitrary external API execution is deliberately not inferred from a supplied specification; it requires an explicit adapter and authorization design.

## Every expected solution capability

| Capability | Implementation | Verification / boundary |
|---|---|---|
| Ingest OpenAPI/Swagger or observe live traffic | JSON/basic YAML importer, optional full YAML loader, normalized inventory; real gateway request/response observation | Import the sample and run the attacker; uploaded server URLs are ignored |
| Test BOLA/IDOR across authenticated sessions | Alice baseline, Bob probe, stable ID and owner comparison, path and query IDs | Seeded-positive and repaired-negative tests |
| Excessive data exposure | Nested field walker and policy-confirmed forbidden-field paths; response withholding at gateway | Exposure finding contains `$.private...` paths and redacted values |
| Missing/weak rate limiting and auth misconfiguration | Anonymous access test; eight-request scanner observation; backend known-limit verification; live gateway rate cap | Missing auth is confirmed; lack of a rate response remains an Info observation |
| Ranked, explainable findings | Confirmed High findings and Info observations; sorted UI; human-readable impact and remediation | Findings screen |
| Reproducible proof-of-concept requests | Placeholder credential request pairs, exact method/path, sandbox replay steps | Finding detail and incident detail; gateway may block replay after containment |
| Dashboard/report for technical and nontechnical readers | Posture overview, inventory, scan status, evidence, incident timeline, graph, automation, JSON and standalone HTML export | Browser demonstration and export |
| Continuous/CI scanning | Persistent opt-in scheduler, explicit selected scope, CLI gate and GitHub Actions workflow | `demo_ci.py` proves a risky build blocks and a fixed build passes |

## Every innovation opportunity

| Opportunity | Delivered implementation | Precise status |
|---|---|---|
| LLM reasoning over specs and smarter test cases | Optional Ollama adapter sends sanitized descriptions, validates suggested path/check pairs and prioritizes accepted candidates when selected | Implemented; success/failure/output contracts unit-tested. Requires a separately installed local model for actual inference |
| Autonomous pentest call chains | Separate attacker follows identity → resource enumeration → cross-user read → synthetic delete, adapts to discovered IDs and records each step | Implemented bounded finite-state agent; not unrestricted target discovery |
| NLP to infer intended access boundaries | Offline description parsing recognizes owner/private/belonging language; optional LLM explanations add reasoning | Implemented; exact owner semantics remain explicit in the sandbox policy |
| CI/CD block on risky deployments | CLI returns 1 for confirmed High/Critical risk and 2 for incomplete/error states; workflow tests vulnerable and fixed fixtures | Executed successfully locally |
| Trends across API surface | Persistent per-scan counts, history, API-wide posture, severity-ranked evidence and detailed report data | Implemented; UI recent-scan chart and class breakdown, complete evidence in export |
| Graph analysis for cascading risks | API reference edges, vulnerable-node indication, transitive dependency traversal that stops at isolated nodes | Implemented for the synthetic dependency graph; paths are potential risk, not confirmed exploit chains |

## Every constraint and consideration

| Constraint | Implementation | Limit |
|---|---|---|
| Explicit authorization and sandbox-only testing | Fixed registered API IDs, no arbitrary attacker URL, uploaded server URLs ignored, private backend transport key and Docker network | Extending target scope requires deliberate adapter work |
| Scanner must not become an attack vector | Redaction before persistence; no model credentials or responses in prompts; local UI session; Origin/Host checks; remote references and redirects rejected; size/thread/request caps | Local single-operator security model, not public-service authentication |
| Minimize false positives | Stable resource and owner proof; explicit private field policy; uncertain rate signal labeled observation; invalid baselines cause partial scan | No assertion that unknown APIs share these owner semantics |
| Explainability | Evidence, paths, confidence, timestamp, paired requests, incident narrative, applied controls and verification | Reproduction uses placeholder credentials |
| Reliability and target protection | GET-only scanner, sequential work, strict timeouts, bounded rate probes, cancellation, size caps and stop after repeated errors | Destructive testing exists only in the attacker/fixture with reset capability |
| Hundreds of endpoints | 144 implemented operations; importer supports 1,000 paths; bounded budgets and persisted scans | Fixture families share implementation; this is not a production scale benchmark |
| Accessibility for nonspecialists | Plain-language descriptions, labeled controls, responsive layout, semantic tables, keyboard focus styles, visible error states | Full independent WCAG audit not performed |

## All four hackathon scope items

| Scope item | Evidence |
|---|---|
| Provided sandbox API with seeded flaws | 24 API families, Alice/Bob fixtures, vulnerable and secure controls, reset/rollback |
| OpenAPI scanner with one or two classes | 144-operation definition; BOLA, exposure, auth plus bounded rate observation |
| Report/dashboard with severity and reproduction | Defense dashboard, evidence dialogs, JSON/HTML exports |
| Advanced additions | Optional LLM planner, NLP, bounded multi-step attacker, CI gate, history and dependency graph |

## User-specific additions

| Request | Delivery |
|---|---|
| Whole runnable project | Three Python services, two web apps, SQLite persistence, launcher, tests, CI, Docker files and documentation |
| Extra external attacker application | Separate process and port, HTTP-only interaction with gateway, no shared defender data or credential |
| Many sandbox APIs | 24 families × 6 operations = 144 operations |
| Select one or many target APIs | Multi-select in scan, inventory, scheduler and attacker UI |
| Find flaws, attempt breach and destruction | Evidence-based scans; attacker cross-user, unauthenticated, exposure, rate and disposable-delete scenarios; adaptive bounded chain |
| Automatically detect and stop attacks | Gateway checks requests and responses; isolates on a detected threat; stops forwarding |
| Automatically repair and show what happened | Approved sandbox patch transaction, timestamps, before/after revisions, repair explanation, response restoration and post-repair proof |
| Fix only selected, authorized APIs | Repair authority default deny; per-API checks and locks; integration tests prove containment-only API remains unchanged |
| Isolate APIs without modification authority | Independent gateway isolation policy; no backend patch or restoration without repair authority |
| Manual and autonomous workflows | Manual scan/plan/repair/isolate/verify/release/reset/rollback/export; automatic gateway response and opt-in scheduler |
| Explain deployment, tests and use | README, detailed deployment guide, first-demo sequence, regression suite and CI demo |

## Claims intentionally not made

This project cannot stop traffic bypassing its gateway, guarantee detection of every unknown exploit, safely rewrite arbitrary production API source, or recover unknown real-world data without backups. These limits follow from the actual implementation. Connecting real systems needs explicit authorization and purpose-built adapters. A live local LLM and Docker runtime were unavailable for full runtime validation; those paths are described with that qualification.
