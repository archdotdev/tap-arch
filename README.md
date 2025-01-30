# tap-arch

`tap-arch` is a Singer tap for Arch.dev, a platform that enables the creation of end-to-end data platforms with AI-powered analytics capabilities. This tap is designed to extract data from the Arch.dev platform, allowing the Arch team to analyze platform usage, customer interactions, and operational metrics.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

This tap is maintained as a private repository. Install directly from GitHub:

```bash
pipx install git+https://github.com/archdotdev/tap-arch.git@main
```

## Configuration

### Accepted Config Options

The tap accepts the following configuration options:

| Option       | Type          | Required | Default              | Description                                                       |
| ------------ | ------------- | -------- | -------------------- | ----------------------------------------------------------------- |
| `auth_token` | String        | Yes      | None                 | The personal access token to authenticate against the API service |
| `org_ids`    | Array[String] | Yes      | None                 | Project IDs to replicate                                          |
| `api_url`    | String        | No       | https://api.arch.dev | The base url for the Arch API                                     |
| `user_agent` | String        | No       | None                 | A custom User-Agent header to send with each request              |

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-arch --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

Authentication with the Arch.dev API requires a Personal Access Token. It is recommended to generate a dedicated Personal Access Token for use with this tap. This token should be provided in the configuration as the `auth_token` parameter.

For security purposes, it's recommended to store the authentication token in an environment variable or secure secrets management system rather than directly in configuration files.

## Usage

You can easily run `tap-arch` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-arch --version
tap-arch --help
tap-arch --config CONFIG --discover > ./catalog.json
```

## Adding New Streams

The tap-arch project follows a streamlined process for adding new streams that pull data from the Arch.dev API. Here's the step-by-step process:

### 1. Update OpenAPI Schema

First, fetch the latest OpenAPI specification from the Arch.dev API:

```bash
./scripts/get_openapi.sh
```

This will download the latest `openapi.json` to `tap_arch/schemas/`.

### 2. Generate Individual Schema Files

Next, extract individual schema files for each component:

```bash
./scripts/get_all_components.sh
```

This script will create separate JSON schema files for each component in the OpenAPI specification under `tap_arch/schemas/`.

### 3. Resolve Schema References and Flatten Structure

Some schema files may contain references to other components and deeply nested objects. Due to circular references in the OpenAPI specification and the need to design an appropriate relational structure, we can't fully automate this process. Instead, use the provided prompt in `prompts/expand_jsonschema.md` to guide decisions about how to handle each reference and nested object. For each one, you'll need to decide whether to:

- Fully resolve it by including the complete referenced schema
- Replace it with an ID field that can be used to join to another stream
- Flatten nested objects into separate streams with appropriate ID relationships

This manual process allows you to make intentional decisions about data modeling, such as:
- Which nested objects should become their own streams
- What relationships should be maintained between streams
- How to handle circular references in a way that makes sense for analytics
- When to preserve nested structures vs. when to normalize them into separate streams

The goal is to create a set of streams that balance data completeness with usability for downstream analytics.

### 4. Create the Stream Class

Add a new stream class in `tap_arch/streams.py`. Stream classes inherit from `ArchStream` and should follow this pattern:

```python
class NewStream(ArchStream):
    """Define custom stream."""

    name = "stream_name"  # The name of your stream
    path = "/v1/path/to/endpoint/"  # The API endpoint path

    replication_key = None  # Add if the stream supports incremental replication
    schema_filepath = SCHEMAS_DIR / "schema_file.json"  # Point to your schema file

    # If this is a child stream, specify the parent
    parent_stream_type = ParentStream  # Optional

    # If this stream will have child streams, implement this method
    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "some_id": record["id"],
            # Include any other context needed by child streams
        }
```

### 5. Register the Stream

Add your new stream to the `discover_streams()` method in `tap_arch/tap.py`:

```python
def discover_streams(self) -> list[streams.ArchStream]:
    """Return a list of discovered streams."""
    return [
        # ... existing streams ...
        streams.NewStream(self),
    ]
```

### Stream Hierarchy

The tap supports hierarchical data extraction with parent-child relationships:

- `OrgsStream` (root)
  - `ProjectsStream`
    - `TenantsStream`
      - `PipelinesStream`
      - `DatabasesStream`
        - `TransformsStream`
    - `GitRepositoriesStream`
    - `WebhooksStream`
    - `ChatThreadsStream`
      - `ChatMessagesStream`

When adding a new stream, consider where it fits in this hierarchy and set the `parent_stream_type` accordingly.

### Best Practices

1. **Schema First**: Always start with the schema definition before implementing the stream class.
2. **Context Passing**: When implementing child streams, ensure all necessary IDs are passed through the `get_child_context` method.
3. **Data Normalization**: If the API response needs transformation before matching the schema, override the `get_records` method as shown in the `PipelinesStream` class.
4. **Path Parameters**: Use curly braces in the `path` property to indicate parameters that should be filled from the context (e.g., `{org_id}`).

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
then run:

```bash
poetry run pytest
```

You can also test the `tap-arch` CLI interface directly using `poetry run`:

```bash
poetry run tap-arch --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-arch
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-arch --version
# OR run a test `elt` pipeline:
meltano run tap-arch target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

```

```
