# PyMOL on WSL2

## Recommended architecture

If AutoSAR Dock and PyMOL are both installed in the same Linux/conda environment, the cleanest workflow is:

```text
WSL2
└── conda environment
    ├── AutoSAR Dock
    └── PyMOL Open Source
```

Then:

```bash
which pymol
```

should return a path inside the active environment.

For example:

```text
/home/user/anaconda3/envs/autosardock/bin/pymol
```

## Why this is preferable

When PyMOL runs natively inside WSL2:

- WSL paths can be passed directly to PyMOL.
- No Windows path conversion is required.
- `cmd.exe` is not required to launch PyMOL.
- Receptor and pose files can remain in the Linux project tree.

## Verify PyMOL

Activate the same environment used for AutoSAR Dock:

```bash
conda activate autosardock
```

Then:

```bash
which pymol
```

and:

```bash
pymol
```

PyMOL must work independently before the AutoSAR Dock pose viewer can work reliably.

## Automatic detection

AutoSAR Dock should prefer:

```python
shutil.which("pymol")
```

or:

```text
$CONDA_PREFIX/bin/pymol
```

over a hard-coded Windows executable path.

## WSL graphics

PyMOL is a graphical application. Modern WSL2 installations with WSLg can display Linux GUI applications through the Windows desktop.

Check:

```bash
echo $DISPLAY
echo $WAYLAND_DISPLAY
```

If PyMOL reports display/OpenGL problems, test the graphical environment independently from AutoSAR Dock.

## Conda-forge installation

The conda-forge PyMOL Open Source feedstock documents:

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install pymol-open-source
```

Source:
https://github.com/conda-forge/pymol-open-source-feedstock

## Source installation

The official PyMOL Open Source repository documents source compilation:

https://github.com/schrodinger/pymol-open-source/blob/master/INSTALL

The repository currently lists C++17, CMake, Python 3.9+, OpenGL/GLEW, and other development dependencies for source builds.

## Common dependency problem

An error such as:

```text
ImportError: libSomething.so: cannot open shared object file
```

usually indicates a binary dependency problem in the PyMOL environment, not an AutoSAR Dock problem.

Avoid solving such problems by renaming shared libraries or creating arbitrary symlinks between incompatible versions.

Prefer a consistent conda package stack or a clean source build.
