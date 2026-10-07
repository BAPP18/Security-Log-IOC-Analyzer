# Contributing

## Local setup

```bash
git clone https://github.com/BAPP18/Security-Log-IOC-Analyzer.git
cd Security-Log-IOC-Analyzer

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY="local-dev-secret"
export SEED_DEMO_USERS=true
python app.py
```

Windows PowerShell:

```powershell
$env:SECRET_KEY="local-dev-secret"
$env:SEED_DEMO_USERS="true"
python app.py
```

## Quality checks

Run before committing:

```bash
python -m compileall -q app.py config.py models routes services utils tests
python -m unittest discover -s tests -v
```

## Detection engineering rules

When changing IOC extraction or triage:

- add at least one positive fixture;
- add at least one benign/false-positive fixture;
- keep extraction confidence separate from maliciousness;
- preserve explainability of scoring;
- avoid depending on live external reputation services in unit tests;
- do not silently turn enrichment-provider output into a confirmed verdict;
- document any new heuristic and its expected failure modes.

## Data safety

Never commit:

- real customer logs;
- credentials;
- API keys;
- generated databases;
- upload/export artifacts;
- private threat-intelligence datasets.

Use synthetic fixtures in `sample_logs/` and tests.
