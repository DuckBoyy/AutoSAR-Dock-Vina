# AutoSAR Dock

AutoSAR Dock is a local desktop workbench for iterative small-molecule SAR design and structure-based docking. It combines RDKit-based structure handling, rule/library-driven SAR transformations, AutoDock Vina docking, experimental activity tracking, project persistence, data export, exploratory analysis, and optional PyMOL pose inspection.

> **Project status:** Active prototype / research tool. Validate all generated chemistry and docking results independently before using them for scientific or decision-making purposes.

## What AutoSAR Dock is designed to do

AutoSAR Dock is intended for an iterative medicinal-chemistry workflow:

1. Import a starting structure from SDF or another supported structure format.
2. Inspect the molecule and atom/bond numbering.
3. Generate SAR derivatives using supported transformations.
4. Review calculated molecular properties.
5. Configure one or more docking targets.
6. Dock compounds against multiple receptor configurations.
7. Retain the docking score and the individual Vina pose scores.
8. Enter experimental IC50/Ki/Kd/EC50 data.
9. Compare experimental activity with molecular properties and docking results.
10. Open selected docked poses in PyMOL.
11. Export the project dataset to CSV or Excel.

## Current SAR capabilities

The application is intended to support:

- Linker generation.
- Insertion of linkers into selected bonds.
- Atom replacement.
- Atom deletion.
- Functional-group deletion.
- Atom and bond mapping for selecting structural positions.
- Numeric atom/bond entry when graphical bond selection is inconvenient.

The chemistry layer should be treated as a library of transformations rather than a general-purpose retrosynthesis or structure-generation engine.

## Docking capabilities

AutoSAR Dock is designed around AutoDock Vina and supports:

- Rigid receptor docking.
- Flexible receptor docking using Vina's flexible receptor mechanism.
- Reusable docking configurations.
- Multiple receptor targets in one campaign.
- Compound-specific pose filenames.
- Capture of Vina output into per-docking log files.
- Retention of multiple docking poses.
- Pose-score inspection and pose selection.
- Optional external PyMOL viewing.

The receptor used by Vina should normally be a prepared PDBQT file. The application can browse for PDB files for convenience, but a raw PDB generally needs to be prepared before Vina docking.

## Experimental SAR data

Experimental data can be associated with individual compounds. The intended fields include:

- Measurement type: IC50, EC50, Ki, Kd, or Other.
- Numerical activity value.
- Units.
- Automatically calculated pActivity/pIC-style value.
- Free-text notes.

Do not combine values from incompatible assays without documenting the assay context.

## PyMOL

AutoSAR Dock can launch PyMOL for pose inspection. For WSL installations, the preferred setup is to install PyMOL in the same Linux/conda environment as AutoSAR Dock and let the application find the executable from the active environment.

See:

- `docs/INSTALL.md`
- `docs/PYMOL_WSL.md`
- `docs/DOCKING_GUIDE.md`

## Installation

The recommended environment is Linux or WSL2 with conda or mamba.

See `docs/INSTALL.md` for the full setup sequence.

A typical environment contains:

- Python 3.11
- RDKit
- Open Babel
- AutoDock Vina
- pandas
- openpyxl
- matplotlib
- Pillow
- PyMOL Open Source (optional)

## Quick start

```bash
conda activate autosardock
cd /path/to/AutoSAR_Dock
python run_app.py
```

Before using docking, verify that the command-line tools are visible:

```bash
which obabel
which vina
which pymol
```

Then test them independently:

```bash
obabel -V
vina --help
pymol
```

## Project organization

A typical repository is organized as:

```text
AutoSAR_Dock/
├── run_app.py
├── autosar_dock/
│   ├── __init__.py
│   ├── app.py
│   ├── chemistry.py
│   ├── docking.py
│   ├── project.py
│   ├── sar.py
│   ├── analysis.py
│   └── pose_viewer.py
├── docs/
│   ├── INSTALL.md
│   ├── USER_GUIDE.md
│   ├── SAR_GUIDE.md
│   ├── DOCKING_GUIDE.md
│   ├── PYMOL_WSL.md
│   ├── DATA_MODEL.md
│   └── TROUBLESHOOTING.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE/
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
└── requirements.txt
```

Some repositories may contain additional modules or files. The actual source tree is the authoritative definition.

## Scientific scope and limitations

Docking scores are computational estimates, not experimental affinity measurements. A more negative Vina score should not be interpreted automatically as a more potent compound. Docking poses require structural inspection and, where appropriate, orthogonal validation.

Likewise, automatically generated SAR structures may contain undesirable chemistry, stereochemical assumptions, valence problems, strained structures, or changes in protonation state. Every derivative should be chemically inspected before synthesis or downstream use.

## Citation and attribution

AutoSAR Dock uses several external projects, including RDKit, Open Babel, AutoDock Vina, and optionally PyMOL Open Source. See the repository's citation documentation and dependency documentation before publishing results.

GitHub recommends that repositories include a README, license, citation information, contribution guidelines, and a code of conduct where appropriate:
https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories

## License

A project license has deliberately not been selected in this documentation package because the appropriate license depends on ownership and the provenance of the code and dependencies.

Before making the repository public, add a license that you are authorized to use. See `LICENSE-TEMPLATE.md` for guidance.
