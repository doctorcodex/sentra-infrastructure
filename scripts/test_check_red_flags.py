import unittest
import os
import shutil
import tempfile
from check_red_flags import (
    get_today_date,
    check_version_mismatch,
    check_missing_logs,
    check_notam_entries,
    calculate_completion_rate,
    check_completion_rate,
    write_health_report,
)

class TestCheckRedFlags(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.agents = ["dexton", "kade"]

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_get_today_date_with_override(self):
        self.assertEqual(get_today_date(self.test_dir, "2023-10-27"), "2023-10-27")

    def test_check_version_mismatch(self):
        hub_dir = os.path.join(self.test_dir, "hub")
        os.makedirs(hub_dir)
        sessions_dir = os.path.join(hub_dir, "sessions")
        os.makedirs(sessions_dir)

        with open(os.path.join(hub_dir, "version.json"), "w") as f:
            f.write('{"version": "2023-10-26"}')
        with open(os.path.join(sessions_dir, "2023-10-27.md"), "w") as f:
            f.write("test session")

        self.assertEqual(check_version_mismatch(self.test_dir), "Version mismatch.")

    def test_check_no_version_mismatch(self):
        hub_dir = os.path.join(self.test_dir, "hub")
        os.makedirs(hub_dir)
        sessions_dir = os.path.join(hub_dir, "sessions")
        os.makedirs(sessions_dir)

        with open(os.path.join(hub_dir, "version.json"), "w") as f:
            f.write('{"version": "2023-10-27"}')
        with open(os.path.join(sessions_dir, "2023-10-27.md"), "w") as f:
            f.write("test session")

        self.assertIsNone(check_version_mismatch(self.test_dir))

    def test_check_missing_logs(self):
        agents_dir = os.path.join(self.test_dir, "agents")
        os.makedirs(os.path.join(agents_dir, "dexton"))
        with open(os.path.join(agents_dir, "dexton", "log.md"), "w") as f:
            f.write("# log — 2023-10-27")

        missing = check_missing_logs(self.test_dir, "2023-10-27", self.agents)
        self.assertEqual(missing, ["Missing log: kade."])

    def test_check_notam_entries(self):
        notam_dir = os.path.join(self.test_dir, "ops", "notam")
        os.makedirs(notam_dir)
        with open(os.path.join(notam_dir, "2023-10-27-incident.md"), "w") as f:
            f.write("test notam")

        self.assertEqual(check_notam_entries(self.test_dir, "2023-10-27"), "Incidents detected: 2023-10-27-incident.md.")

    def test_calculate_completion_rate(self):
        agents_dir = os.path.join(self.test_dir, "agents")
        os.makedirs(os.path.join(agents_dir, "dexton"))
        with open(os.path.join(agents_dir, "dexton", "log.md"), "w") as f:
            f.write("- [x] task 1\n- [ ] task 2")

        os.makedirs(os.path.join(agents_dir, "kade"))
        with open(os.path.join(agents_dir, "kade", "log.md"), "w") as f:
            f.write("- [x] task 1\n- [x] task 2")

        self.assertEqual(calculate_completion_rate(self.test_dir, self.agents), 75.0)

    def test_check_low_completion_rate(self):
        self.assertEqual(check_completion_rate(49.9), "Low completion.")

    def test_check_high_completion_rate(self):
        self.assertIsNone(check_completion_rate(50.0))

    def test_write_health_report_no_red_flags(self):
        health_path = os.path.join(self.test_dir, "daily.md")
        write_health_report(health_path, "2023-10-27", 85.0, [])
        with open(health_path, "r") as f:
            content = f.read()
        self.assertIn("# health — 2023-10-27", content)
        self.assertIn("- completion_rate: 85.0", content)
        self.assertIn("- no red flags.", content)

    def test_write_health_report_with_red_flags(self):
        health_path = os.path.join(self.test_dir, "daily.md")
        red_flags = ["Version mismatch.", "Missing log: kade."]
        write_health_report(health_path, "2023-10-27", 45.0, red_flags)
        with open(health_path, "r") as f:
            content = f.read()
        self.assertIn("# health — 2023-10-27", content)
        self.assertIn("- completion_rate: 45.0", content)
        self.assertIn("- Version mismatch.", content)
        self.assertIn("- Missing log: kade.", content)

if __name__ == '__main__':
    unittest.main()
