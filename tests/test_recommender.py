import unittest

from src.recommender import (
    evaluate_dataset,
    exact_report_example,
    hybrid_score,
    load_dataset,
    recommend,
    recommend_for_user,
)


class RecommenderTests(unittest.TestCase):
    def test_report_example_order_and_scores(self):
        rows = exact_report_example()
        self.assertEqual([row["title"] for row in rows], [
            "Track B: indie folk",
            "Track A: acoustic pop",
            "Track C: electronic dance",
        ])
        self.assertEqual([round(float(row["hybrid_score"]), 2) for row in rows], [0.81, 0.72, 0.54])

    def test_weight_changes_report_example(self):
        content_first = recommend(content_weight=1.0, limit=1)
        collaborative_first = recommend(content_weight=0.0, limit=1)
        self.assertEqual(content_first[0]["title"], "Track A: acoustic pop")
        self.assertEqual(collaborative_first[0]["title"], "Track B: indie folk")

    def test_dataset_user_gets_unseen_recommendations(self):
        tracks, users, interactions = load_dataset()
        user_id = users.iloc[0]["user_id"]
        rows = recommend_for_user(user_id, tracks, interactions, limit=5)
        listened = set(interactions.loc[interactions["user_id"] == user_id, "track_id"])
        self.assertTrue(rows)
        self.assertTrue(all(row["track_id"] not in listened for row in rows))
        self.assertTrue(all(0 <= float(row["hybrid_score"]) <= 1 for row in rows))

    def test_evaluation_returns_expected_metrics(self):
        tracks, users, interactions = load_dataset()
        metrics, detail = evaluate_dataset(users["user_id"], tracks, interactions, k=5)
        self.assertEqual(len(detail), len(users))
        self.assertTrue({"precision@k", "recall@k", "ndcg@k", "coverage", "diversity"}.issubset(metrics))

    def test_invalid_inputs_fail_loudly(self):
        with self.assertRaises(ValueError):
            hybrid_score(exact_report_example()[0], 1.1)
        with self.assertRaises(ValueError):
            recommend(limit=0)


if __name__ == "__main__":
    unittest.main()
