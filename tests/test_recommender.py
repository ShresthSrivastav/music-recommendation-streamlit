import unittest

from src.recommender import exact_report_example, hybrid_score, recommend


class RecommenderTests(unittest.TestCase):
    def test_report_example_order_and_scores(self):
        rows = exact_report_example()
        self.assertEqual([row["title"] for row in rows], [
            "Track B: indie folk",
            "Track A: acoustic pop",
            "Track C: electronic dance",
        ])
        self.assertEqual([round(float(row["hybrid_score"]), 2) for row in rows], [0.81, 0.72, 0.54])

    def test_weight_changes_the_winner(self):
        content_first = recommend(content_weight=1.0, limit=1)
        collaborative_first = recommend(content_weight=0.0, limit=1)
        self.assertEqual(content_first[0]["title"], "Track A: acoustic pop")
        self.assertEqual(collaborative_first[0]["title"], "Neon Steps")

    def test_invalid_inputs_fail_loudly(self):
        with self.assertRaises(ValueError):
            hybrid_score(exact_report_example()[0], 1.1)
        with self.assertRaises(ValueError):
            recommend(limit=0)


if __name__ == "__main__":
    unittest.main()
