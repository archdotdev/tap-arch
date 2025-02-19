"""Arch tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_arch import streams


class TapArch(Tap):
    """Arch tap class."""

    name = "tap-arch"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,
            title="Auth Token",
            description="The personal access token to authenticate against the API service",  # noqa: E501
        ),
        th.Property(
            "org_ids",
            th.ArrayType(th.StringType),
            required=True,
            title="Org IDs",
            description="Organization IDs to replicate",
        ),
        th.Property(
            "api_url",
            th.StringType,
            title="API URL",
            default="https://api.arch.dev",
            description="The base url for the Arch API",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            description=("A custom User-Agent header to send with each request."),
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.ArchStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.OrgsStream(self),
            streams.TenantsStream(self),
            streams.PipelinesStream(self),
            streams.PipelineSyncsStream(self),
            streams.DatabasesStream(self),
            streams.TransformsStream(self),
            streams.TransformSyncsStream(self),
            streams.GitRepositoriesStream(self),
            streams.WebhooksStream(self),
            streams.ChatThreadsStream(self),
            streams.ChatMessagesStream(self),
            streams.ConnectorsStream(self),
        ]


if __name__ == "__main__":
    TapArch.cli()