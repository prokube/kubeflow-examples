# PR #56 review follow-up — action plan

Source: [review](https://github.com/prokube/examples/pull/56#pullrequestreview-5178431816).
The live-testing comment on the same PR is disregarded (cluster was
misconfigured at the time).

Two commits, split by how much confidence we have in the fix without a live
cluster:

- **Commit 1 — shadow-deployment & KEDA** (`serving/minimal-example-shadow-deployment`,
  `serving/kserve-keda-autoscaling`): neither example was ever exercised
  against a real cluster, so every item here is a best-effort fix based on
  code review only and needs live verification before merging with
  confidence.
- **Commit 2 — everything else**: CI harness, cleanup scripts, credential
  helpers, MLflow examples, docs.

---

## Commit 1 — shadow-deployment & KEDA fixes (untested live)

| # | File | Fix |
|---|---|---|
| 1.1 | `serving/minimal-example-shadow-deployment/apply.py:194-197` | Replace `f"-h={host}"`, `f"-U={_PG_USER}"`, `f"-d={_PG_DB}"` with separate `"-h", host, "-U", _PG_USER, "-d", _PG_DB` args — psql short opts don't take `=`. |
| 1.2 | `serving/minimal-example-shadow-deployment/apply.py:261` | Read `body.get("results")` instead of `body.get("predictions")` to match `minimal-predictor/main.py`'s actual response shape. |
| 1.3 | `serving/minimal-example-shadow-deployment/apply.py:34-39` (`_SCHEMA_SQL`) | Rename the `inference_response.request_data` column to `response_data` to match the column name `PredictionDBHandler.py:51` actually inserts into. Also fix `store_batch` (`PredictionDBHandler.py:110-120`) so a DB insert error doesn't get silently swallowed — at minimum log at `ERROR` with the failing query name, ideally surface it so CI can catch persistence breakage. |
| 1.4 | `serving/kserve-keda-autoscaling/apply.py:88-114` (`_wait_scaledobject_active`) | Wait on the ScaledObject's `Ready` condition (or just confirm it exists) right after apply — don't block on `Active`, which only flips once traffic arrives. Move the `Active` check to *after* `load-generator.py` sends traffic. Also raise on a non-zero `kubectl get` exit code instead of silently looping on empty stdout. |
| 1.5 | `serving/minimal-example-shadow-deployment/apply.py:129-153` (`_wait_pg_primary_ready`) | `kubectl wait pod -l cluster=…,role=master` immediately after applying the CR can return `no matching resources found` before the operator creates the pod. Poll for pod existence first (or wait on the PostgresCluster CR's own status) before running `kubectl wait`. |
| 1.6 | `serving/minimal-example-shadow-deployment/apply.py:242-245` (`_smoke_test`) | Point `internal_predict_url` at the top-level doubler ISVC host, not directly at `<isvc>-predictor`, so the transformer (and its Postgres persistence) is actually exercised. |
| 1.7 | `serving/minimal-example-shadow-deployment/cleanup.py:27+` | Cleanup budget in `ci/run_all.py::_run_cleanup` is 120s; sequential blocking deletes of 2 ISVCs + a PostgresCluster (with PVCs) can exceed that and leave the PostgresCluster (and `pg-schema-init` pod) behind. Switch to non-blocking deletes (`--wait=false`) or fire all deletes concurrently before waiting, and explicitly delete the `pg-schema-init` pod. |
| 1.8 | `serving/kserve-keda-autoscaling/apply.py:169-175` | `sys.exit(0)` on "KEDA absent" is reported as `[PASS]` by `ci/run_all.py`. Since this example is already opt-in (`--include-keda`), fail loudly instead (non-zero exit) so a missing KEDA install doesn't masquerade as a pass. (If we later want a real SKIP semantics, that needs a `run_all.py` change too — out of scope for this commit, tracked in Commit 2 notes below if needed.) |
| 1.9 | `serving/kserve-keda-autoscaling/apply.py` (docstring + `_smoke_test`) | Docstring claims the script "verifies KEDA autoscaling" but it only sends one request and never checks replica count. Extend the check to poll `readyReplicas >= 2` (or similar) after driving load with `load-generator.py --mode stable-2`, within the existing timeout budget. |

All of the above need to be validated against a real cluster with
`postgres-operator` / KEDA installed before merging with confidence — these
are code-review fixes only.

---

## Commit 2 — everything else

### CI harness (`ci/run_all.py`)

| # | Line(s) | Fix |
|---|---|---|
| 2.1 | `~1024` (`if __name__ == "__main__"` exit code) | Fold KFP terminal states other than `SUCCEEDED`/`SKIPPED` (FAILED/ERROR/CANCELED/TIMEOUT/POLL_ERROR) into the pass/fail count used for the process exit code, not just `Result.status == "FAIL"`. Today a Phase 2 pipeline can fail and CI still exits 0. |
| 2.2 | `~808-838` (`_await_mobile_price`, inline `_poll_kfp_run` call) | Wrap the inline poll in try/except like `_phase4_poll` already does, so a transient KFP API error doesn't propagate out of the executor block and skip Phases 3–4 + the report. |
| 2.3 | `~18-21` (`_REPO_ROOT`) | Replace `subprocess.check_output(["git", "rev-parse", "--show-toplevel"])` with `Path(__file__).resolve().parents[1]` — avoids a cwd-dependent result. |
| 2.4 | `~346-348` (`_run_notebook` output path) | Output notebooks are keyed by basename only; `notebooks/mobile-price-classification/mobile-price-classifications.ipynb` (Phase 1) and `pipelines/lightweight-components/mobile-price-classifications.ipynb` (Phase 2) collide on `ci/output/mobile-price-classifications.ipynb`. Key the output path by the example name (or a path-derived subdirectory) instead of bare basename. |
| 2.5 | `ci/README.md` (cleanup section) | `_run_cleanup` ignoring non-zero exit codes/stderr is expected behavior (cleanup failures shouldn't fail the example run) — update the README's cleanup contract description to state this explicitly instead of changing the code. |
| 2.6 | `~281-284` (`_EXTRA_CLEANUP_PATHS`) | Investigate why `hparam-tuning/minimal-mnist/cleanup.py` runs on every CI run with no registered `Example` creating it. Register `hparam-tuning/minimal-mnist` as a proper `Example` (with `cleanup=`) if it's meant to run in CI, otherwise drop it from `_EXTRA_CLEANUP_PATHS` so CI stops deleting a same-named experiment a user may have started manually in the shared namespace. |
| 2.7 (optional/low-priority) | `~598-609` (`_print_report`) | SKIP results are currently counted as "passed" in the summary counts. Low priority — leave as is unless trivial to also split out a SKIPPED bucket while touching this file for 2.1. |

### Cleanup scripts

| # | File | Fix |
|---|---|---|
| 2.8 | `notebooks/dask/cleanup.py:9` | `_CLUSTER_NAME = "dask-cluster"` doesn't match `KubeCluster(name="test-cluster", ...)` in `dask_example.ipynb:124` — confirmed mismatch. Change to `"test-cluster"`. |
| 2.9 | `hparam-tuning/minimal-mnist/cleanup.py:9` | `_EXPERIMENT_NAME = "minimal-mnist"` doesn't match `katib-experiment.yaml`'s actual `name: random-mnist` — confirmed mismatch. Change to `"random-mnist"`, and change the `kubectl delete` resource type from bare `experiment` to `experiments.kubeflow.org` to avoid ambiguity with Argo Rollouts' `Experiment` CRD. (Depends on 2.6's decision on whether this cleanup runs at all.) |
| 2.10 | `serving/minimal-s3-model/cleanup.py` | Currently only deletes the InferenceService. Extend to also remove `s3://<ns>-data/minimal-kserve-example/model.joblib` from object storage. (Leftover `model.joblib` / `inferenceservice.yaml` in the git checkout is a notebook/example hygiene issue, not a cleanup.py concern — leave as is unless trivial.) |

### Secrets / credentials (`src/pk_helpers/`)

| # | File | Fix |
|---|---|---|
| 2.11 | `mlflow_credentials.py:64-71` (`setup_mlflow_credentials`) | Skip the overwrite confirmation prompt when `uri`, `username`, and `password` are all supplied as arguments (i.e., non-interactive call) — only prompt when at least one is `None`. Fixes `EOFError` under headless/non-interactive use and makes the setup re-runnable via CLI args. |
| 2.12 | `src/pk_helpers/api_key.py:19-35` (`get_or_create_api_key`) | Wrap the `getpass()` call so an `EOFError` (closed stdin, e.g. under papermill) is caught and re-raised as the documented `RuntimeError("No API key available...")` instead of propagating raw. Also fix the docstring nit — nothing is "created", just resolved/prompted; consider renaming to `get_api_key` or adjusting the docstring wording only (no need to break the public name without checking callers). |

No action (explicitly out of scope per maintainer judgment):
- `mlflow_credentials.py:82` (password visible in `CalledProcessError` argv) — skip.
- `mlflow_credentials.py:118` (`_read_secret` returns `None` on any error) and `mlflow_credentials.py:74` (empty strings accepted) — optional hardening, not worth the complexity for a convenience script; skip for now.

### Notebooks

| # | File | Fix |
|---|---|---|
| 2.13 | `mlflow/mlflow-image-example.ipynb`, `mlflow/mlflow-kfp-example.ipynb` (cell 1) | `setup_mlflow_credentials()` is called before the `%run -n` cell that defines it, causing `NameError` when run top-to-bottom interactively (masked in CI by `ci-skip`). Reorder cells to match `mlflow-quickstart`/mobile-price notebooks (load helpers first, then call). Apply the local fix mentioned as already made but unpushed. |

### Serving examples

| # | File | Fix |
|---|---|---|
| 2.14 | All `serving/*/apply.py` (`hf-vllm-completion`, `kserve-keda-autoscaling`, `minimal-example-shadow-deployment`, `mlflow-kserve-minimal`, `mlflow-kserve-inference-protocols`) | `_ensure_pk_helpers()` / API-key resolution currently happens inside the test step, after 10-20 min of readiness waits. Move the pk_helpers install / API-key resolution to the top of `deploy()` (or before it) so a missing/broken credential fails fast instead of after a long wait. |
| 2.15 | `serving/mlflow-kserve-minimal/apply.py:161-179` (`test()`) + `test_inference_service.py` | `test_inference_service.py` only does `print(response.json())` with no status check — a 401/404/500 is reported as PASS. Add a `raise_for_status()` and an `outputs`/`predictions` key check, matching the validation pattern already used in `hf-vllm-completion/apply.py:_smoke_test` (`"predictions" not in body`). |

### Pipelines

| # | File | Fix |
|---|---|---|
| 2.16 | `pipelines/lightweight-python-package/README.md` | Update stale docs: `python:3.9` → reflect actual default image tag `:v2` (`pipeline.py:19`), and document the `COMPONENTS_IMAGE` env var override instead of "edit `pipeline.py`". |
| 2.17 | `pipelines/lightweight-python-package/submit-cluster.py:19` | Change `enable_caching=True` to `False` to match the sibling `minimal-container-components` example, so repeated CI runs with identical inputs don't silently no-op on cache hits. |

### Nits (judgment calls — do the cheap ones, defer the rest)

| # | File | Decision |
|---|---|---|
| 2.18 | `ci/README.md` (`internal_predict_url` doc) | README's "Upcoming (agentgateway)" bullet says the route is `/v2/models/<m>/infer`, but `src/pk_helpers/kserve_url.py:23-33` builds `/v1/models/<m>:predict` on both the agentgateway and direct-Service branches. Fix the doc to say `v1` for both, matching the code. |
| 2.19 | `serving/hf-vllm-completion/apply.py` | Add a one-line comment noting the deployed manifest is the DistilBERT/HF CPU variant, not the vLLM/Qwen manifest the directory name implies. Remove the unused `import urllib.error` here and in `kserve-keda-autoscaling/apply.py`. |
| 2.20 | `serving/mlflow-kserve-inference-protocols/apply.py:181` | Log message calls `len(result[pred_key])` for the v2 case, which is a tensor/output count (1), not a prediction count — reword the log line to say "output(s)" for v2 rather than implying prediction count. Low priority; skip unused-variable/context-manager nits (`open()` without `with`, unused `proto` loop var) unless touching this file anyway. |
| — | `serving/mlflow-kserve-minimal/apply.py:102` (dropped `.status.conditions` in error) | **Don't touch** — explicit maintainer call. |
| — | `notebooks/mnist-vae/run_training.py:5` (re-exec guard / `LD_LIBRARY_PATH`) | **Don't touch** — works today, root cause is upstream image, not worth the churn now. |
| — | `serving/mlflow-kserve-inference-protocols/inference_protocol_version_example.ipynb` §6 (`ci-skip` dead comment) | Deferred to a future PR. |
| — | `ci/run_all.py:905` (`ThreadPoolExecutor.__exit__` on Ctrl-C not cancelling queued futures) | No clear problem statement / repro — no action. |
| — | Duplication across `apply.py`/`cleanup.py` scripts (`_namespace`, `_ensure_pk_helpers`, `_kubectl_delete`, `_mlflow_username`/`_apply_yaml`/`_wait_ready`/`_isvc_url`) | **Rejected** — every example is intentionally self-contained; this is not duplication to fix. |
| — | Notebooks hardcoding `%run -n ~/examples/src/pk_helpers/*.py` | **Rejected** — this is the agreed simplest/most readable pattern; repo is always cloned to `$HOME/examples` in our images. Consider adding a one-line comment noting the path assumption (optional, not required). |
| — | `mlflow-isvc-sa` byte-identical across the two MLflow serving examples | **Rejected** — self-contained by design, not duplication to dedupe. |

---

## Notes on items the review flagged but that "were never tested live"

Per PR discussion, the shadow-deployment and KEDA examples were never run
against a real cluster, so items 1.1–1.9 above should be treated as
best-effort fixes pending a live verification run (with
`--include-shadow --include-keda`) before being trusted.
