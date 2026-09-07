import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
WORKFLOW = (ROOT / ".github/workflows/build-images.yaml").read_text()
MAKEFILE = (ROOT / "Makefile").read_text()


class BuildImagesWorkflowContractTest(unittest.TestCase):
    def test_release_tag_contract(self) -> None:
        self.assertIn("tags:\n    - 'v*'", WORKFLOW)
        self.assertIn("^v[0-9]+\\.[0-9]+\\.[0-9]+(-rc[0-9]+)?$", WORKFLOW)
        self.assertIn('echo "tag=$REF_NAME"', WORKFLOW)

    def test_every_dockerfile_is_a_release_artifact(self) -> None:
        dockerfiles = {
            path.relative_to(ROOT).as_posix() for path in ROOT.rglob("Dockerfile")
        }
        configured = set(
            re.findall(r"^          dockerfile: (.+)$", WORKFLOW, re.MULTILINE)
        )
        self.assertEqual(configured, dockerfiles)

    def test_release_pushes_one_unchanged_tag(self) -> None:
        release = WORKFLOW.split("    - name: Build and push release image", 1)[1]
        release = release.split("    - name: Build and push development image", 1)[0]
        self.assertIn("prokube/releases", WORKFLOW)
        self.assertEqual(release.count("        tags:"), 1)
        self.assertIn(
            "tags: ${{ env.REGISTRY }}/${{ matrix.image }}:"
            "${{ needs.prepare.outputs.tag }}",
            release,
        )
        self.assertNotIn("latest", release)
        self.assertNotIn("commit-", release)
        self.assertNotIn("prokube/development", release)

    def test_existing_release_check_only_accepts_not_found(self) -> None:
        check = WORKFLOW.split("    - name: Check immutable release artifact", 1)[1]
        check = check.split("    - name: Build and push release image", 1)[0]
        self.assertIn("gcloud artifacts docker images describe", check)
        self.assertIn("elif grep -q 'NOT_FOUND'", check)
        self.assertIn('cat "$ERROR_FILE" >&2', check)
        self.assertIn("exit 1", check)

    def test_non_release_builds_only_use_development_registry(self) -> None:
        self.assertIn("prokube/development", WORKFLOW)
        self.assertNotIn("prokube-internal", WORKFLOW)
        self.assertIn(
            "override REGISTRY := " "europe-west3-docker.pkg.dev/prokube/development",
            MAKEFILE,
        )
        self.assertNotIn("prokube/releases", MAKEFILE)


if __name__ == "__main__":
    unittest.main()
