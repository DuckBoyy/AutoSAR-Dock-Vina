# AutoSAR Dock Installation Guide

This guide assumes AutoSAR Dock is being run in Ubuntu under WSL2 on Windows.

## 1. Prerequisites

Recommended:

- Windows 10/11
- WSL2
- Ubuntu or another supported Linux distribution
- conda or mamba
- Git
- A working X/Wayland/WSLg environment if you want graphical PyMOL

Confirm WSL:

```bash
uname -a
```

## 2. Create the conda environment

Example:

```bash
conda create -n autosardock python=3.11
conda activate autosardock
```

You may substitute an existing environment if it is already dedicated to the AutoSAR Dock workflow.

## 3. Install Python dependencies

At minimum:

```bash
pip install pandas openpyxl matplotlib pillow
```

Install RDKit using your preferred supported method. For conda environments, a conda/mamba package is generally preferable to compiling RDKit manually.

If your application has a `requirements.txt`, install it with:

```bash
pip install -r requirements.txt
```

## 4. Open Babel

Verify:

```bash
which obabel
obabel -V
```

If Open Babel is not available, install it using a package manager appropriate to your environment, for example conda-forge:

```bash
conda install -c conda-forge openbabel
```

## 5. AutoDock Vina

Verify:

```bash
which vina
vina --help
```

Install Vina using your preferred supported distribution method. Keep the installed Vina version documented because command-line behavior can vary between releases.

AutoSAR Dock intentionally captures Vina stdout/stderr rather than relying on the Vina `--log` option. This avoids compatibility problems with Vina builds that do not accept `--log`.

## 6. PyMOL Open Source

For WSL, the recommended route is the community Open Source PyMOL package from conda-forge when available:

```bash
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
conda install pymol-open-source
```

Then:

```bash
which pymol
pymol
```

The conda-forge feedstock documents installation with `pymol-open-source` and strict channel priority:
https://github.com/conda-forge/pymol-open-source-feedstock

The official PyMOL Open Source repository also documents source compilation and lists its build requirements:
https://github.com/schrodinger/pymol-open-source

## 7. Clone AutoSAR Dock

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd AutoSAR_Dock
```

## 8. First launch

Activate the environment:

```bash
conda activate autosardock
```

Then:

```bash
python run_app.py
```

## 9. Verify the tools before docking

Run:

```bash
which python
which obabel
which vina
which pymol
```

It is useful for all four tools to resolve consistently inside the intended environment.

For example:

```text
/home/you/anaconda3/envs/autosardock/bin/python
/home/you/anaconda3/envs/autosardock/bin/obabel
/home/you/anaconda3/envs/autosardock/bin/vina
/home/you/anaconda3/envs/autosardock/bin/pymol
```

## 10. Recommended reproducibility step

Record:

```bash
conda list
```

and:

```bash
python --version
```

For a publication or internal project, keep the environment specification used for the campaign. An `environment.yml` file is preferable when the environment is intended to be reproduced by collaborators.

## 11. PyMOL source-build alternative

If you specifically need to build PyMOL from the official GitHub source, see:

https://github.com/schrodinger/pymol-open-source/blob/master/INSTALL

The official instructions list requirements including a C++17 compiler, CMake, Python 3.9+, OpenGL/GLEW, libpng, freetype, and optional components. They recommend:

```bash
pip install .
```

from the PyMOL source tree.

For AutoSAR Dock, source-built PyMOL should still be placed on the active environment's PATH so that:

```bash
which pymol
```

returns the executable AutoSAR Dock should use.
