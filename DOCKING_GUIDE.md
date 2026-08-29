# Docking Guide

## Receptor preparation

AutoDock Vina normally operates on prepared PDBQT inputs. A raw PDB is not equivalent to a prepared Vina receptor.

A typical receptor workflow is:

```text
PDB
 ↓
Inspect biological assembly
 ↓
Choose chain/residue state
 ↓
Resolve unwanted waters/ligands as appropriate
 ↓
Assign protonation/charges
 ↓
Generate receptor PDBQT
 ↓
Define docking box
 ↓
Validate configuration
```

The exact preparation pipeline is outside the scope of AutoSAR Dock.

## Flexible receptor docking

AutoDock Vina supports a flexible receptor argument using a rigid receptor plus a separate flexible-residue PDBQT component.

Configure:

- Rigid receptor PDBQT.
- Flexible receptor PDBQT.
- Flexible docking enabled.

The current application should pass the flexible component to Vina only when the flexible-docking option is enabled.

## Grid definition

A docking configuration contains:

- Center X.
- Center Y.
- Center Z.
- Size X.
- Size Y.
- Size Z.

Document the biological rationale for the selected box.

## Exhaustiveness

Exhaustiveness controls search effort. It is not a measure of affinity.

Higher values can increase runtime.

## Number of poses

AutoSAR Dock is intended to retain multiple returned Vina poses.

For a five-pose campaign, retain:

```text
Pose 1
Pose 2
Pose 3
Pose 4
Pose 5
```

and their individual scores.

## Main-table docking score

The main docking score represents the best stored Vina score for that compound/target result.

In a standard Vina ranking, a numerically lower/more negative score is the better-scoring pose.

## Pose inspection

Always inspect poses that are intended to influence chemistry decisions.

Questions to consider:

- Is the ligand orientation chemically reasonable?
- Are key contacts geometrically plausible?
- Are there severe steric clashes?
- Is the ligand buried/exposed as expected?
- Does the pose agree with known SAR?
- Does the pose depend on questionable receptor geometry?

## Multiple targets

A single compound can be docked to multiple receptors/configurations.

Treat each combination as its own result:

```text
compound × target × configuration
```

This prevents the common mistake of interpreting "docked somewhere" as "docked everywhere."

## Output naming

Recommended output structure:

```text
docking_results/
├── target_A/
│   ├── compound_A__target_A_poses.pdbqt
│   ├── compound_A__target_A_vina.log
│   └── ...
└── target_B/
    ├── compound_A__target_B_poses.pdbqt
    ├── compound_A__target_B_vina.log
    └── ...
```

This makes downstream PyMOL inspection substantially easier.
