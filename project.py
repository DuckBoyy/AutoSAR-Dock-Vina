import json
from pathlib import Path

from rdkit import Chem


PROJECT_VERSION = "3.4"


class Project:
    """
    AutoSAR Dock project model.

    Stores:

        - compounds
        - SAR metadata
        - experimental activity data
        - multiple docking targets
        - multiple docking poses per target
        - project docking configurations
        - PyMOL configuration
    """

    def __init__(self):

        self.project_directory = None

        self.compounds = {}

        self.active_config = {}

        self.docking_configs = []

        self.settings = {
            "pymol_path": "",
        }

        self.counter = 0

    # ============================================================
    # PROJECT CREATION
    # ============================================================

    def new(
        self,
        directory,
    ):

        self.project_directory = Path(
            directory
        )

        self.project_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            self.project_directory
            / "compounds"
        ).mkdir(
            exist_ok=True,
        )

        (
            self.project_directory
            / "docking_results"
        ).mkdir(
            exist_ok=True,
        )

        self.compounds = {}

        self.active_config = {}

        self.docking_configs = []

        self.settings = {
            "pymol_path": "",
        }

        self.counter = 0

        self.save()

    # ============================================================
    # PROJECT OPEN
    # ============================================================

    def open(
        self,
        directory,
    ):

        directory = Path(
            directory
        )

        project_file = (
            directory
            / "project.json"
        )

        if not project_file.exists():

            raise FileNotFoundError(
                "project.json was not found in:\n"
                f"{directory}"
            )

        with open(
            project_file,
            "r",
            encoding="utf-8",
        ) as handle:

            data = json.load(
                handle
            )

        self.project_directory = directory

        self.counter = int(
            data.get(
                "counter",
                0,
            )
        )

        self.active_config = dict(
            data.get(
                "active_config",
                {},
            )
        )

        self.docking_configs = list(
            data.get(
                "docking_configs",
                [],
            )
        )

        self.settings = dict(
            data.get(
                "settings",
                {},
            )
        )

        self.settings.setdefault(
            "pymol_path",
            "",
        )

        self.compounds = {}

        raw_compounds = data.get(
            "compounds",
            {},
        )

        # --------------------------------------------------------
        # Support dictionary-style project files.
        # --------------------------------------------------------

        if isinstance(
            raw_compounds,
            list,
        ):

            converted = {}

            for index, compound in enumerate(
                raw_compounds
            ):

                compound_id = compound.get(
                    "id",
                    f"CMP_{index:05d}",
                )

                converted[
                    str(compound_id)
                ] = compound

            raw_compounds = converted

        # --------------------------------------------------------
        # Load each compound.
        # --------------------------------------------------------

        for compound_id, metadata in (
            raw_compounds.items()
        ):

            compound = dict(
                metadata
            )

            compound_id = str(
                compound_id
            )

            sdf_path = (
                directory
                / "compounds"
                / f"{compound_id}.sdf"
            )

            # ----------------------------------------------------
            # Older projects may have stored an alternate path.
            # ----------------------------------------------------

            if not sdf_path.exists():

                relative_sdf = compound.get(
                    "SDF",
                    compound.get(
                        "sdf",
                        "",
                    ),
                )

                if relative_sdf:

                    candidate = (
                        directory
                        / relative_sdf
                    )

                    if candidate.exists():

                        sdf_path = candidate

            mol = None

            if sdf_path.exists():

                try:

                    supplier = (
                        Chem.SDMolSupplier(
                            str(
                                sdf_path
                            ),
                            removeHs=False,
                        )
                    )

                    for candidate in supplier:

                        if candidate is not None:

                            mol = candidate

                            break

                except Exception:

                    mol = None

            # ----------------------------------------------------
            # Defaults for backward compatibility.
            # ----------------------------------------------------

            compound.setdefault(
                "name",
                compound_id,
            )

            compound.setdefault(
                "source",
                "",
            )

            compound.setdefault(
                "parent_id",
                "",
            )

            compound.setdefault(
                "sar_operation",
                "",
            )

            compound.setdefault(
                "generation",
                0,
            )

            compound.setdefault(
                "properties",
                {},
            )

            compound.setdefault(
                "smiles",
                "",
            )

            compound.setdefault(
                "activity_type",
                "IC50",
            )

            compound.setdefault(
                "activity_value",
                "",
            )

            compound.setdefault(
                "activity_unit",
                "nM",
            )

            compound.setdefault(
                "notes",
                "",
            )

            compound.setdefault(
                "docking_results",
                [],
            )

            # ----------------------------------------------------
            # Normalize docking result format.
            # ----------------------------------------------------

            compound[
                "docking_results"
            ] = self._normalize_docking_results(
                compound[
                    "docking_results"
                ]
            )

            if mol is not None:

                compound[
                    "mol"
                ] = mol

            elif not compound.get(
                "smiles"
            ):

                # Nothing usable remains.
                continue

            self.compounds[
                compound_id
            ] = compound

    # ============================================================
    # NORMALIZE DOCKING RESULTS
    # ============================================================

    @staticmethod
    def _normalize_docking_results(
        results,
    ):
        """
        Normalize old dictionary-style docking results and
        newer list-style results into a common list format.
        """

        if results is None:

            return []

        # --------------------------------------------------------
        # Old format:
        #
        # {
        #     "Target A": {
        #         "score": -8.2,
        #         ...
        #     }
        # }
        # --------------------------------------------------------

        if isinstance(
            results,
            dict,
        ):

            converted = []

            for target_name, result in (
                results.items()
            ):

                if isinstance(
                    result,
                    dict,
                ):

                    item = dict(
                        result
                    )

                else:

                    item = {
                        "score": result
                    }

                item.setdefault(
                    "target_name",
                    target_name,
                )

                item.setdefault(
                    "poses",
                    [],
                )

                if not item[
                    "poses"
                ]:

                    score = item.get(
                        "score"
                    )

                    if score is not None:

                        try:

                            item[
                                "poses"
                            ] = [

                                {
                                    "rank": 1,

                                    "score": float(
                                        score
                                    ),
                                }
                            ]

                        except (
                            TypeError,
                            ValueError,
                        ):

                            item[
                                "poses"
                            ] = []

                item = (
                    Project
                    ._normalize_single_result(
                        item
                    )
                )

                converted.append(
                    item
                )

            return converted

        # --------------------------------------------------------
        # New list format.
        # --------------------------------------------------------

        if isinstance(
            results,
            list,
        ):

            normalized = []

            for result in results:

                if not isinstance(
                    result,
                    dict,
                ):

                    continue

                normalized.append(
                    Project
                    ._normalize_single_result(
                        dict(result)
                    )
                )

            return normalized

        return []

    @staticmethod
    def _normalize_single_result(
        result,
    ):
        """
        Normalize one docking result.
        """

        result.setdefault(
            "target_name",
            result.get(
                "target",
                "",
            ),
        )

        result.setdefault(
            "poses_file",
            None,
        )

        result.setdefault(
            "log_file",
            None,
        )

        result.setdefault(
            "best_pose",
            1,
        )

        raw_poses = result.get(
            "poses",
            [],
        )

        normalized_poses = []

        if isinstance(
            raw_poses,
            dict,
        ):

            raw_poses = [
                raw_poses
            ]

        if isinstance(
            raw_poses,
            list,
        ):

            for index, pose in enumerate(
                raw_poses,
                start=1,
            ):

                if not isinstance(
                    pose,
                    dict,
                ):

                    continue

                rank = pose.get(
                    "rank",
                    index,
                )

                score = pose.get(
                    "score"
                )

                try:

                    rank = int(
                        rank
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    rank = index

                try:

                    score = float(
                        score
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    continue

                normalized_poses.append(
                    {
                        "rank": rank,
                        "score": score,
                    }
                )

        result[
            "poses"
        ] = sorted(

            normalized_poses,

            key=lambda pose:
                pose[
                    "rank"
                ],
        )

        # --------------------------------------------------------
        # Recalculate best pose whenever possible.
        # --------------------------------------------------------

        if result[
            "poses"
        ]:

            best = min(

                result[
                    "poses"
                ],

                key=lambda pose:
                    pose[
                        "score"
                    ],
            )

            result[
                "best_pose"
            ] = int(
                best[
                    "rank"
                ]
            )

            result[
                "score"
            ] = float(
                best[
                    "score"
                ]
            )

        else:

            score = result.get(
                "score"
            )

            try:

                result[
                    "score"
                ] = float(
                    score
                )

            except (
                TypeError,
                ValueError,
            ):

                result[
                    "score"
                ] = None

        return result

    # ============================================================
    # SAVE
    # ============================================================

    def save(
        self,
    ):

        if self.project_directory is None:

            raise RuntimeError(
                "No project directory is open."
            )

        data = {

            "version":
                PROJECT_VERSION,

            "counter":
                self.counter,

            "active_config":
                self.active_config,

            "docking_configs":
                self.docking_configs,

            "settings":
                self.settings,

            "compounds":
                {},
        }

        for compound_id, compound in (
            self.compounds.items()
        ):

            docking_results = (
                self._normalize_docking_results(
                    compound.get(
                        "docking_results",
                        [],
                    )
                )
            )

            data[
                "compounds"
            ][
                compound_id
            ] = {

                "name":
                    compound.get(
                        "name",
                        compound_id,
                    ),

                "source":
                    compound.get(
                        "source",
                        "",
                    ),

                "parent_id":
                    compound.get(
                        "parent_id",
                        "",
                    ),

                "sar_operation":
                    compound.get(
                        "sar_operation",
                        "",
                    ),

                "generation":
                    compound.get(
                        "generation",
                        0,
                    ),

                "properties":
                    compound.get(
                        "properties",
                        {},
                    ),

                "smiles":
                    compound.get(
                        "smiles",
                        "",
                    ),

                "activity_type":
                    compound.get(
                        "activity_type",
                        "IC50",
                    ),

                "activity_value":
                    compound.get(
                        "activity_value",
                        "",
                    ),

                "activity_unit":
                    compound.get(
                        "activity_unit",
                        "nM",
                    ),

                "notes":
                    compound.get(
                        "notes",
                        "",
                    ),

                "docking_results":
                    docking_results,
            }

        project_file = (
            self.project_directory
            / "project.json"
        )

        with open(
            project_file,
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                data,
                handle,
                indent=2,
            )

        return project_file

    # ============================================================
    # COMPOUNDS
    # ============================================================

    def add_compound(
        self,
        mol,
        name=None,
        source="",
        parent_id="",
        sar_operation="",
    ):

        from .chemistry import (
            molecule_properties,
            molecule_to_smiles,
            write_sdf,
        )

        if self.project_directory is None:

            raise RuntimeError(
                "Create or open a project first."
            )

        compound_id = (
            f"CMP_{self.counter:05d}"
        )

        self.counter += 1

        if not name:

            name = compound_id

        properties = (
            molecule_properties(
                mol
            )
        )

        generation = 0

        if parent_id:

            parent = self.compounds.get(
                parent_id
            )

            if parent is not None:

                generation = (
                    int(
                        parent.get(
                            "generation",
                            0,
                        )
                    )
                    + 1
                )

        compound = {

            "mol":
                Chem.Mol(
                    mol
                ),

            "name":
                name,

            "source":
                source,

            "parent_id":
                parent_id,

            "sar_operation":
                sar_operation,

            "generation":
                generation,

            "properties":
                properties,

            "smiles":
                molecule_to_smiles(
                    mol
                ),

            "activity_type":
                "IC50",

            "activity_value":
                "",

            "activity_unit":
                "nM",

            "notes":
                "",

            "docking_results":
                [],
        }

        self.compounds[
            compound_id
        ] = compound

        sdf_path = (
            self.project_directory
            / "compounds"
            / f"{compound_id}.sdf"
        )

        write_sdf(
            mol,
            sdf_path,
        )

        self.save()

        return compound_id

    # ============================================================
    # MOLECULE
    # ============================================================

    def get_molecule(
        self,
        compound_id,
    ):

        if compound_id not in self.compounds:

            raise KeyError(
                compound_id
            )

        compound = self.compounds[
            compound_id
        ]

        if "mol" not in compound:

            raise RuntimeError(
                f"No molecule is loaded for {compound_id}"
            )

        return Chem.Mol(
            compound[
                "mol"
            ]
        )

    # ============================================================
    # SAR
    # ============================================================

    def add_sar_products(
        self,
        parent_id,
        products,
        operation,
    ):

        if parent_id not in self.compounds:

            raise KeyError(
                parent_id
            )

        ids = []

        parent = self.compounds[
            parent_id
        ]

        parent_name = parent.get(
            "name",
            parent_id,
        )

        generation = (

            int(
                parent.get(
                    "generation",
                    0,
                )
            )
            + 1
        )

        for index, (
            variant,
            mol,
        ) in enumerate(
            products,
            start=1,
        ):

            if mol is None:
                continue

            name = (

                f"{parent_name}_"
                f"G{generation}_"
                f"{operation.replace(' ', '_')}_"
                f"{variant}_"
                f"{index}"
            )

            compound_id = self.add_compound(

                mol=mol,

                name=name,

                source="SAR",

                parent_id=parent_id,

                sar_operation=operation,
            )

            self.compounds[
                compound_id
            ][
                "generation"
            ] = generation

            ids.append(
                compound_id
            )

        self.save()

        return ids

    # ============================================================
    # EXPERIMENTAL ACTIVITY
    # ============================================================

    def update_activity(
        self,
        compound_id,
        activity_type,
        activity_value,
        activity_unit,
        notes="",
    ):

        if compound_id not in self.compounds:

            raise KeyError(
                compound_id
            )

        compound = self.compounds[
            compound_id
        ]

        compound[
            "activity_type"
        ] = activity_type

        compound[
            "activity_value"
        ] = activity_value

        compound[
            "activity_unit"
        ] = activity_unit

        compound[
            "notes"
        ] = notes

        self.save()

    # ============================================================
    # DOCKING RESULTS
    # ============================================================

    def set_docking_result(
        self,
        compound_id,
        docking_target,
        score,
        poses_file=None,
        log_file=None,
        poses=None,
        best_pose=1,
    ):
        """
        Store one docking result for a compound against a target.

        Multiple targets are independently retained.

        Multiple poses are retained within each target.
        """

        if compound_id not in self.compounds:

            raise KeyError(
                compound_id
            )

        compound = self.compounds[
            compound_id
        ]

        results = compound.setdefault(
            "docking_results",
            [],
        )

        results = self._normalize_docking_results(
            results
        )

        compound[
            "docking_results"
        ] = results

        # --------------------------------------------------------
        # Normalize pose list.
        # --------------------------------------------------------

        normalized_poses = []

        for index, pose in enumerate(
            poses or [],
            start=1,
        ):

            if not isinstance(
                pose,
                dict,
            ):

                continue

            rank = pose.get(
                "rank",
                index,
            )

            pose_score = pose.get(
                "score"
            )

            try:

                rank = int(
                    rank
                )

                pose_score = float(
                    pose_score
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            normalized_poses.append({

                "rank":
                    rank,

                "score":
                    pose_score,
            })

        # --------------------------------------------------------
        # If the caller did not supply individual pose scores,
        # retain the single score as Pose 1 for compatibility.
        # --------------------------------------------------------

        if not normalized_poses and score is not None:

            try:

                normalized_poses = [

                    {
                        "rank": 1,

                        "score":
                            float(
                                score
                            ),
                    }
                ]

            except (
                TypeError,
                ValueError,
            ):

                normalized_poses = []

        # --------------------------------------------------------
        # Determine best pose.
        # --------------------------------------------------------

        if normalized_poses:

            best = min(

                normalized_poses,

                key=lambda pose:
                    pose[
                        "score"
                    ],
            )

            final_score = float(
                best[
                    "score"
                ]
            )

            final_best_pose = int(
                best[
                    "rank"
                ]
            )

        else:

            try:

                final_score = (
                    float(score)
                    if score is not None
                    else None
                )

            except (
                TypeError,
                ValueError,
            ):

                final_score = None

            final_best_pose = int(
                best_pose
            )

        new_result = {

            "target_name":
                str(
                    docking_target
                ),

            "score":
                final_score,

            "best_pose":
                final_best_pose,

            "poses":
                normalized_poses,

            "poses_file":
                poses_file,

            "log_file":
                log_file,
        }

        # --------------------------------------------------------
        # Replace existing target result.
        # --------------------------------------------------------

        existing = None

        for result in results:

            target = result.get(

                "target_name",

                result.get(
                    "target",
                    "",
                ),
            )

            if target == docking_target:

                existing = result

                break

        if existing is not None:

            existing.update(
                new_result
            )

        else:

            results.append(
                new_result
            )

        self.save()

    def get_docking_result(
        self,
        compound_id,
        docking_target,
    ):

        if compound_id not in self.compounds:

            return None

        compound = self.compounds[
            compound_id
        ]

        results = self._normalize_docking_results(
            compound.get(
                "docking_results",
                [],
            )
        )

        for result in results:

            target = result.get(

                "target_name",

                result.get(
                    "target",
                    "",
                ),
            )

            if target == docking_target:

                return result

        return None

    def get_docking_score(
        self,
        compound_id,
        docking_target,
    ):

        result = self.get_docking_result(

            compound_id,

            docking_target,
        )

        if result is None:

            return None

        score = result.get(
            "score"
        )

        try:

            return float(
                score
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    def get_pose_scores(
        self,
        compound_id,
        docking_target,
    ):
        """
        Return all stored pose scores for a compound/target.
        """

        result = self.get_docking_result(

            compound_id,

            docking_target,
        )

        if result is None:

            return []

        poses = result.get(
            "poses",
            [],
        )

        if poses:

            return sorted(

                [

                    {
                        "rank":
                            int(
                                pose[
                                    "rank"
                                ]
                            ),

                        "score":
                            float(
                                pose[
                                    "score"
                                ]
                            ),
                    }

                    for pose in poses

                    if pose.get(
                        "score"
                    ) is not None
                ],

                key=lambda pose:
                    pose[
                        "rank"
                    ],
            )

        # --------------------------------------------------------
        # Backward compatibility for old one-score results.
        # --------------------------------------------------------

        score = result.get(
            "score"
        )

        if score is None:

            return []

        try:

            return [

                {
                    "rank": 1,

                    "score":
                        float(
                            score
                        ),
                }
            ]

        except (
            TypeError,
            ValueError,
        ):

            return []

    def get_best_pose(
        self,
        compound_id,
        docking_target,
    ):
        """
        Return the best-scoring pose.
        """

        poses = self.get_pose_scores(

            compound_id,

            docking_target,
        )

        if not poses:

            return None

        return min(

            poses,

            key=lambda pose:
                pose[
                    "score"
                ],
        )

    def compound_docked_to_target(
        self,
        compound_id,
        docking_target,
    ):

        return (

            self.get_docking_score(

                compound_id,

                docking_target,
            )

            is not None
        )

    def docking_targets(
        self,
    ):

        targets = set()

        for compound in (
            self.compounds.values()
        ):

            results = self._normalize_docking_results(

                compound.get(

                    "docking_results",

                    [],
                )
            )

            for result in results:

                target = result.get(

                    "target_name",

                    result.get(
                        "target",
                        "",
                    ),
                )

                if target:

                    targets.add(
                        target
                    )

        return sorted(

            targets,

            key=str.lower,
        )

    # ============================================================
    # PROJECT DOCKING CONFIGURATIONS
    # ============================================================

    def add_docking_config(
        self,
        config,
    ):

        self.docking_configs.append(
            dict(
                config
            )
        )

        self.save()

    def update_docking_config(
        self,
        index,
        config,
    ):

        self.docking_configs[
            index
        ] = dict(
            config
        )

        self.save()

    def remove_docking_config(
        self,
        index,
    ):

        del self.docking_configs[
            index
        ]

        self.save()

    # ============================================================
    # PYMol
    # ============================================================

    def set_pymol_path(
        self,
        path,
    ):

        self.settings[
            "pymol_path"
        ] = str(
            path
        )

        self.save()


class GlobalDockingConfigLibrary:
    """
    Global reusable docking configurations.

    Stored separately from individual projects at:

        ~/.autosar_dock/docking_configurations.json
    """

    def __init__(
        self,
    ):

        self.directory = (

            Path.home()

            /

            ".autosar_dock"
        )

        self.directory.mkdir(

            parents=True,

            exist_ok=True,
        )

        self.filename = (

            self.directory

            /

            "docking_configurations.json"
        )

        self.configurations = {}

        self.load()

    def load(
        self,
    ):

        if not self.filename.exists():

            self.configurations = {}

            return

        try:

            with open(

                self.filename,

                "r",

                encoding="utf-8",

            ) as handle:

                data = json.load(
                    handle
                )

            if isinstance(
                data,
                dict,
            ):

                self.configurations = data

            else:

                self.configurations = {}

        except Exception:

            self.configurations = {}

    def save(
        self,
    ):

        with open(

            self.filename,

            "w",

            encoding="utf-8",

        ) as handle:

            json.dump(

                self.configurations,

                handle,

                indent=2,
            )

    def names(
        self,
    ):

        return sorted(

            self.configurations.keys(),

            key=str.lower,
        )

    def get(
        self,
        name,
    ):

        if name not in self.configurations:

            raise KeyError(

                f"Global docking configuration "
                f"'{name}' was not found."
            )

        return dict(
            self.configurations[
                name
            ]
        )

    def add(
        self,
        name,
        configuration,
    ):

        name = str(
            name
        ).strip()

        if not name:

            raise ValueError(

                "Configuration name cannot be empty."
            )

        configuration = dict(
            configuration
        )

        configuration[
            "name"
        ] = name

        self.configurations[
            name
        ] = configuration

        self.save()

    def delete(
        self,
        name,
    ):

        if name in self.configurations:

            del self.configurations[
                name
            ]

            self.save()