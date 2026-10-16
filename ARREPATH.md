# ArrePath integration branch

This branch is mmpdb **3.1.4+arrepath.1**, based on upstream tag `v3.1.4`.
It keeps the upstream license and attribution unchanged.

## Changes

- Cherry-pick [rdkit/mmpdb#82](https://github.com/rdkit/mmpdb/pull/82),
  commit `b8fc64f597dbfaea959e65a12242ed5d361b4669`: replace neutral noble-gas
  attachment masks with Rf/Db/Sg so normal RDKit valence validation accepts them.
- Canonicalize the existing single-atom/multiple-cut exclusion patterns. RDKit
  writes bracketed carbons next to the replacement masks; literal comparison
  would otherwise bypass the safeguards intended to avoid losing stereochemistry.
- Correct the malformed Click requirement in the upstream release tag's
  `pyproject.toml` so immutable source archives can be built.
- Add behavioral regressions for actual indexing, reducibility with one through
  three attachment points, the exclusion safeguards, and distinct enantiomers.

## Validation

The supported Ariadne integration uses RDKit `2025.9.4`. Run:

```sh
python -m unittest discover -s tests -p test_smallest_transformation.py
python -m unittest discover -s tests -p test_index.py
```

Ariadne consumes a full-commit archive URL, not this moving branch name.
Return to an upstream release only after it passes the same regressions and
Ariadne's real `build_mmpdb` subprocess test. This patch does not resolve all
pre-existing limitations of `--smallest-transformation-only`, including upstream
issues [#20](https://github.com/rdkit/mmpdb/issues/20),
[#22](https://github.com/rdkit/mmpdb/issues/22), and
[#23](https://github.com/rdkit/mmpdb/issues/23).
