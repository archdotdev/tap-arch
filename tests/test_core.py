"""Tests standard tap features using the built-in SDK tests library."""

import os

from singer_sdk.testing import get_tap_test_class

from tap_arch.tap import TapArch

SAMPLE_CONFIG = {
    "auth_token": os.environ.get("TAP_ARCH_AUTH_TOKEN"),
    "org_ids": os.environ.get("TAP_ARCH_ORG_IDS"),
}


# Run standard built-in tap tests from the SDK:
TestTapArch = get_tap_test_class(
    tap_class=TapArch,
    config=SAMPLE_CONFIG,
)
