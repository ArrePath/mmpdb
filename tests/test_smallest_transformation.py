"""Regressions for attachment masks used by --smallest-transformation-only."""

import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

from mmpdblib import config, index_algorithm
from support import create_test_filename, expect_pass


class TestSmallestTransformation(unittest.TestCase):
    def setUp(self):
        self.reducer = index_algorithm.VariableFragmentsReducer(config.DEFAULT_FRAGMENT_OPTIONS.get_fragment_filter())

    def test_reducibility_with_one_two_and_three_attachment_points(self):
        cases = [
            ("[*:1]c1ccccc1O>>[*:1]c1ccccc1N", True),
            ("[*:1]F>>[*:1]Cl", False),
            ("[*:1]C([*:2])CO>>[*:1]C([*:2])CN", True),
            ("[*:1]C([*:2])([*:3])CO>>[*:1]C([*:2])([*:3])CN", True),
        ]
        for smirks, expected in cases:
            with self.subTest(smirks=smirks):
                self.assertEqual(self.reducer.transformation_is_reducible(smirks), expected)

    def test_single_atom_multiple_cut_guard_is_preserved(self):
        # These intentionally remain indexed: shrinking them can lose stereo
        # at the atom carrying the original attachment points.
        for smirks in [
            "[*:1]C([*:2])F>>[*:1]C([*:2])Cl",
            "[*:1]C([*:2])([*:3])F>>[*:1]C([*:2])([*:3])Cl",
        ]:
            with self.subTest(smirks=smirks):
                self.assertFalse(self.reducer.transformation_is_reducible(smirks))

    def test_attachment_mask_does_not_collapse_enantiomers(self):
        left = self.reducer.get_or_compute_variable_fragments("[*:1][C@](F)(Cl)Br")
        right = self.reducer.get_or_compute_variable_fragments("[*:1][C@@](F)(Cl)Br")
        self.assertNotEqual(left["frag_canon"], right["frag_canon"])

    def test_index_removes_redundant_rule_but_retains_smaller_replacement(self):
        smiles = Path(create_test_filename(self, "series.smi"))
        smiles.write_text("CCOc1ccccc1 A\nCCNc1ccccc1 B\nCCCOc1ccccc1 C\nCCSc1ccccc1 D\n")
        fragments = smiles.with_suffix(".fragdb")
        expect_pass(("--quiet", "fragment", "--num-jobs", "1", str(smiles), "-o", str(fragments)))
        rules = {}
        for name, flags in [("default", ()), ("smallest", ("--smallest-transformation-only",))]:
            database = smiles.with_name(name + ".mmpdb")
            expect_pass(
                (
                    "--quiet",
                    "index",
                    str(fragments),
                    "-o",
                    str(database),
                    "--max-variable-heavies",
                    "16",
                    "--max-variable-ratio",
                    "0.5",
                )
                + flags
            )
            with closing(sqlite3.connect(database)) as connection:
                compounds = {row[0] for row in connection.execute("SELECT public_id FROM compound")}
                self.assertEqual(compounds, {"A", "B", "C", "D"})
                rules[name] = set(
                    connection.execute(
                        "SELECT a.smiles, b.smiles FROM rule r "
                        "JOIN rule_smiles a ON a.id = r.from_smiles_id "
                        "JOIN rule_smiles b ON b.id = r.to_smiles_id"
                    )
                )
        redundant = ("[*:1]OCC", "[*:1]OCCC")
        self.assertIn(redundant, rules["default"])
        self.assertNotIn(redundant, rules["smallest"])
        self.assertIn(("[*:1]CC", "[*:1]CCC"), rules["smallest"])
        self.assertLess(rules["smallest"], rules["default"])


if __name__ == "__main__":
    unittest.main()
