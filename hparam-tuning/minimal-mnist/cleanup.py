"""Delete the minimal MNIST Katib experiment and its trial pods."""

from __future__ import annotations

import argparse
import subprocess
import sys

_EXPERIMENT_NAME = "random-mnist"  # must match katib-experiment.yaml's metadata.name


def _namespace() -> str:
    with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace") as fh:
        return fh.read().strip()


def _kubectl_delete(*args: str, dry_run: bool = False) -> None:
    cmd = ["kubectl", "delete", *args, "--ignore-not-found"]
    if dry_run:
        print(f"[dry-run] {' '.join(cmd)}")
        return
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"WARNING: {result.stderr.strip()}", file=sys.stderr)
    else:
        print(result.stdout.strip() or f"deleted (or not found): {' '.join(args)}")


def cleanup(dry_run: bool = False) -> None:
    ns = _namespace()
    # experiments.kubeflow.org, not the bare "experiment" resource type,
    # which is ambiguous on clusters with Argo Rollouts installed.
    # Deleting the Experiment cascades to Trials via owner references.
    _kubectl_delete(
        "experiments.kubeflow.org", _EXPERIMENT_NAME, "-n", ns, dry_run=dry_run
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing them"
    )
    args = parser.parse_args()
    cleanup(dry_run=args.dry_run)
