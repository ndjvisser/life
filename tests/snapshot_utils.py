"""Utilities for working with snapshot tests."""

import json
from typing import Any


def assert_json_snapshot(snapshot: Any, data: Any, filename: str) -> None:
    """Serialize data to formatted JSON and assert snapshot match.

    Adds a trailing newline to keep compatibility with stored snapshots.
    """
    serialized = json.dumps(data, indent=2, sort_keys=True) + "\n"
    snapshot.assert_match(serialized, filename)
