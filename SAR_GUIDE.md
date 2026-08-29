# SAR Generation Guide

## Purpose

AutoSAR Dock is intended to make focused medicinal-chemistry SAR enumeration faster. It is not intended to replace chemical judgment.

Every generated structure should be inspected for:

- Valence.
- Aromaticity.
- Formal charge.
- Stereochemistry.
- Protonation state.
- Tautomeric state.
- Synthetic plausibility.
- Assay relevance.

## Atom numbering

Use the structure viewer's atom labels or Atom Map to identify the desired atom number.

Do not assume an atom number from one SDF will remain valid after a molecule is regenerated or transformed.

## Bond numbering

Use Bond Map or the SAR window's bond-label toggle.

A bond number identifies the RDKit bond index, not necessarily the atom number or a conventional chemical numbering scheme.

## Linker insertion

For:

**Insert into bond**

provide:

- Bond number.
- Linker library.

The operation conceptually replaces the selected bond with a linker between the original attachment atoms.

This is useful for exploring homologous series and spacer effects.

## Link atoms

For:

**Link atoms**

provide:

- Atom A.
- Atom B.
- Linker library.

The exact chemical behavior depends on the implementation of the linker library.

## Atom replacement

For:

**Replace atom**

provide:

- Atom number.
- Replacement library.

A replacement may create second-order chemical consequences. For example, changing an aromatic carbon to nitrogen may require changes to:

- Implicit hydrogen count.
- Bond orders.
- Aromaticity.
- Valence.
- Formal charge.

Products that cannot be sanitized should be rejected rather than forced into an invalid representation.

## Atom deletion

For:

**Delete atom**

provide:

- Atom number.

Deletion can disconnect a structure or create invalid valence. Inspect every resulting derivative.

## Functional-group deletion

For:

**Delete functional group**

provide:

- The attachment bond number.
- The atom to retain on the core side.

The implementation removes the fragment on the opposite side of the selected attachment.

## Library design

Focused libraries are generally more interpretable than very large indiscriminate enumerations.

Useful focused series include:

- Linker homologation.
- Heteroatom scans.
- Halogen scans.
- Small substituent scans.
- Ring replacements.
- Functional-group truncations.

## Docking after SAR generation

Do not interpret a more favorable docking score as sufficient evidence that the derivative is more potent.

A useful prioritization may combine:

- Docking score.
- Pose plausibility.
- Structural novelty.
- Molecular properties.
- Experimental SAR.
- Synthetic accessibility.
