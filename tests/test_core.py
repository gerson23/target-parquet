"""Tests standard target features using the built-in SDK tests library."""

from __future__ import annotations

import json
import shutil
import typing as t
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from singer_sdk.testing import get_target_test_class

from target_parquet.target import TargetParquet, DecimalEncoder

TEST_OUTPUT_DIR = Path(f".output/test_{uuid4()}/")
SAMPLE_CONFIG: dict[str, t.Any] = {
    "destination_path": str(TEST_OUTPUT_DIR),
}


# Run standard built-in target tests from the SDK:
StandardTargetTests = get_target_test_class(
    target_class=TargetParquet,
    config=SAMPLE_CONFIG,
)


class TestTargetParquet(StandardTargetTests):  # type: ignore[misc, valid-type]
    """Standard Target Tests."""

    @pytest.fixture(scope="class")
    def test_output_dir(self):
        return TEST_OUTPUT_DIR

    @pytest.fixture(scope="class")
    def resource(self, test_output_dir):  # noqa: ANN201
        """Generic external resource.

        This fixture is useful for setup and teardown of external resources,
        such output folders, tables, buckets etc. for use during testing.

        Example usage can be found in the SDK samples test suite:
        https://github.com/meltano/sdk/tree/main/tests/samples
        """
        test_output_dir.mkdir(parents=True, exist_ok=True)
        yield test_output_dir
        shutil.rmtree(test_output_dir)


def test_decimal_encoding():
    # States could have decimal values, so we need to ensure they are encoded as floats
    data = {
        "value1": Decimal("10.5"),
        "value2": Decimal("3.14159"),
        "value3": 42,
        "nested": {"value4": Decimal("2.71828")},
        "list_of_values": [Decimal("1.1"), Decimal("2.2"), 3],
    }

    encoded_json = json.dumps(data, cls=DecimalEncoder)
    expected_json = json.dumps({
        "value1": 10.5,
        "value2": 3.14159,
        "value3": 42,
        "nested": {"value4": 2.71828},
        "list_of_values": [1.1, 2.2, 3],
    })
    assert encoded_json == expected_json

def test_non_decimal_types():
    # Test that non-decimal types are not affected by the DecimalEncoder
    data = {
        "value1": 10.5,
        "value2": 42,
        "nested": {"value4": "string_value"},
        "list_of_values": [1.1, 2.2, 3],
    }

    encoded_json = json.dumps(data, cls=DecimalEncoder)
    expected_json = json.dumps(data)
    assert encoded_json == expected_json
