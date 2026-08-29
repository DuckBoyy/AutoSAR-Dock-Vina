import re
import subprocess

from pathlib import Path

from rdkit import Chem


def safe_filename(name):
    """
    Convert a compound/configuration name into a safe filename.
    """

    name = str(name).strip()

    name = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        name,
    )

    name = name.strip(
        "._"
    )

    if not name:
        name = "compound"

    return name


class DockingEngine:

    def __init__(
        self,
        config,
    ):

        self.config = dict(
            config
        )

    # ==========================================================
    # LIGAND PREPARATION
    # ==========================================================

    def prepare_ligand(
        self,
        mol,
        compound_name,
        output_directory,
    ):

        output_directory = Path(
            output_directory
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        compound_name = safe_filename(
            compound_name
        )

        sdf_file = (
            output_directory
            / f"{compound_name}.sdf"
        )

        pdbqt_file = (
            output_directory
            / f"{compound_name}.pdbqt"
        )

        writer = Chem.SDWriter(
            str(sdf_file)
        )

        writer.write(
            mol
        )

        writer.close()

        obabel = self.config.get(
            "obabel",
            "obabel",
        )

        command = [

            str(obabel),

            str(sdf_file),

            "-O",

            str(pdbqt_file),

            "--gen3d",
        ]

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:

            raise RuntimeError(
                "Open Babel could not be found.\n\n"
                "Configured executable:\n"
                f"{obabel}"
            )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr
                or result.stdout
                or "Open Babel ligand conversion failed."
            )

        if not pdbqt_file.exists():

            raise RuntimeError(
                "Open Babel did not create:\n"
                f"{pdbqt_file}"
            )

        return pdbqt_file

    # ==========================================================
    # TARGET NAME
    # ==========================================================

    def get_target_name(self):

        name = self.config.get(
            "name"
        )

        if not name:

            name = self.config.get(
                "target_name"
            )

        if not name:

            receptor = self.config.get(
                "receptor"
            )

            if receptor:

                name = Path(
                    receptor
                ).stem

        if not name:

            name = "Docking_Target"

        return safe_filename(
            name
        )

    # ==========================================================
    # VINA COMMAND
    # ==========================================================

    def build_vina_command(
        self,
        ligand_pdbqt,
        poses_file,
    ):

        vina = self.config.get(
            "vina",
            "vina",
        )

        receptor = self.config.get(
            "receptor"
        )

        if not receptor:

            raise RuntimeError(
                "No receptor has been configured."
            )

        command = [

            str(vina),

            "--receptor",
            str(receptor),

            "--ligand",
            str(ligand_pdbqt),

            "--center_x",
            str(
                self.config[
                    "center_x"
                ]
            ),

            "--center_y",
            str(
                self.config[
                    "center_y"
                ]
            ),

            "--center_z",
            str(
                self.config[
                    "center_z"
                ]
            ),

            "--size_x",
            str(
                self.config[
                    "size_x"
                ]
            ),

            "--size_y",
            str(
                self.config[
                    "size_y"
                ]
            ),

            "--size_z",
            str(
                self.config[
                    "size_z"
                ]
            ),

            "--exhaustiveness",
            str(
                self.config.get(
                    "exhaustiveness",
                    32,
                )
            ),

            "--num_modes",
            str(
                self.config.get(
                    "poses",
                    5,
                )
            ),

            "--out",
            str(poses_file),
        ]

        if (
            self.config.get(
                "flexible",
                False,
            )
            and self.config.get(
                "flex_receptor"
            )
        ):

            command.extend(
                [

                    "--flex",

                    str(
                        self.config[
                            "flex_receptor"
                        ]
                    ),
                ]
            )

        return command

    # ==========================================================
    # SAVE LOG
    # ==========================================================

    def save_log(
        self,
        log_file,
        command,
        result,
    ):

        log_file = Path(
            log_file
        )

        with open(
            log_file,
            "w",
            encoding="utf-8",
        ) as handle:

            handle.write(
                "AUTOSAR DOCK - VINA LOG\n"
            )

            handle.write(
                "=" * 70
                + "\n\n"
            )

            handle.write(
                "COMMAND\n"
            )

            handle.write(
                " ".join(
                    str(x)
                    for x in command
                )
            )

            handle.write(
                "\n\nRETURN CODE\n"
            )

            handle.write(
                str(
                    result.returncode
                )
            )

            handle.write(
                "\n\nSTDOUT\n"
            )

            handle.write(
                result.stdout
                or ""
            )

            handle.write(
                "\n\nSTDERR\n"
            )

            handle.write(
                result.stderr
                or ""
            )

    # ==========================================================
    # PARSE ALL VINA SCORES
    # ==========================================================

    def extract_pose_scores(
        self,
        poses_file,
    ):
        """
        Read every:

            REMARK VINA RESULT:

        line from the generated PDBQT.

        Returns a list of dictionaries:

            [
                {
                    "rank": 1,
                    "score": -10.43
                },
                ...
            ]
        """

        poses_file = Path(
            poses_file
        )

        if not poses_file.exists():

            raise RuntimeError(
                "Pose file does not exist:\n"
                f"{poses_file}"
            )

        scores = []

        with open(
            poses_file,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as handle:

            for line in handle:

                if "VINA RESULT:" not in line:
                    continue

                try:

                    text = (
                        line
                        .split(
                            "VINA RESULT:"
                        )[1]
                        .strip()
                    )

                    value = float(
                        text.split()[0]
                    )

                    scores.append(
                        {
                            "rank":
                                len(scores) + 1,

                            "score":
                                value,
                        }
                    )

                except (
                    ValueError,
                    IndexError,
                ):

                    continue

        if not scores:

            raise RuntimeError(
                "No VINA RESULT records were found in:\n"
                f"{poses_file}"
            )

        return scores

    # ==========================================================
    # BACKWARD-COMPATIBLE BEST SCORE
    # ==========================================================

    def extract_best_score(
        self,
        poses_file,
    ):

        poses = self.extract_pose_scores(
            poses_file
        )

        return float(
            min(
                pose["score"]
                for pose in poses
            )
        )

    # ==========================================================
    # DOCK
    # ==========================================================

    def dock(
        self,
        ligand_pdbqt,
        compound_name,
        output_directory,
    ):

        output_directory = Path(
            output_directory
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        compound_name = safe_filename(
            compound_name
        )

        target_name = (
            self.get_target_name()
        )

        output_prefix = (
            f"{compound_name}"
            f"__"
            f"{target_name}"
        )

        poses_file = (
            output_directory
            / f"{output_prefix}_poses.pdbqt"
        )

        log_file = (
            output_directory
            / f"{output_prefix}_vina.log"
        )

        command = self.build_vina_command(
            ligand_pdbqt,
            poses_file,
        )

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:

            raise RuntimeError(
                "AutoDock Vina could not be found.\n\n"
                "Configured executable:\n"
                f"{self.config.get('vina', 'vina')}"
            )

        self.save_log(
            log_file,
            command,
            result,
        )

        if result.returncode != 0:

            raise RuntimeError(
                result.stderr
                or result.stdout
                or "AutoDock Vina failed."
            )

        if not poses_file.exists():

            raise RuntimeError(
                "Vina completed without creating:\n"
                f"{poses_file}\n\n"
                f"See log:\n{log_file}"
            )

        pose_scores = (
            self.extract_pose_scores(
                poses_file
            )
        )

        best_pose = min(
            pose_scores,
            key=lambda x: x["score"]
        )

        return {

            # Backward-compatible
            # main score.
            "score":
                float(
                    best_pose["score"]
                ),

            # New complete pose data.
            "poses":
                pose_scores,

            "best_pose":
                int(
                    best_pose["rank"]
                ),

            "poses_file":
                str(
                    poses_file
                ),

            "log_file":
                str(
                    log_file
                ),

            "target_name":
                target_name,
        }
