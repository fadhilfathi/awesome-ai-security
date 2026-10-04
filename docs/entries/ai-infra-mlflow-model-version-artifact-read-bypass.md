# MLflow CreateModelVersion authorization bypass reads another user's model artifacts

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-mlflow-model-version-artifact-read-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Data exfiltration |
| Target | MLflow before 3.15.0 (pip package mlflow) with the built-in basic-auth plugin |
| Disclosure date | 2026-08-17 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-69148 |

## Summary

MLflow's CreateModelVersion handler checked that a submitted model-version source path sat inside the artifact directory of the run or model it referenced, but it did not check whether the caller had READ permission on that run. An authenticated user could therefore create a model version whose source points at another user's artifact directory and then download files from it through the model-version artifact endpoint, which derives its path from the stored source rather than re-checking the caller's rights. The advisory reports the bypass validated on v3.13.0 and fixed in 3.15.0.

## Impact

Any authenticated user who can create a registered model could read files from any other user's artifact directory, which the advisory names as model weights, training data samples and evaluation reports, in deployments where the experiment-level READ gate would otherwise answer 403. The items that cross the boundary are records and artifacts rather than a named credential, so the taxonomy tie-break on the item set makes this DATA_EXFILTRATION. The advisory's own proof of concept retrieved a file called secret_weights.txt; no source states that any real deployment was exploited.

## Mitigation

Upgrade to MLflow 3.15.0 or later, which requires READ permission on the source run or model. Until then do not rely on experiment-level permission separation alone: keep artifact directories unreadable across tenants, and audit model versions whose source path points outside the runs the creator owns.

## Sources

- **PRIMARY** - [CreateModelVersion source validation does not check READ permission on referenced run_id (GHSA-gqch-g4w5-7qcw)](https://github.com/mlflow/mlflow/security/advisories/GHSA-gqch-g4w5-7qcw)
- **PRIMARY** - [CVE-2026-69148 CVE record for the MLflow model version authorization bypass](https://cveawg.mitre.org/api/cve/CVE-2026-69148)

Generated from `data/entries/ai-infra-mlflow-model-version-artifact-read-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-mlflow-model-version-artifact-read-bypass.yml).
