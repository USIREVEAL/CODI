from unittest import TestCase

from codi.api.utils.compute_statistics import micro_averaged_f_score_labels


class TestStatistics(TestCase):
    def test_micro_averaged_f_score_with_all_same(self):
        gold = [1, 1, 1, 2, 2, 2, 3, 3]
        pred = [1, 1, 1, 2, 2, 2, 3, 3]

        self.assertEqual(micro_averaged_f_score_labels({}, gold, pred), 1)

    def test_micro_averaged_f_score_with_one_swap(self):
        gold = [1, 1, 1, 2, 2, 2, 3, 3]
        pred = [1, 1, 1, 1, 2, 2, 3, 3]

        self.assertAlmostEqual(micro_averaged_f_score_labels({}, gold, pred), 0.8714286, 7)

    def test_micro_averaged_f_score_with_interleaving_message(self):
        gold = [1, 1, 2, 1, 2, 3, 3]
        pred = [1, 1, 1, 1, 1, 2, 2]

        self.assertAlmostEqual(micro_averaged_f_score_labels({}, gold, pred), 0.7704082, 7)

    def test_micro_averaged_f_score_without_disentangling(self):
        gold = [1, 1, 2, 1, 2, 2]
        pred = [1, 1, 1, 2, 2, 2]

        self.assertAlmostEqual(micro_averaged_f_score_labels({}, gold, pred), 0.6666667, 7)
