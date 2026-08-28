import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bug_monitor
import daily_summary
import language_channels_report
import suggestions_report


LOCAL_TZ = ZoneInfo("Asia/Shanghai")
HOURLY_CFG = SimpleNamespace(
    local_timezone="Asia/Shanghai",
    schedule_start_hour=8,
    schedule_end_hour=22,
    overnight_start_hour=22,
)
DAILY_CFG = SimpleNamespace(
    local_timezone="Asia/Shanghai",
    daily_schedule_time="18:00",
    first_schedule_date=None,
)


class HourlyWindowTests(unittest.TestCase):
    def test_0800_window_starts_at_previous_day_2200(self):
        reference = datetime(2026, 8, 28, 8, 10, tzinfo=LOCAL_TZ)
        for module in (suggestions_report, language_channels_report):
            start_utc, end_utc = module.scheduled_window_for_hour(
                HOURLY_CFG,
                slot_hour=8,
                reference_local=reference,
            )
            self.assertEqual(
                start_utc.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M"),
                "2026-08-27 22:00",
            )
            self.assertEqual(
                end_utc.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M"),
                "2026-08-28 08:00",
            )

    def test_delayed_run_uses_latest_due_boundary(self):
        cases = (
            (datetime(2026, 8, 28, 7, 50, tzinfo=LOCAL_TZ), "2026-08-27 22:00"),
            (datetime(2026, 8, 28, 18, 37, tzinfo=LOCAL_TZ), "2026-08-28 18:00"),
            (datetime(2026, 8, 28, 23, 5, tzinfo=LOCAL_TZ), "2026-08-28 22:00"),
        )
        for module in (suggestions_report, language_channels_report):
            for current, expected in cases:
                actual = module.latest_due_end_utc(HOURLY_CFG, current)
                self.assertEqual(
                    actual.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M"),
                    expected,
                )

    def test_catch_up_starts_from_persisted_boundary(self):
        with patch.dict(
            os.environ,
            {"SUGGESTIONS_LAST_END_UTC": "2026-08-28T10:00:00+00:00"},
            clear=False,
        ):
            start_utc, end_utc = suggestions_report.catch_up_window(
                HOURLY_CFG,
                now_local=datetime(2026, 8, 28, 20, 19, tzinfo=LOCAL_TZ),
            )
        self.assertEqual(start_utc.astimezone(LOCAL_TZ).hour, 18)
        self.assertEqual(end_utc.astimezone(LOCAL_TZ).hour, 20)


class DailyWindowTests(unittest.TestCase):
    def test_before_1800_never_uses_future_window(self):
        with patch.dict(
            os.environ,
            {"DAILY_LAST_REPORTED_DATE": "2026-08-26"},
            clear=False,
        ):
            pending = daily_summary.pending_report_dates(
                DAILY_CFG,
                now_local=datetime(2026, 8, 28, 4, 0, tzinfo=LOCAL_TZ),
            )
        self.assertEqual([str(item) for item in pending], ["2026-08-27"])

    def test_after_1800_catches_all_missing_dates(self):
        with patch.dict(
            os.environ,
            {"DAILY_LAST_REPORTED_DATE": "2026-08-26"},
            clear=False,
        ):
            pending = daily_summary.pending_report_dates(
                DAILY_CFG,
                now_local=datetime(2026, 8, 28, 19, 0, tzinfo=LOCAL_TZ),
            )
        self.assertEqual(
            [str(item) for item in pending],
            ["2026-08-27", "2026-08-28"],
        )


class BugStateTests(unittest.TestCase):
    def test_github_variable_is_used_when_runner_has_no_state_file(self):
        now_utc = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
        expected = now_utc - timedelta(hours=5)
        with tempfile.TemporaryDirectory() as temp_dir, patch.dict(
            os.environ,
            {
                "BUG_LAST_CHECKED_AT_UTC": expected.isoformat(),
                "BUG_STATELESS_LOOKBACK_MINUTES": "10080",
            },
            clear=False,
        ):
            actual = bug_monitor.load_last_checked_at_utc(
                now_utc=now_utc,
                interval_minutes=20,
                state_path=Path(temp_dir) / "missing-state.json",
            )
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
