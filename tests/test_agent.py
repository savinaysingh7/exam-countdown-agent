import unittest

from agent import ExamAgent


class ExamAgentToolTests(unittest.TestCase):
    def setUp(self):
        self.agent = ExamAgent()

    def test_set_exam_records_remaining_days(self):
        result = self.agent._set_exam("2026-09-10")

        self.assertEqual(
            result,
            "Exam set to 2026-09-10. There are 19 days remaining.",
        )
        self.assertEqual(self.agent.state["exam_date"], "2026-09-10")
        self.assertEqual(self.agent.state["days_left"], 19)

    def test_set_exam_rejects_the_demo_date(self):
        result = self.agent._set_exam("2026-08-22")

        self.assertTrue(result.startswith("Error:"))
        self.assertIsNone(self.agent.state["exam_date"])

    def test_allocate_topics_retains_existing_topics(self):
        self.agent._set_exam("2026-09-10")
        self.agent._allocate_topics(["OS", "DBMS"])
        plan = self.agent._allocate_topics(["Computer Networks"])

        self.assertEqual(
            self.agent.state["topics"],
            ["OS", "DBMS", "Computer Networks"],
        )
        self.assertIn("Computer Networks", plan)

    def test_allocate_topics_requires_an_exam_date(self):
        result = self.agent._allocate_topics(["OS"])

        self.assertEqual(
            result,
            "Error: No exam date set. Please call set_exam first.",
        )


if __name__ == "__main__":
    unittest.main()
