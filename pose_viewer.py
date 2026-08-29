import os
import platform
import shutil
import subprocess

from pathlib import Path


def is_wsl():
    """
    Detect WSL.
    """

    try:

        release = (
            platform.uname()
            .release
            .lower()
        )

        version = (
            platform.uname()
            .version
            .lower()
        )

        return (
            "microsoft" in release
            or "microsoft" in version
            or "wsl" in release
        )

    except Exception:

        return False


def wsl_to_windows_path(path):
    """
    Convert a WSL/Linux path to a Windows path.
    """

    path = Path(path)

    result = subprocess.run(
        [

            "wslpath",

            "-w",

            str(path),

        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Could not convert WSL path to Windows path:\n"
            f"{path}\n\n"
            f"{result.stderr}"
        )

    return result.stdout.strip()


def create_pymol_script(
    receptor_file,
    pose_file,
    script_file,
    flexible_receptor=None,
):
    """
    Create a PyMOL PML script.

    The script loads:

        rigid receptor
        optional flexible receptor
        docked ligand

    and sets a useful initial view.
    """

    receptor_file = str(
        receptor_file
    )

    pose_file = str(
        pose_file
    )

    flexible_receptor = (
        str(flexible_receptor)
        if flexible_receptor
        else None
    )

    script_file = Path(
        script_file
    )

    lines = [

        "reinitialize",

        f'load "{receptor_file}", receptor',

    ]

    if flexible_receptor:

        lines.extend(
            [

                f'load "{flexible_receptor}", flexible_receptor',

                "show sticks, flexible_receptor",

            ]
        )

    lines.extend(
        [

            f'load "{pose_file}", ligand',

            "hide everything, all",

            "show cartoon, receptor",

            "show sticks, ligand",

            "set stick_radius, 0.18, ligand",

            "zoom ligand, 12",

            "bg_color white",

        ]
    )

    script_file.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return script_file


def find_windows_pymol():
    """
    Try several common Windows PyMOL locations.

    This is only a convenience function.
    The user can always configure the path manually.
    """

    possible_paths = [

        r"C:\Program Files\PyMOL\PyMOL.exe",

        r"C:\Program Files (x86)\PyMOL\PyMOL.exe",

        r"C:\Program Files\Schrodinger\PyMOL\PyMOL.exe",

    ]

    for path in possible_paths:

        try:

            result = subprocess.run(
                [

                    "cmd.exe",

                    "/C",

                    "if",

                    "exist",

                    path,

                    "echo",

                    path,

                ],
                capture_output=True,
                text=True,
            )

            if result.stdout.strip():

                return path

        except Exception:

            continue

    return None


def launch_pymol(
    receptor_file,
    pose_file,
    flexible_receptor=None,
    pymol_path=None,
):
    """
    Launch PyMOL with the selected docking result.

    Supports:

        Linux
        Windows
        WSL -> Windows PyMOL
    """

    receptor_file = Path(
        receptor_file
    )

    pose_file = Path(
        pose_file
    )

    if not receptor_file.exists():

        raise RuntimeError(
            "Receptor file does not exist:\n"
            f"{receptor_file}"
        )

    if not pose_file.exists():

        raise RuntimeError(
            "Docked pose file does not exist:\n"
            f"{pose_file}"
        )

    if flexible_receptor:

        flexible_receptor = Path(
            flexible_receptor
        )

        if not flexible_receptor.exists():

            flexible_receptor = None

    script_file = pose_file.with_suffix(
        ".pml"
    )

    # ------------------------------------------------------
    # WSL
    # ------------------------------------------------------

    if is_wsl():

        if not pymol_path:

            pymol_path = find_windows_pymol()

        if not pymol_path:

            raise RuntimeError(
                "Windows PyMOL could not be located.\n\n"
                "Please configure the PyMOL executable path."
            )

        receptor_win = wsl_to_windows_path(
            receptor_file
        )

        pose_win = wsl_to_windows_path(
            pose_file
        )

        if flexible_receptor:

            flex_win = wsl_to_windows_path(
                flexible_receptor
            )

        else:

            flex_win = None

        script_win = wsl_to_windows_path(
            script_file
        )

        create_pymol_script(
            receptor_win,
            pose_win,
            script_win,
            flex_win,
        )

        subprocess.Popen(
            [

                "cmd.exe",

                "/C",

                pymol_path,

                script_win,

            ]
        )

        return

    # ------------------------------------------------------
    # Native Windows
    # ------------------------------------------------------

    if os.name == "nt":

        if not pymol_path:

            pymol_path = find_windows_pymol()

        if not pymol_path:

            pymol_path = "pymol"

        create_pymol_script(
            receptor_file,
            pose_file,
            script_file,
            flexible_receptor,
        )

        subprocess.Popen(
            [

                pymol_path,

                str(script_file),

            ]
        )

        return

    # ------------------------------------------------------
    # Native Linux
    # ------------------------------------------------------

    if not pymol_path:

        pymol_path = shutil.which(
            "pymol"
        )

    if not pymol_path:

        pymol_path = "pymol"

    create_pymol_script(
        receptor_file,
        pose_file,
        script_file,
        flexible_receptor,
    )

    subprocess.Popen(
        [

            pymol_path,

            str(script_file),

        ]
    )