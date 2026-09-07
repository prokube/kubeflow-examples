import os
import re
from dataclasses import dataclass

DEVELOPMENT_REGISTRY = "europe-west3-docker.pkg.dev/prokube/development"
RELEASE_REGISTRY = "europe-west3-docker.pkg.dev/prokube/releases"
NUMBER = r"(?:0|[1-9][0-9]*)"
RELEASE_TAG = re.compile(rf"^v{NUMBER}\.{NUMBER}\.{NUMBER}(?:-rc{NUMBER})?$")


@dataclass(frozen=True)
class Build:
    registry: str
    tag: str
    publish: bool
    release: bool


def resolve(event: str, ref: str, ref_name: str, sha: str) -> Build:
    release = event == "push" and ref.startswith("refs/tags/")
    if release and not RELEASE_TAG.fullmatch(ref_name):
        raise ValueError("Release tag must match vX.Y.Z or vX.Y.Z-rcN")

    publish = (
        release
        or event == "workflow_dispatch"
        or (event == "push" and ref == "refs/heads/main")
    )

    return Build(
        registry=RELEASE_REGISTRY if release else DEVELOPMENT_REGISTRY,
        tag=ref_name if release else f"commit-{sha}",
        publish=publish,
        release=release,
    )


def main() -> None:
    build = resolve(
        os.environ["GITHUB_EVENT_NAME"],
        os.environ["GITHUB_REF"],
        os.environ["GITHUB_REF_NAME"],
        os.environ["GITHUB_SHA"],
    )
    values = {
        "registry": build.registry,
        "tag": build.tag,
        "publish": str(build.publish).lower(),
        "release": str(build.release).lower(),
    }
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
