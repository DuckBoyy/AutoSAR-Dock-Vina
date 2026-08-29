# AutoSAR Dock User Guide

## 1. Start a project

Launch:

```bash
python run_app.py
```

Create a new project directory from the application.

The project should contain persistent project metadata plus directories for compounds and docking outputs.

## 2. Import a molecule

Use:

**Molecule → Import Molecule**

Supported formats depend on the chemistry module, but commonly include:

- SDF
- MOL
- MOL2
- SMILES

The imported compound is assigned an internal compound ID. The displayed compound name can be different from that internal ID.

## 3. View the structure

Use:

**Molecule → View Structure**

The structure viewer can display:

- Atom numbers.
- Bond numbers.
- Both.
- No labels.

Use **Atom Map** or **Bond Map** when selecting an exact atom or bond numerically is easier than clicking the drawing.

## 4. Generate SAR

Use:

**Molecule → Generate SAR**

The SAR window is intended to provide explicit numeric inputs for operations where clicking a bond or atom is difficult.

Before generating derivatives, inspect the structure and make sure the numbering corresponds to the intended chemical position.

## 5. Review generated compounds

Generated derivatives are added to the main table and retain parent/generation/SAR metadata when supported by the project model.

A generated derivative should be chemically inspected before docking.

## 6. Add experimental activity

Select a compound and choose:

**Molecule → Experimental Data**

Enter:

- Measurement type.
- Numerical value.
- Units.
- Notes.

The application calculates a negative-log activity value from the numerical activity and units.

## 7. Docking configurations

Use:

**Docking → Configure Docking**

A configuration can specify:

- Receptor.
- Flexible receptor file when applicable.
- Grid center X/Y/Z.
- Grid size X/Y/Z.
- Exhaustiveness.
- Number of poses.
- Vina executable.
- Open Babel executable.

Configurations can be saved at the project level and, where supported, into a global reusable configuration library.

## 8. Docking campaigns

Use:

**Docking → Run Docking Campaign**

Select one or more docking configurations.

The intended behavior is independent tracking of:

```text
Compound A × Target 1
Compound A × Target 2
Compound B × Target 1
Compound B × Target 2
```

Therefore a compound docked to one receptor should not be treated as automatically docked to every receptor.

## 9. Pose scores

When the docking engine stores multiple Vina poses, the project retains the individual pose ranks and scores.

Use:

**Docking → Pose Scores**

to see the individual poses.

Double-click an individual pose to inspect it in PyMOL.

The best pose is the pose with the lowest stored Vina score and remains the default docking score used in the main table.

## 10. View a docked pose

Select a compound and use:

**Docking → View Docked Pose**

or inspect a pose through the Pose Scores window.

For a multi-target project, first select the desired target.

The viewer should load:

- The rigid receptor.
- The optional flexible-receptor component.
- The selected ligand pose.

## 11. Export data

Use:

**Project → Export CSV**

or:

**Project → Export Excel**

CSV is suitable for analysis in external software.

Excel export is useful for retaining separate sheets for compound and docking information when supported by the version of the application.

## 12. Analysis

Use:

**Docking → Analyze Data**

Available variables depend on the installed analysis module.

Typical comparisons include:

- Docking score vs pActivity.
- Molecular weight vs pActivity.
- LogP vs pActivity.
- TPSA vs pActivity.
- Docking score vs molecular descriptors.

Treat correlation as exploratory analysis. A correlation between docking and activity does not establish causality.

## 13. Recommended SAR workflow

A practical cycle is:

```text
Parent
  ↓
Generate focused derivatives
  ↓
Inspect structures
  ↓
Dock
  ↓
Inspect poses
  ↓
Prioritize compounds
  ↓
Add experimental data
  ↓
Analyze SAR
  ↓
Generate next derivative set
```

Keep the parent compound and derivatives in the same project when possible so the SAR history remains connected.
