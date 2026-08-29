# Troubleshooting

## `ImportError: cannot import name 'DockingEngine'`

Confirm that:

```python
class DockingEngine:
```

exists in `autosar_dock/docking.py`.

Test:

```bash
python -c "from autosar_dock.docking import DockingEngine; print('OK')"
```

## `ImportError: cannot import name 'GlobalDockingConfigLibrary'`

Confirm that the class exists in `autosar_dock/project.py`.

Test:

```bash
python -c "from autosar_dock.project import Project, GlobalDockingConfigLibrary; print('OK')"
```

## `IndentationError`

Compile modules before launching the application:

```bash
python -m py_compile autosar_dock/project.py
python -m py_compile autosar_dock/docking.py
python -m py_compile autosar_dock/app.py
```

## Vina says `unrecognized option '--log'`

The application should not pass:

```text
--log
```

to Vina.

Instead, capture Vina's stdout/stderr from Python and write those streams to the per-docking log file.

## Docking score does not populate

The returned score should be converted to a Python float before entering the project table.

Test:

```python
float(score)
```

The stored project score should be numeric.

## Multiple targets appear as one docking state

Check that the project records docking status by:

```text
compound + target
```

rather than by compound alone.

## Pose scores are missing

New docking runs need to store the list of returned Vina poses. Older projects that stored only one score cannot recover the missing scores unless their original Vina pose file is still available.

## PyMOL not found

Run:

```bash
conda activate autosardock
which pymol
```

If nothing is returned:

```bash
conda install -c conda-forge pymol-open-source
```

Then test:

```bash
pymol
```

before using the AutoSAR Dock pose viewer.

## PyMOL starts but crashes with a missing `.so`

Run:

```bash
ldd "$(python -c 'import pymol._cmd; print(pymol._cmd.__file__)')" | grep "not found"
```

Do not manually symlink libraries until you understand the exact ABI/package mismatch.

A clean conda-forge environment is usually safer than mixing incompatible binary packages.

## PyMOL opens but cannot see a WSL file

Use the native Linux PyMOL executable:

```bash
which pymol
```

rather than launching the Windows executable.

## Excel export fails

Check:

```bash
python -c "import pandas, openpyxl; print('Excel dependencies OK')"
```

Install as necessary:

```bash
pip install pandas openpyxl
```

## Analysis window fails

Check:

```bash
python -c "import matplotlib; print(matplotlib.__version__)"
```

Install:

```bash
pip install matplotlib
```

## SDF structure is visually scrambled

Check that the imported structure has usable 2D/3D coordinates.

If the application chemistry module supports coordinate generation or regeneration, use that process before drawing or exporting.

Do not change chemical connectivity merely to improve the 2D layout.
