import argparse
import base64
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

MEDIA_TYPES = (
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
)
ABSENT_CODES = {"MANIFEST_UNKNOWN", "NAME_UNKNOWN"}


def manifest_exists(
    registry: str,
    image: str,
    tag: str,
    token: str,
    opener=urlopen,
) -> bool:
    path = quote(f"{image}/manifests/{tag}", safe="/")
    credentials = base64.b64encode(f"oauth2accesstoken:{token}".encode()).decode()
    request = Request(
        f"https://{registry}/v2/{path}",
        headers={
            "Accept": ", ".join(MEDIA_TYPES),
            "Authorization": f"Basic {credentials}",
        },
        method="GET",
    )
    try:
        response = opener(request, timeout=30)
        response.close()
        return True
    except HTTPError as error:
        body = error.read()
        if error.code != 404:
            raise RuntimeError(f"registry returned HTTP {error.code}") from error
        try:
            errors = json.loads(body).get("errors", [])
            codes = {item["code"] for item in errors}
        except (AttributeError, KeyError, TypeError, ValueError) as cause:
            raise RuntimeError("registry returned an invalid 404 response") from cause
        if codes and codes <= ABSENT_CODES:
            return False
        detail = ", ".join(sorted(codes)) or "no error code"
        raise RuntimeError(
            f"registry returned unexpected 404 error: {detail}"
        ) from error
    except URLError as error:
        raise RuntimeError(f"registry request failed: {error.reason}") from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    exists = manifest_exists(
        args.registry,
        args.image,
        args.tag,
        os.environ["REGISTRY_TOKEN"],
    )
    print("exists" if exists else "absent")


if __name__ == "__main__":
    main()
