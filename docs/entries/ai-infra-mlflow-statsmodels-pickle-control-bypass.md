# MLflow statsmodels flavor loads pickle artifacts despite the deserialization control

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-mlflow-statsmodels-pickle-control-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Supply chain (model) |
| Target | MLflow 2.1.0 to before 3.15.0 (pip package mlflow), the statsmodels model flavor |
| Disclosure date | 2026-09-01 |
| Last verified | 2026-10-04 |

## Summary

MLflow added an environment-variable control, MLFLOW_ALLOW_PICKLE_DESERIALIZATION, after a run of unsafe pickle loading flaws in its model flavors. The statsmodels flavor never consulted that control: its loader called the pickle-based reader in the statsmodels library directly, while sibling flavors such as sklearn raised an error instead. An attacker who can place a crafted MLmodel artifact into an accessible artifact store therefore gets code execution on any process that loads that model through mlflow.pyfunc.load_model(), even with the control set to False. The advisory lists 3.15.0 as the patched version.

## Impact

The advisory states that the malicious pickle file executes arbitrary code with the privileges of the calling process, and that on default MLflow deployments without the basic-auth app authentication is disabled, so uploading an artifact requires no credentials. The control the operator was told they had set to False gave no protection on this flavor. The compromise is carried by a model artifact planted for another party to load, not by a package resolved in an index, so the direction rule in the taxonomy makes this SUPPLY_CHAIN_MODEL rather than SUPPLY_CHAIN_PACKAGE.

## Mitigation

Upgrade to MLflow 3.15.0 or later. Until then, do not rely on MLFLOW_ALLOW_PICKLE_DESERIALIZATION as the only control: treat any artifact store as untrusted, load only artifacts whose provenance you control, and run mlflow.pyfunc.load_model() in a process that holds nothing worth taking.

## Sources

- **PRIMARY** - [MLFLOW_ALLOW_PICKLE_DESERIALIZATION=False safety control bypassed by mlflow.statsmodels flavor (GHSA-gqvg-gmmx-x4hm)](https://github.com/mlflow/mlflow/security/advisories/GHSA-gqvg-gmmx-x4hm)

Generated from `data/entries/ai-infra-mlflow-statsmodels-pickle-control-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-mlflow-statsmodels-pickle-control-bypass.yml).
