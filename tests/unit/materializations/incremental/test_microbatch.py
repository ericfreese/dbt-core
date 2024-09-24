from datetime import datetime
from unittest import mock

import pytest
import pytz
from freezegun import freeze_time

from dbt.artifacts.resources import NodeConfig
from dbt.artifacts.resources.types import BatchSize
from dbt.materializations.incremental.microbatch import MicrobatchBuilder


class TestMicrobatchBuilder:
    @pytest.fixture(scope="class")
    def microbatch_model(self):
        model = mock.Mock()
        model.config = mock.MagicMock(NodeConfig)
        model.config.materialized = "incremental"
        model.config.incremental_strategy = "microbatch"

        return model

    @freeze_time("2024-09-05 08:56:00")
    @pytest.mark.parametrize(
        "is_incremental,event_time_end,expected_end_time",
        [
            (
                False,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
            ),
            (
                False,
                datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
                datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                True,
                datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
                datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
            ),
        ],
    )
    def test_build_end_time(
        self, microbatch_model, is_incremental, event_time_end, expected_end_time
    ):
        microbatch_builder = MicrobatchBuilder(
            model=microbatch_model,
            is_incremental=is_incremental,
            event_time_start=None,
            event_time_end=event_time_end,
        )

        assert microbatch_builder.build_end_time() == expected_end_time

    @pytest.mark.parametrize(
        "is_incremental,event_time_start,checkpoint,batch_size,lookback,expected_start_time",
        [
            (
                False,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                0,
                None,
            ),
            # BatchSize.year
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.year,
                0,
                datetime(2024, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.year,
                # Offset not applied when event_time_start provided
                1,
                datetime(2024, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.year,
                0,
                # is_incremental=False + no start_time -> None
                None,
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.year,
                0,
                datetime(2024, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.year,
                1,
                datetime(2023, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            # BatchSize.month
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.month,
                0,
                datetime(2024, 9, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.month,
                # Offset not applied when event_time_start provided
                1,
                datetime(2024, 9, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.month,
                0,
                # is_incremental=False + no start_time -> None
                None,
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.month,
                0,
                datetime(2024, 9, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.month,
                1,
                datetime(2024, 8, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            # BatchSize.day
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                0,
                datetime(2024, 9, 5, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                # Offset not applied when event_time_start provided
                1,
                datetime(2024, 9, 5, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                0,
                # is_incremental=False + no start_time -> None
                None,
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                0,
                datetime(2024, 9, 5, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                1,
                datetime(2024, 9, 4, 0, 0, 0, 0, pytz.UTC),
            ),
            # BatchSize.hour
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.hour,
                0,
                datetime(2024, 9, 5, 8, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.hour,
                # Offset not applied when event_time_start provided
                1,
                datetime(2024, 9, 5, 8, 0, 0, 0, pytz.UTC),
            ),
            (
                False,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.hour,
                0,
                # is_incremental=False + no start_time -> None
                None,
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.hour,
                0,
                datetime(2024, 9, 5, 8, 0, 0, 0, pytz.UTC),
            ),
            (
                True,
                None,
                datetime(2024, 9, 5, 8, 56, 0, 0, pytz.UTC),
                BatchSize.hour,
                1,
                datetime(2024, 9, 5, 7, 0, 0, 0, pytz.UTC),
            ),
        ],
    )
    def test_build_start_time(
        self,
        microbatch_model,
        is_incremental,
        event_time_start,
        checkpoint,
        batch_size,
        lookback,
        expected_start_time,
    ):
        microbatch_model.config.batch_size = batch_size
        microbatch_model.config.lookback = lookback
        microbatch_builder = MicrobatchBuilder(
            model=microbatch_model,
            is_incremental=is_incremental,
            event_time_start=event_time_start,
            event_time_end=None,
        )

        assert microbatch_builder.build_start_time(checkpoint) == expected_start_time

    @pytest.mark.parametrize(
        "start,end,batch_size,expected_batches",
        [
            # BatchSize.year
            (
                datetime(2024, 1, 1, 0, 0, 0, 0, pytz.UTC),
                datetime(2026, 1, 7, 3, 56, 0, 0, pytz.UTC),
                BatchSize.year,
                [
                    (
                        datetime(2024, 1, 1, 0, 0, 0, 0, pytz.UTC),
                        datetime(2025, 1, 1, 0, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2025, 1, 1, 0, 0, 0, 0, pytz.UTC),
                        datetime(2026, 1, 1, 0, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2026, 1, 1, 0, 0, 0, 0, pytz.UTC),
                        datetime(2026, 1, 7, 3, 56, 0, 0, pytz.UTC),
                    ),
                ],
            ),
            # BatchSize.month
            (
                datetime(2024, 9, 1, 0, 0, 0, 0, pytz.UTC),
                datetime(2024, 11, 7, 3, 56, 0, 0, pytz.UTC),
                BatchSize.month,
                [
                    (
                        datetime(2024, 9, 1, 0, 0, 0, 0, pytz.UTC),
                        datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
                        datetime(2024, 11, 1, 0, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2024, 11, 1, 0, 0, 0, 0, pytz.UTC),
                        datetime(2024, 11, 7, 3, 56, 0, 0, pytz.UTC),
                    ),
                ],
            ),
            # BatchSize.day
            (
                datetime(2024, 9, 5, 0, 0, 0, 0, pytz.UTC),
                datetime(2024, 9, 7, 3, 56, 0, 0, pytz.UTC),
                BatchSize.day,
                [
                    (
                        datetime(2024, 9, 5, 0, 0, 0, 0, pytz.UTC),
                        datetime(2024, 9, 6, 0, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2024, 9, 6, 0, 0, 0, 0, pytz.UTC),
                        datetime(2024, 9, 7, 0, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2024, 9, 7, 0, 0, 0, 0, pytz.UTC),
                        datetime(2024, 9, 7, 3, 56, 0, 0, pytz.UTC),
                    ),
                ],
            ),
            # BatchSize.hour
            (
                datetime(2024, 9, 5, 1, 0, 0, 0, pytz.UTC),
                datetime(2024, 9, 5, 3, 56, 0, 0, pytz.UTC),
                BatchSize.hour,
                [
                    (
                        datetime(2024, 9, 5, 1, 0, 0, 0, pytz.UTC),
                        datetime(2024, 9, 5, 2, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2024, 9, 5, 2, 0, 0, 0, pytz.UTC),
                        datetime(2024, 9, 5, 3, 0, 0, 0, pytz.UTC),
                    ),
                    (
                        datetime(2024, 9, 5, 3, 0, 0, 0, pytz.UTC),
                        datetime(2024, 9, 5, 3, 56, 0, 0, pytz.UTC),
                    ),
                ],
            ),
        ],
    )
    def test_build_batches(self, microbatch_model, start, end, batch_size, expected_batches):
        microbatch_model.config.batch_size = batch_size
        microbatch_builder = MicrobatchBuilder(
            model=microbatch_model, is_incremental=True, event_time_start=None, event_time_end=None
        )

        actual_batches = microbatch_builder.build_batches(start, end)
        assert len(actual_batches) == len(expected_batches)
        assert actual_batches == expected_batches

    @pytest.mark.parametrize(
        "timestamp,batch_size,offset,expected_timestamp",
        [
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.year,
                1,
                datetime(2025, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.year,
                -1,
                datetime(2023, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.month,
                1,
                datetime(2024, 10, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.month,
                -1,
                datetime(2024, 8, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.day,
                1,
                datetime(2024, 9, 6, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.day,
                -1,
                datetime(2024, 9, 4, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.hour,
                1,
                datetime(2024, 9, 5, 4, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.hour,
                -1,
                datetime(2024, 9, 5, 2, 0, 0, 0, pytz.UTC),
            ),
        ],
    )
    def test_offset_timestamp(self, timestamp, batch_size, offset, expected_timestamp):
        assert (
            MicrobatchBuilder.offset_timestamp(timestamp, batch_size, offset) == expected_timestamp
        )

    @pytest.mark.parametrize(
        "timestamp,batch_size,expected_timestamp",
        [
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.year,
                datetime(2024, 1, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.month,
                datetime(2024, 9, 1, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.day,
                datetime(2024, 9, 5, 0, 0, 0, 0, pytz.UTC),
            ),
            (
                datetime(2024, 9, 5, 3, 56, 1, 1, pytz.UTC),
                BatchSize.hour,
                datetime(2024, 9, 5, 3, 0, 0, 0, pytz.UTC),
            ),
        ],
    )
    def test_truncate_timestamp(self, timestamp, batch_size, expected_timestamp):
        assert MicrobatchBuilder.truncate_timestamp(timestamp, batch_size) == expected_timestamp

    @pytest.mark.parametrize(
        "batch_size,batch_start,expected_formatted_batch_start",
        [
            (None, None, None),
            (BatchSize.year, datetime(2020, 1, 1, 1), "2020-01-01"),
            (BatchSize.month, datetime(2020, 1, 1, 1), "2020-01-01"),
            (BatchSize.day, datetime(2020, 1, 1, 1), "2020-01-01"),
            (BatchSize.hour, datetime(2020, 1, 1, 1), "2020-01-01 01:00:00"),
        ],
    )
    def test_format_batch_start(self, batch_size, batch_start, expected_formatted_batch_start):
        assert (
            MicrobatchBuilder.format_batch_start(batch_start, batch_size)
            == expected_formatted_batch_start
        )