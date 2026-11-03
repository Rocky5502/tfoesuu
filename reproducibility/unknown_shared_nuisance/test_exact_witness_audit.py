import math
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from exact_witness_audit import (
    run,
    shifted_null,
    transcript_kl,
    transcript_law,
    witness_probability,
)


class ExactWitnessAuditTests(unittest.TestCase):
    def test_complete_laws_and_support(self):
        p, h, d = F(1, 4), F(1, 2), F(1, 100)
        null = transcript_law(p, h, p, h)
        alt = transcript_law(p, h + d, p, h)
        self.assertEqual(
            null,
            {
                (1, 1, 1, 1): p,
                (0, 1, 0, 1): h - p,
                (0, 0, 0, 0): 1 - h,
            },
        )
        self.assertEqual(witness_probability(null), 0)
        self.assertEqual(witness_probability(alt), d)
        self.assertTrue(math.isinf(transcript_kl(alt, null)))

    def test_shifted_support_counterexample(self):
        eta = F(1, 200)
        self.assertEqual(
            witness_probability(shifted_null(F(1, 5), F(1, 5), eta)),
            2 * eta,
        )
        with self.assertRaisesRegex(ValueError, "require 0 < p"):
            shifted_null(F(-1, 20), F(1, 10), F(1, 50))

    def test_full_audit(self):
        result = run()
        self.assertEqual(result["exact_shared_nuisance_cases"], 24)
        self.assertEqual(result["counterexample_horizon"], 299)
        self.assertAlmostEqual(
            result["counterexample_false_reject"], 0.9504637433623376
        )


if __name__ == "__main__":
    unittest.main()
