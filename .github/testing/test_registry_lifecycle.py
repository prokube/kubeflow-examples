import base64
import importlib.util
import io
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).parents[2]
WORKFLOW = (ROOT / ".github/workflows/build-images.yaml").read_text()
MAKEFILE = (ROOT / "Makefile").read_text()


def load(name: str):
    path = ROOT / ".github/scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


resolve_build = load("resolve_build")
registry_manifest = load("registry_manifest")


class BuildRoutingTest(unittest.TestCase):
    def test_pull_request_is_build_only(self) -> None:
        build = resolve_build.resolve(
            "pull_request", "refs/pull/66/merge", "66/merge", "abc123"
        )
        self.assertFalse(build.publish)
        self.assertFalse(build.release)
        self.assertEqual(build.registry, resolve_build.DEVELOPMENT_REGISTRY)

    def test_main_and_manual_publish_development(self) -> None:
        for event, ref in (
            ("push", "refs/heads/main"),
            ("workflow_dispatch", "refs/tags/v1.2.3"),
        ):
            with self.subTest(event=event, ref=ref):
                build = resolve_build.resolve(event, ref, "main", "abc123")
                self.assertTrue(build.publish)
                self.assertFalse(build.release)
                self.assertEqual(build.registry, resolve_build.DEVELOPMENT_REGISTRY)

    def test_untrusted_or_unconfigured_events_do_not_publish(self) -> None:
        for event, ref in (
            ("pull_request", "refs/pull/66/merge"),
            ("push", "refs/heads/feature/test"),
            ("schedule", "refs/heads/main"),
        ):
            with self.subTest(event=event, ref=ref):
                self.assertFalse(
                    resolve_build.resolve(event, ref, "test", "abc123").publish
                )

    def test_release_uses_unchanged_tag(self) -> None:
        for tag in ("v0.0.0", "v1.2.3", "v10.20.30-rc0", "v1.0.0-rc12"):
            with self.subTest(tag=tag):
                build = resolve_build.resolve("push", f"refs/tags/{tag}", tag, "sha")
                self.assertTrue(build.publish)
                self.assertTrue(build.release)
                self.assertEqual(build.registry, resolve_build.RELEASE_REGISTRY)
                self.assertEqual(build.tag, tag)

    def test_release_rejects_invalid_or_zero_padded_tags(self) -> None:
        for tag in (
            "1.2.3",
            "v1.2",
            "v01.2.3",
            "v1.02.3",
            "v1.2.03",
            "v1.2.3-rc01",
            "v1.2.3-rc",
            "v1.2.3-rc1-extra",
        ):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                resolve_build.resolve("push", f"refs/tags/{tag}", tag, "sha")


class RegistryManifestTest(unittest.TestCase):
    def error(self, status: int, codes: list[str]) -> HTTPError:
        body = {"errors": [{"code": code} for code in codes]}
        return HTTPError(
            "https://registry.example/v2/image/manifests/tag",
            status,
            "error",
            {},
            io.BytesIO(registry_manifest.json.dumps(body).encode()),
        )

    def test_accepts_image_indexes_and_existing_manifest(self) -> None:
        seen = {}

        def opener(request, timeout):
            seen["accept"] = request.headers["Accept"]
            seen["authorization"] = request.headers["Authorization"]
            seen["timeout"] = timeout
            return io.BytesIO(b"manifest")

        self.assertTrue(
            registry_manifest.manifest_exists(
                "registry.example",
                "project/repository/image",
                "v1.2.3",
                "token",
                opener,
            )
        )
        self.assertIn("image.index", seen["accept"])
        self.assertIn("manifest.list", seen["accept"])
        scheme, encoded = seen["authorization"].split(" ", 1)
        self.assertEqual(scheme, "Basic")
        self.assertEqual(base64.b64decode(encoded).decode(), "oauth2accesstoken:token")
        self.assertEqual(seen["timeout"], 30)

    def test_manifest_and_first_image_absence_are_safe(self) -> None:
        for code in ("MANIFEST_UNKNOWN", "NAME_UNKNOWN"):
            with self.subTest(code=code):
                opener = lambda request, timeout: (_ for _ in ()).throw(
                    self.error(404, [code])
                )
                self.assertFalse(
                    registry_manifest.manifest_exists(
                        "registry.example",
                        "project/repository/image",
                        "v1.2.3",
                        "token",
                        opener,
                    )
                )

    def test_auth_registry_and_network_errors_fail(self) -> None:
        errors = (
            self.error(401, ["UNAUTHORIZED"]),
            self.error(404, ["DENIED"]),
            URLError("network unavailable"),
        )
        for error in errors:
            with self.subTest(error=error), self.assertRaises(RuntimeError):
                opener = lambda request, timeout: (_ for _ in ()).throw(error)
                registry_manifest.manifest_exists(
                    "registry.example",
                    "project/repository/image",
                    "v1.2.3",
                    "token",
                    opener,
                )


class WorkflowContractTest(unittest.TestCase):
    def test_every_dockerfile_is_a_release_artifact(self) -> None:
        dockerfiles = {
            path.relative_to(ROOT).as_posix() for path in ROOT.rglob("Dockerfile")
        }
        configured = {
            line.strip().removeprefix("dockerfile: ")
            for line in WORKFLOW.splitlines()
            if line.strip().startswith("dockerfile: ")
        }
        self.assertEqual(configured, dockerfiles)

    def test_prepare_executes_contract_tests(self) -> None:
        prepare = WORKFLOW.split("  prepare:", 1)[1].split("  build:", 1)[0]
        self.assertIn("python3 .github/testing/test_registry_lifecycle.py", prepare)

    def test_pull_requests_cannot_authenticate_or_push(self) -> None:
        pull_request = WORKFLOW.split("    - name: Build pull request image", 1)[1]
        pull_request = pull_request.split("    - name: Build and push release", 1)[0]
        self.assertIn("if: github.event_name == 'pull_request'", pull_request)
        self.assertIn("push: false", pull_request)
        self.assertNotIn("secrets.", pull_request)
        for name in (
            "Authenticate to Google Cloud",
            "Log in to Google Artifact Registry",
        ):
            step = WORKFLOW.split(f"    - name: {name}", 1)[1].split("\n\n", 1)[0]
            self.assertIn("if: github.event_name != 'pull_request'", step)

    def test_release_pushes_one_unchanged_tag(self) -> None:
        release = WORKFLOW.split("    - name: Build and push release image", 1)[1]
        release = release.split("    - name: Build and push development image", 1)[0]
        self.assertEqual(release.count("        tags:"), 1)
        self.assertIn("${{ needs.prepare.outputs.tag }}", release)
        self.assertNotIn("latest", release)
        self.assertNotIn("commit-", release)

    def test_development_tags_never_include_an_empty_entry(self) -> None:
        development = WORKFLOW.split("    - name: Build and push development image", 1)[
            1
        ]
        self.assertNotIn("tags: |", development)
        self.assertIn("tags: ${{ github.event_name == 'push'", development)
        self.assertIn("{0}/{1}:{2},{0}/{1}:latest", development)
        self.assertIn("|| format('{0}/{1}:{2}'", development)

    def test_release_checks_repository_before_manifest(self) -> None:
        repository = WORKFLOW.index("gcloud artifacts repositories describe")
        manifest = WORKFLOW.index("registry_manifest.py")
        self.assertLess(repository, manifest)

    def test_local_builds_reject_official_release_registry(self) -> None:
        self.assertIn("REGISTRY ?=", MAKEFILE)
        self.assertIn("local builds must not target", MAKEFILE)


if __name__ == "__main__":
    unittest.main()
