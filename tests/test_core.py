import unittest

from time_zone_precedence import (
    ZoneCandidate,
    select,
    specificity,
)


class TestSpecificity(unittest.TestCase):
    def test_bare_identifier_scores_one(self):
        self.assertEqual(specificity("UTC"), 1)
        self.assertEqual(specificity("GMT"), 1)

    def test_two_segments_score_two(self):
        self.assertEqual(specificity("America/Chicago"), 2)
        self.assertEqual(specificity("Europe/London"), 2)

    def test_three_segments_score_three(self):
        self.assertEqual(
            specificity("America/North_Dakota/New_Salem"), 3
        )
        self.assertEqual(
            specificity("America/Indiana/Knox"), 3
        )

    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            specificity("")

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            specificity(None)
        with self.assertRaises(TypeError):
            specificity(123)
        with self.assertRaises(TypeError):
            specificity(["America", "Chicago"])

    def test_leading_slash_rejected(self):
        with self.assertRaises(ValueError):
            specificity("/America/Chicago")

    def test_trailing_slash_rejected(self):
        with self.assertRaises(ValueError):
            specificity("America/Chicago/")

    def test_double_slash_rejected(self):
        with self.assertRaises(ValueError):
            specificity("America//Chicago")

    def test_only_slashes_rejected(self):
        with self.assertRaises(ValueError):
            specificity("///")


class TestSelect(unittest.TestCase):
    def test_returns_most_specific(self):
        result = select([
            ZoneCandidate("America/Chicago"),
            ZoneCandidate("America/North_Dakota/New_Salem"),
        ])
        self.assertEqual(result.zone_id, "America/North_Dakota/New_Salem")

    def test_two_segment_vs_two_segment_returns_first(self):
        result = select([
            ZoneCandidate("America/New_York"),
            ZoneCandidate("America/Chicago"),
        ])
        self.assertEqual(result.zone_id, "America/New_York")

    def test_first_wins_on_tie(self):
        result = select([
            ZoneCandidate("Europe/London"),
            ZoneCandidate("Europe/Paris"),
            ZoneCandidate("America/North_Dakota/New_Salem"),
            ZoneCandidate("America/Indiana/Vincennes"),
        ])
        self.assertEqual(result.zone_id, "America/North_Dakota/New_Salem")

    def test_single_candidate(self):
        only = ZoneCandidate("America/Chicago")
        self.assertIs(select([only]), only)

    def test_empty_iterable_raises_value_error(self):
        with self.assertRaises(ValueError):
            select([])

    def test_non_iterable_raises_type_error(self):
        with self.assertRaises(TypeError):
            select(42)

    def test_non_zone_candidate_raises_type_error(self):
        with self.assertRaises(TypeError):
            select(["America/Chicago"])

    def test_returns_zone_candidate_instance(self):
        result = select([ZoneCandidate("UTC")])
        self.assertIsInstance(result, ZoneCandidate)

    def test_bare_identifier_beaten_by_slashed(self):
        result = select([
            ZoneCandidate("UTC"),
            ZoneCandidate("America/Chicago"),
        ])
        self.assertEqual(result.zone_id, "America/Chicago")

    def test_bare_identifier_wins_alone(self):
        result = select([ZoneCandidate("UTC")])
        self.assertEqual(result.zone_id, "UTC")

    def test_generator_input(self):
        def gen():
            yield ZoneCandidate("America/Chicago")
            yield ZoneCandidate("America/North_Dakota/New_Salem")
        result = select(gen())
        self.assertEqual(result.zone_id, "America/North_Dakota/New_Salem")

    def test_candidate_with_invalid_zone_id_propagates(self):
        with self.assertRaises(ValueError):
            select([ZoneCandidate("")])


if __name__ == "__main__":
    unittest.main()
