import unittest

from services.ioc_extractor import extract_iocs


class IOCExtractorTests(unittest.TestCase):
    def test_deduplicates_and_counts_occurrences(self):
        rows = extract_iocs(
            [
                "blocked malicious connection from 8.8.8.8",
                "repeat source 8.8.8.8",
                "another event from 8.8.8.8",
            ],
            "firewall.log",
        )

        ip = next(item for item in rows if item["value"] == "8.8.8.8")
        self.assertEqual(ip["occurrence_count"], 3)
        self.assertGreaterEqual(ip["risk_score"], 60)
        self.assertEqual(ip["severity"], "High")

    def test_private_ip_is_lower_priority(self):
        rows = extract_iocs(
            ["healthcheck allowed from 10.0.0.1"],
            "internal.log",
        )

        ip = next(item for item in rows if item["ioc_type"] == "IPv4")
        self.assertEqual(ip["scope"], "private")
        self.assertLess(ip["risk_score"], 20)

    def test_domain_inside_email_is_not_double_counted(self):
        rows = extract_iocs(
            ["contact admin@example.com for investigation"],
            "mail.log",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ioc_type"], "Email")
        self.assertEqual(rows[0]["value"], "admin@example.com")

    def test_domain_and_ip_inside_url_are_not_double_counted(self):
        rows = extract_iocs(
            ["request blocked to https://Example.COM/CaseSensitivePath"],
            "proxy.log",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ioc_type"], "URL")
        self.assertEqual(
            rows[0]["value"],
            "https://example.com/CaseSensitivePath",
        )

    def test_placeholder_hash_is_filtered(self):
        rows = extract_iocs(
            ["hash=00000000000000000000000000000000"],
            "edr.log",
        )
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
