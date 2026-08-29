# Data Model

## Compound

A compound record may contain:

- Internal compound ID.
- Display name.
- RDKit molecule.
- SMILES.
- Molecular properties.
- Parent ID.
- SAR operation.
- Generation.
- Experimental activity.
- Notes.
- Docking results.

## Experimental activity

Typical fields:

```text
activity_type
activity_value
activity_unit
```

The calculated pActivity is derived from the numerical value and unit.

## Docking result

A docking result should be associated with:

```text
compound
target
configuration
```

and may contain:

```text
score
best_pose
poses[]
poses_file
log_file
```

## Pose

Each pose stores at minimum:

```text
rank
score
```

The multi-pose PDBQT remains the source structure file for the returned poses.

## Project

A project stores:

- Compounds.
- Active/project docking configuration.
- Reusable project configurations.
- PyMOL settings.
- Docking-result metadata.

## Global configuration library

Reusable docking configurations may be stored outside the project so they can be reused across campaigns.

The global library should store configuration metadata such as:

- Configuration name.
- Receptor path.
- Flexible receptor path.
- Box center.
- Box size.
- Exhaustiveness.
- Number of poses.
- Vina executable.
- Open Babel executable.

## Backward compatibility

Older projects may contain single-score docking records. A compatible loader may expose such a result as a one-pose record while preserving the original score.

Do not assume missing historical poses can be reconstructed unless the original Vina multi-pose PDBQT remains available.
