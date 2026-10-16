# Matched molecular pair indexing

## intent

Identify property-relevant molecular replacements. The smallest-transformation
filter re-fragments variable groups using distinguishable attachment masks,
without relaxing RDKit validation of input molecules.

## invariants

- Attachment masking supports normal RDKit sanitization for one through three attachment points
- Single-atom multiple-cut exclusions remain effective after attachment masking
- Attachment masking keeps opposite tetrahedral configurations distinct

## works when

- boundary "Attachment masking supports normal RDKit sanitization for one through three attachment points" at VariableFragmentsReducer via guard "tests/test_smallest_transformation.py::TestSmallestTransformation::test_reducibility_with_one_two_and_three_attachment_points"
- boundary "Single-atom multiple-cut exclusions remain effective after attachment masking" at VariableFragmentsReducer via guard "tests/test_smallest_transformation.py::TestSmallestTransformation::test_single_atom_multiple_cut_guard_is_preserved"
- boundary "Attachment masking keeps opposite tetrahedral configurations distinct" at VariableFragmentsReducer via guard "tests/test_smallest_transformation.py::TestSmallestTransformation::test_attachment_mask_does_not_collapse_enantiomers"

## seams

The CLI consumes fragment databases and writes indexed SQLite databases.
`test_index_removes_redundant_rule_but_retains_smaller_replacement` exercises both
commands with real serialized input and queries the resulting rules and compounds.

## verification boundary

The representative tests use RDKit 2025.9.4. They do not establish that every
chemically reducible transformation is detected under every fragmentation filter.

## why

Original attachment points must stay distinct from new cuts. Mask comparisons use
canonical representations because RDKit can write explicit bracketed carbons next
to the masks; the exclusion must recognize the same structure in that form.
