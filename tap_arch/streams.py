"""Stream type classes for tap-arch."""

from __future__ import annotations

import typing as t
from importlib import resources
from functools import cached_property
from tap_arch.client import ArchStream

SCHEMAS_DIR = resources.files(__package__) / "schemas"


class OrgsStream(ArchStream):
    """Define custom stream."""

    name = "orgs"
    path = "/v1/orgs/"

    replication_key = None
    schema_filepath = SCHEMAS_DIR / "org.json"

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for a child stream."""
        return {"org_id": record["id"]}

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """Return a generator of records."""
        # If we define org_ids in the config, only return records for those orgs
        if self.config.get("org_ids"):
            for record in super().get_records(context):
                if record["id"] in self.config["org_ids"]:
                    yield record
        # Otherwise, return all records
        else:
            yield from super().get_records(context)


class GitRepositoriesStream(ArchStream):
    """Define Git Repositories stream."""

    name = "git_repositories"
    path = "/v1/orgs/{org_id}/git_repositories/"
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "git_repository.json"
    parent_stream_type = OrgsStream


class WebhooksStream(ArchStream):
    """Define Webhooks stream."""

    name = "webhooks"
    path = "/v1/orgs/{org_id}/webhooks/"
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "webhook.json"
    parent_stream_type = OrgsStream


class ChatThreadsStream(ArchStream):
    """Define Chat Threads stream."""

    name = "chat_threads"
    path = "/v1/orgs/{org_id}/chats/"
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "chat_thread.json"
    parent_stream_type = OrgsStream

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for a child stream."""
        return {
            "org_id": context["org_id"],
            "chat_thread_id": record["id"],
        }


class ChatMessagesStream(ArchStream):
    """Define Chat Messages stream."""

    name = "chat_messages"
    path = "/v1/orgs/{org_id}/chats/{chat_thread_id}/messages/"
    schema_filepath = SCHEMAS_DIR / "chat_message.json"
    parent_stream_type = ChatThreadsStream


class TenantsStream(ArchStream):
    """Define Tenants stream."""

    name = "tenants"
    path = "/v1/orgs/{org_id}/tenants/"
    schema_filepath = SCHEMAS_DIR / "tenant.json"
    parent_stream_type = OrgsStream

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for a child stream."""
        return {
            "org_id": context["org_id"],
            "tenant_id": record["id"],
        }


class ConnectorsStream(ArchStream):
    """Define Connectors stream."""

    name = "connectors"
    path = "/v1/orgs/{org_id}/connectors/"
    schema_filepath = SCHEMAS_DIR / "meltano_plugin.json"
    parent_stream_type = OrgsStream


class PipelinesStream(ArchStream):
    """Define Pipelines stream."""

    name = "pipelines"
    path = "/v1/orgs/{org_id}/tenants/{tenant_id}/pipelines/"
    schema_filepath = SCHEMAS_DIR / "pipeline.json"
    parent_stream_type = TenantsStream

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """Return a generator of records."""
        for record in super().get_records(context):
            normalized = self.normalize_record(record)
            normalized["extractor_config"] = str(record["extractor_config"])
            normalized["loader_config"] = str(record["loader_config"])
            yield normalized

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for a child stream."""
        return {
            "org_id": context["org_id"],
            "tenant_id": context["tenant_id"],
            "pipeline_id": record["id"],
        }


class PipelineSyncsStream(ArchStream):
    """Define Pipeline Syncs stream."""

    records_jsonpath = "$.results[*]"
    name = "pipeline_syncs"
    path = "/v1/orgs/{org_id}/tenants/{tenant_id}/pipelines/{pipeline_id}/syncs/"
    schema_filepath = SCHEMAS_DIR / "sync.json"
    parent_stream_type = PipelinesStream


class DatabasesStream(ArchStream):
    """Define databases stream."""

    name = "databases"
    path = "/v1/orgs/{org_id}/tenants/{tenant_id}/databases/"
    schema_filepath = SCHEMAS_DIR / "database.json"
    parent_stream_type = TenantsStream

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for a child stream."""
        return {
            "org_id": context["org_id"],
            "tenant_id": context["tenant_id"],
            "database_id": record["id"],
        }


class TransformsStream(ArchStream):
    """Define Transforms stream."""

    name = "transforms"
    path = "/v1/orgs/{org_id}/tenants/{tenant_id}/databases/{database_id}/transforms/"
    schema_filepath = SCHEMAS_DIR / "transform.json"
    parent_stream_type = DatabasesStream

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for a child stream."""
        return {
            "org_id": context["org_id"],
            "tenant_id": context["tenant_id"],
            "database_id": context["database_id"],
            "transform_id": record["id"],
        }


class TransformSyncsStream(ArchStream):
    """Define Transform Syncs stream."""

    name = "transform_syncs"
    records_jsonpath = "$.results[*]"
    path = "/v1/orgs/{org_id}/tenants/{tenant_id}/databases/{database_id}/transforms/{transform_id}/syncs/"
    schema_filepath = SCHEMAS_DIR / "sync.json"
    parent_stream_type = TransformsStream
