import os
import shutil
import tempfile
import math
import subprocess

from pathlib import Path

import tkinter as tk

from tkinter import (
    ttk,
    filedialog,
    messagebox,
    simpledialog,
)

from PIL import Image
from PIL import ImageTk

from .chemistry import (
    load_molecule,
    molecule_image,
    atom_information,
    bond_information,
)

from .sar import (
    LINKER_LIBRARIES,
    REPLACEMENT_LIBRARIES,
    linker_library,
    bond_linker_library,
    replacement_library,
    delete_atom,
    delete_functional_group,
)

from .project import (
    Project,
    GlobalDockingConfigLibrary,
)

from .docking import (
    DockingEngine,
    safe_filename,
)

from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog

from .analysis import (
    flatten_project,
    export_csv,
    export_excel,
    calculate_pactivity,
    correlation,
    plot_relationship,
)

from .pose_viewer import (
    launch_pymol,
)

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)

class AutoSARDockApp:

    def __init__(
        self,
        root,
    ):

        self.root = root

        self.root.title(
            "AutoSAR Dock v3.4"
        )

        self.root.geometry(
            "1700x900"
        )

        self.project = Project()

        self.global_docking_configs = (
            GlobalDockingConfigLibrary()
        )

        self.current_id = None

        self.status = tk.StringVar(
            value="Create or open a project."
        )

        self.build_interface()

    # ============================================================
    # INTERFACE
    # ============================================================

    def build_interface(self):

        menu = tk.Menu(
            self.root
        )

        self.root.config(
            menu=menu
        )

        project_menu = tk.Menu(
            menu,
            tearoff=False,
        )

        menu.add_cascade(
            label="Project",
            menu=project_menu,
        )

        project_menu.add_command(
            label="New Project",
            command=self.new_project,
        )

        project_menu.add_command(
            label="Open Project",
            command=self.open_project,
        )

        project_menu.add_command(
            label="Save Project",
            command=self.save_project,
        )

        project_menu.add_separator()

        project_menu.add_command(
            label="Export CSV",
            command=self.export_csv,
        )

        project_menu.add_command(
            label="Export Excel",
            command=self.export_excel,
        )

        molecule_menu = tk.Menu(
            menu,
            tearoff=False,
        )

        menu.add_cascade(
            label="Molecule",
            menu=molecule_menu,
        )

        molecule_menu.add_command(
            label="Import Molecule",
            command=self.import_molecule,
        )

        molecule_menu.add_command(
            label="View Structure",
            command=self.view_structure,
        )

        molecule_menu.add_command(
            label="Generate SAR",
            command=self.open_sar_window,
        )

        molecule_menu.add_command(
            label="Experimental Data",
            command=self.edit_experimental_data,
        )

        docking_menu = tk.Menu(
            menu,
            tearoff=False,
        )

        menu.add_cascade(
            label="Docking",
            menu=docking_menu,
        )

        docking_menu.add_command(
            label="Configure Docking",
            command=self.configure_docking,
        )

        docking_menu.add_command(
            label="Run Docking Campaign",
            command=self.open_docking_campaign_window,
        )

        docking_menu.add_separator()

        docking_menu.add_command(
            label="Pose Scores",
            command=self.show_pose_scores,
        )

        docking_menu.add_command(
            label="View Docked Pose",
            command=self.view_selected_pose,
        )

        docking_menu.add_command(
            label="Configure PyMOL",
            command=self.configure_pymol,
        )

        docking_menu.add_command(
            label="Analyze Data",
            command=self.open_analysis_window,
        )

        toolbar = ttk.Frame(
            self.root,
            padding=5,
        )

        toolbar.pack(
            fill="x"
        )

        ttk.Button(
            toolbar,
            text="New Project",
            command=self.new_project,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Open Project",
            command=self.open_project,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Import Molecule",
            command=self.import_molecule,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="View Structure",
            command=self.view_structure,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Generate SAR",
            command=self.open_sar_window,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Docking Configuration",
            command=self.configure_docking,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Run Campaign",
            command=self.open_docking_campaign_window,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Pose Scores",
            command=self.show_pose_scores,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="View Pose",
            command=self.view_selected_pose,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Experimental Data",
            command=self.edit_experimental_data,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Analyze",
            command=self.open_analysis_window,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Export CSV",
            command=self.export_csv,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            toolbar,
            text="Export Excel",
            command=self.export_excel,
        ).pack(
            side="left",
            padx=3,
        )

        table_frame = ttk.Frame(
            self.root,
            padding=10,
        )

        table_frame.pack(
            fill="both",
            expand=True,
        )

        self.tree = ttk.Treeview(
            table_frame,
            show="headings",
        )

        yscroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )

        xscroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        yscroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        xscroll.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        table_frame.rowconfigure(
            0,
            weight=1,
        )

        table_frame.columnconfigure(
            0,
            weight=1,
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_table_selection,
        )

        self.tree.bind(
            "<Double-1>",
            lambda event: self.show_pose_scores(),
        )

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status,
            relief="sunken",
            anchor="w",
            padding=5,
        )

        status_bar.pack(
            fill="x",
            side="bottom",
        )

        self.refresh_table()

    # ============================================================
    # PROJECT
    # ============================================================

    def new_project(self):

        directory = filedialog.askdirectory(
            title="Create or Select Project Directory"
        )

        if not directory:

            return

        try:

            self.project.new(
                directory
            )

            self.current_id = None

            self.refresh_table()

            self.status.set(
                f"Project created: {directory}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Project Error",
                str(exc),
            )

    def open_project(self):

        directory = filedialog.askdirectory(
            title="Open Project"
        )

        if not directory:

            return

        try:

            self.project.open(
                directory
            )

            self.current_id = None

            self.refresh_table()

            self.status.set(
                f"Project opened: {directory}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Project Error",
                str(exc),
            )

    def save_project(self):

        try:

            self.project.save()

            self.status.set(
                "Project saved."
            )

        except Exception as exc:

            messagebox.showerror(
                "Save Error",
                str(exc),
            )

    # ============================================================
    # MOLECULE IMPORT
    # ============================================================

    def import_molecule(self):

        if (
            self.project.project_directory
            is None
        ):

            messagebox.showwarning(
                "Project Required",
                "Create or open a project first."
            )

            return

        filename = filedialog.askopenfilename(
            title="Import Molecule",
            filetypes=[
                (
                    "Structure files",
                    "*.sdf *.mol *.mol2 *.smi",
                ),

                (
                    "All files",
                    "*.*",
                ),
            ],
        )

        if not filename:

            return

        try:

            mol = load_molecule(
                filename
            )

            default_name = (
                Path(filename).stem
            )

            name = simpledialog.askstring(
                "Compound Name",
                "Compound name:",
                initialvalue=default_name,
                parent=self.root,
            )

            if not name:

                name = default_name

            compound_id = (
                self.project.add_compound(
                    mol,
                    name=name,
                    source=filename,
                )
            )

            self.current_id = compound_id

            self.refresh_table()

            self.status.set(
                f"Imported {name}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Import Error",
                str(exc),
            )

    # ============================================================
    # TABLE
    # ============================================================

    def get_table_columns(self):

        base = [

            "ID",

            "Name",

            "MW",

            "LogP",

            "TPSA",

            "HBD",

            "HBA",

            "RotB",

            "Rings",
        ]

        return (
            base
            + self.project.docking_targets()
        )

    def refresh_table(self):

        columns = (
            self.get_table_columns()
        )

        for item in self.tree.get_children():

            self.tree.delete(
                item
            )

        self.tree[
            "columns"
        ] = columns

        for column in columns:

            self.tree.heading(
                column,
                text=column,
                command=lambda c=column:
                    self.sort_table(c),
            )

            self.tree.column(
                column,
                width=115,
                anchor="center",
            )

        for compound_id, compound in (
            self.project.compounds.items()
        ):

            properties = compound.get(
                "properties",
                {},
            )

            row = [

                compound_id,

                compound.get(
                    "name",
                    compound_id,
                ),

                properties.get(
                    "MW",
                    "",
                ),

                properties.get(
                    "LogP",
                    "",
                ),

                properties.get(
                    "TPSA",
                    "",
                ),

                properties.get(
                    "HBD",
                    "",
                ),

                properties.get(
                    "HBA",
                    "",
                ),

                properties.get(
                    "RotB",
                    "",
                ),

                properties.get(
                    "Rings",
                    "",
                ),
            ]

            for target in (
                self.project.docking_targets()
            ):

                score = (
                    self.project
                    .get_docking_score(
                        compound_id,
                        target,
                    )
                )

                if score is None:

                    row.append(
                        ""
                    )

                else:

                    row.append(
                        f"{float(score):.2f}"
                    )

            self.tree.insert(
                "",
                "end",
                iid=compound_id,
                values=row,
            )

        self.apply_score_coloring()

    def sort_table(
        self,
        column,
    ):

        children = list(
            self.tree.get_children()
        )

        values = []

        column_index = list(
            self.tree[
                "columns"
            ]
        ).index(
            column
        )

        for item in children:

            value = self.tree.item(
                item,
                "values",
            )[column_index]

            try:

                value = float(
                    value
                )

            except Exception:

                value = str(
                    value
                ).lower()

            values.append(
                (
                    value,
                    item,
                )
            )

        reverse = getattr(
            self,
            "_sort_reverse",
            False,
        )

        values.sort(
            key=lambda x: x[0],
            reverse=reverse,
        )

        for index, (
            value,
            item,
        ) in enumerate(
            values
        ):

            self.tree.move(
                item,
                "",
                index,
            )

        self._sort_reverse = (
            not reverse
        )

    def apply_score_coloring(self):

        targets = (
            self.project.docking_targets()
        )

        all_scores = []

        for compound_id in (
            self.project.compounds
        ):

            for target in targets:

                score = (
                    self.project
                    .get_docking_score(
                        compound_id,
                        target,
                    )
                )

                if score is not None:

                    all_scores.append(
                        float(score)
                    )

        if not all_scores:

            return

        minimum = min(
            all_scores
        )

        maximum = max(
            all_scores
        )

        self.tree.tag_configure(
            "excellent",
            background="#B8D8FF",
        )

        self.tree.tag_configure(
            "moderate",
            background="#F4F4F4",
        )

        self.tree.tag_configure(
            "weak",
            background="#FFB8B8",
        )

        for compound_id in (
            self.project.compounds
        ):

            scores = []

            for target in targets:

                score = (
                    self.project
                    .get_docking_score(
                        compound_id,
                        target,
                    )
                )

                if score is not None:

                    scores.append(
                        float(score)
                    )

            if not scores:

                continue

            best = min(
                scores
            )

            if maximum == minimum:

                fraction = 0.5

            else:

                fraction = (
                    (best - minimum)
                    /
                    (maximum - minimum)
                )

            if fraction < 0.33:

                tag = "excellent"

            elif fraction < 0.66:

                tag = "moderate"

            else:

                tag = "weak"

            self.tree.item(
                compound_id,
                tags=(tag,),
            )

    def on_table_selection(
        self,
        event,
    ):

        selected = (
            self.tree.selection()
        )

        if selected:

            self.current_id = selected[0]

    def require_selection(self):

        if self.current_id is None:

            messagebox.showwarning(
                "No Compound Selected",
                "Select a compound first."
            )

            return False

        if (
            self.current_id
            not in self.project.compounds
        ):

            return False

        return True

    # ============================================================
    # STRUCTURE VIEWER
    # ============================================================

    def view_structure(self):

        if not self.require_selection():

            return

        mol = self.project.get_molecule(
            self.current_id
        )

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Structure Viewer"
        )

        window.geometry(
            "1000x800"
        )

        display = tk.StringVar(
            value="Atoms"
        )

        image_label = ttk.Label(
            window
        )

        image_label.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        control = ttk.Frame(
            window,
            padding=10,
        )

        control.pack(
            fill="x",
            side="bottom",
        )

        ttk.Label(
            control,
            text="Labels:",
        ).pack(
            side="left"
        )

        box = ttk.Combobox(
            control,
            textvariable=display,
            values=[
                "Atoms",
                "Bonds",
                "Both",
                "None",
            ],
            state="readonly",
            width=12,
        )

        box.pack(
            side="left",
            padx=5,
        )

        def render():

            value = display.get()

            png = molecule_image(
                mol,
                atom_indices=value in [
                    "Atoms",
                    "Both",
                ],
                bond_indices=value in [
                    "Bonds",
                    "Both",
                ],
            )

            temporary = tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False,
            )

            temporary.write(
                png
            )

            temporary.close()

            pil_image = Image.open(
                temporary.name
            )

            photo = ImageTk.PhotoImage(
                pil_image
            )

            image_label.configure(
                image=photo
            )

            image_label.image = photo

            os.unlink(
                temporary.name
            )

        box.bind(
            "<<ComboboxSelected>>",
            lambda event: render(),
        )

        ttk.Button(
            control,
            text="Atom Map",
            command=lambda:
                self.show_atom_map(
                    mol
                ),
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            control,
            text="Bond Map",
            command=lambda:
                self.show_bond_map(
                    mol
                ),
        ).pack(
            side="left",
            padx=5,
        )

        render()

    def show_atom_map(
        self,
        mol,
    ):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Atom Map"
        )

        tree = ttk.Treeview(
            window,
            columns=(
                "Index",
                "Element",
                "Atomic Number",
                "Aromatic",
                "Degree",
                "Hydrogens",
            ),
            show="headings",
        )

        tree.pack(
            fill="both",
            expand=True,
        )

        for column in tree[
            "columns"
        ]:

            tree.heading(
                column,
                text=column,
            )

        for atom in atom_information(
            mol
        ):

            tree.insert(
                "",
                "end",
                values=(
                    atom["index"],
                    atom["symbol"],
                    atom["atomic_number"],
                    atom["aromatic"],
                    atom["degree"],
                    atom["hydrogens"],
                ),
            )

    def show_bond_map(
        self,
        mol,
    ):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Bond Map"
        )

        tree = ttk.Treeview(
            window,
            columns=(
                "Bond",
                "Atom A",
                "Atom B",
                "Type",
                "Aromatic",
            ),
            show="headings",
        )

        tree.pack(
            fill="both",
            expand=True,
        )

        for column in tree[
            "columns"
        ]:

            tree.heading(
                column,
                text=column,
            )

        for bond in bond_information(
            mol
        ):

            tree.insert(
                "",
                "end",
                values=(
                    bond["index"],
                    bond["atom_a"],
                    bond["atom_b"],
                    bond["type"],
                    bond["aromatic"],
                ),
            )

    # ============================================================
    # SAR WINDOW
    # ============================================================

    def open_sar_window(self):

        if not self.require_selection():

            return

        mol = self.project.get_molecule(
            self.current_id
        )

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Generate SAR"
        )

        window.geometry(
            "1500x850"
        )

        image_frame = ttk.Frame(
            window
        )

        image_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10,
        )

        control_frame = ttk.Frame(
            window,
            padding=15,
            width=420,
        )

        control_frame.pack(
            side="right",
            fill="y",
        )

        display_mode = tk.StringVar(
            value="Atoms"
        )

        operation = tk.StringVar(
            value="Link atoms"
        )

        atom_a = tk.StringVar()

        atom_b = tk.StringVar()

        bond_number = tk.StringVar()

        keep_atom = tk.StringVar()

        library = tk.StringVar()

        instruction = tk.StringVar()

        image_label = ttk.Label(
            image_frame
        )

        image_label.pack(
            fill="both",
            expand=True,
        )

        def render():

            mode = display_mode.get()

            png = molecule_image(
                mol,
                width=1000,
                height=750,
                atom_indices=mode in [
                    "Atoms",
                    "Both",
                ],
                bond_indices=mode in [
                    "Bonds",
                    "Both",
                ],
            )

            temporary = tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False,
            )

            temporary.write(
                png
            )

            temporary.close()

            image = Image.open(
                temporary.name
            )

            photo = ImageTk.PhotoImage(
                image
            )

            image_label.configure(
                image=photo
            )

            image_label.image = photo

            os.unlink(
                temporary.name
            )

        ttk.Label(
            control_frame,
            text="Structure Labels",
        ).pack(
            anchor="w"
        )

        label_box = ttk.Combobox(
            control_frame,
            textvariable=display_mode,
            state="readonly",
            values=[
                "Atoms",
                "Bonds",
                "Both",
                "None",
            ],
        )

        label_box.pack(
            fill="x",
            pady=(0, 15),
        )

        label_box.bind(
            "<<ComboboxSelected>>",
            lambda event: render(),
        )

        ttk.Button(
            control_frame,
            text="Atom Map",
            command=lambda:
                self.show_atom_map(
                    mol
                ),
        ).pack(
            fill="x",
            pady=2,
        )

        ttk.Button(
            control_frame,
            text="Bond Map",
            command=lambda:
                self.show_bond_map(
                    mol
                ),
        ).pack(
            fill="x",
            pady=2,
        )

        ttk.Separator(
            control_frame,
            orient="horizontal",
        ).pack(
            fill="x",
            pady=10,
        )

        ttk.Label(
            control_frame,
            text="SAR Operation",
        ).pack(
            anchor="w"
        )

        operation_box = ttk.Combobox(
            control_frame,
            textvariable=operation,
            state="readonly",
            values=[
                "Link atoms",
                "Insert into bond",
                "Replace atom",
                "Delete atom",
                "Delete functional group",
            ],
        )

        operation_box.pack(
            fill="x"
        )

        ttk.Label(
            control_frame,
            textvariable=instruction,
            justify="left",
            wraplength=390,
        ).pack(
            fill="x",
            pady=10,
        )

        inputs = ttk.Frame(
            control_frame
        )

        inputs.pack(
            fill="x"
        )

        inputs.columnconfigure(
            1,
            weight=1,
        )

        atom_a_label = ttk.Label(
            inputs,
            text="Atom A",
        )

        atom_a_entry = ttk.Entry(
            inputs,
            textvariable=atom_a,
        )

        atom_b_label = ttk.Label(
            inputs,
            text="Atom B",
        )

        atom_b_entry = ttk.Entry(
            inputs,
            textvariable=atom_b,
        )

        bond_label = ttk.Label(
            inputs,
            text="Bond Number",
        )

        bond_entry = ttk.Entry(
            inputs,
            textvariable=bond_number,
        )

        keep_label = ttk.Label(
            inputs,
            text="Keep Atom",
        )

        keep_entry = ttk.Entry(
            inputs,
            textvariable=keep_atom,
        )

        library_label = ttk.Label(
            inputs,
            text="Library",
        )

        library_box = ttk.Combobox(
            inputs,
            textvariable=library,
            state="readonly",
        )

        all_widgets = [

            atom_a_label,
            atom_a_entry,

            atom_b_label,
            atom_b_entry,

            bond_label,
            bond_entry,

            keep_label,
            keep_entry,

            library_label,
            library_box,
        ]

        def hide_all():

            for widget in all_widgets:

                widget.grid_forget()

        def show(
            row,
            label,
            entry,
        ):

            label.grid(
                row=row,
                column=0,
                sticky="w",
                pady=5,
            )

            entry.grid(
                row=row,
                column=1,
                sticky="ew",
                pady=5,
            )

        def update_operation(
            *args
        ):

            hide_all()

            op = operation.get()

            if op == "Link atoms":

                instruction.set(
                    "Required inputs:\n\n"
                    "• Atom A\n"
                    "• Atom B\n"
                    "• Linker Library\n\n"
                    "The selected atoms must currently "
                    "be connected by a bond. That bond "
                    "will be replaced with the linker."
                )

                show(
                    0,
                    atom_a_label,
                    atom_a_entry,
                )

                show(
                    1,
                    atom_b_label,
                    atom_b_entry,
                )

                library_box[
                    "values"
                ] = list(
                    LINKER_LIBRARIES.keys()
                )

                if (
                    LINKER_LIBRARIES
                ):

                    library.set(
                        list(
                            LINKER_LIBRARIES.keys()
                        )[0]
                    )

                show(
                    2,
                    library_label,
                    library_box,
                )

            elif op == "Insert into bond":

                instruction.set(
                    "Required inputs:\n\n"
                    "• Bond Number\n"
                    "• Linker Library\n\n"
                    "The selected bond will be broken "
                    "and replaced by the linker. "
                    "This can be used for aryl–aryl "
                    "bond modification."
                )

                show(
                    0,
                    bond_label,
                    bond_entry,
                )

                library_box[
                    "values"
                ] = list(
                    LINKER_LIBRARIES.keys()
                )

                if (
                    LINKER_LIBRARIES
                ):

                    library.set(
                        list(
                            LINKER_LIBRARIES.keys()
                        )[0]
                    )

                show(
                    1,
                    library_label,
                    library_box,
                )

            elif op == "Replace atom":

                instruction.set(
                    "Required inputs:\n\n"
                    "• Atom Number\n"
                    "• Replacement Library\n\n"
                    "The selected atom is replaced "
                    "with each element in the selected "
                    "library. Products that cannot be "
                    "sanitized are discarded."
                )

                show(
                    0,
                    atom_a_label,
                    atom_a_entry,
                )

                library_box[
                    "values"
                ] = list(
                    REPLACEMENT_LIBRARIES.keys()
                )

                if (
                    REPLACEMENT_LIBRARIES
                ):

                    library.set(
                        list(
                            REPLACEMENT_LIBRARIES.keys()
                        )[0]
                    )

                show(
                    1,
                    library_label,
                    library_box,
                )

            elif op == "Delete atom":

                instruction.set(
                    "Required input:\n\n"
                    "• Atom Number\n\n"
                    "The selected atom is removed. "
                    "The resulting molecule must "
                    "remain chemically valid."
                )

                show(
                    0,
                    atom_a_label,
                    atom_a_entry,
                )

            elif op == "Delete functional group":

                instruction.set(
                    "Required inputs:\n\n"
                    "• Bond Number\n"
                    "• Keep Atom\n\n"
                    "The selected bond is treated as "
                    "the attachment point. The molecular "
                    "fragment containing Keep Atom is "
                    "retained and the opposite fragment "
                    "is removed."
                )

                show(
                    0,
                    bond_label,
                    bond_entry,
                )

                show(
                    1,
                    keep_label,
                    keep_entry,
                )

        operation.trace_add(
            "write",
            update_operation,
        )

        update_operation()

        def generate():

            try:

                op = operation.get()

                if op == "Link atoms":

                    products = linker_library(
                        mol,
                        int(
                            atom_a.get()
                        ),
                        int(
                            atom_b.get()
                        ),
                        library.get(),
                    )

                elif op == "Insert into bond":

                    products = bond_linker_library(
                        mol,
                        int(
                            bond_number.get()
                        ),
                        library.get(),
                    )

                elif op == "Replace atom":

                    products = replacement_library(
                        mol,
                        int(
                            atom_a.get()
                        ),
                        library.get(),
                    )

                elif op == "Delete atom":

                    product = delete_atom(
                        mol,
                        int(
                            atom_a.get()
                        ),
                    )

                    products = []

                    if product is not None:

                        products.append(
                            (
                                "deleted",
                                product,
                            )
                        )

                elif op == "Delete functional group":

                    product = (
                        delete_functional_group(
                            mol,
                            int(
                                bond_number.get()
                            ),
                            int(
                                keep_atom.get()
                            ),
                        )
                    )

                    products = []

                    if product is not None:

                        products.append(
                            (
                                "deleted_group",
                                product,
                            )
                        )

                else:

                    raise ValueError(
                        "Unknown SAR operation."
                    )

                if not products:

                    raise ValueError(
                        "No valid products were generated."
                    )

                ids = (
                    self.project.add_sar_products(
                        self.current_id,
                        products,
                        op,
                    )
                )

                self.refresh_table()

                self.status.set(
                    f"Generated {len(ids)} "
                    "SAR derivative(s)."
                )

                window.destroy()

            except Exception as exc:

                messagebox.showerror(
                    "SAR Error",
                    str(exc),
                )

        ttk.Button(
            control_frame,
            text="Generate and Add Derivatives",
            command=generate,
        ).pack(
            fill="x",
            pady=20,
        )

        render()

    # ============================================================
    # DOCKING CONFIGURATION
    # ============================================================

    def configure_docking(self):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Docking Configuration"
        )

        window.geometry(
            "900x750"
        )

        global_frame = ttk.LabelFrame(
            window,
            text="Reusable Global Configurations",
            padding=10,
        )

        global_frame.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        selected_config = tk.StringVar()

        config_box = ttk.Combobox(
            global_frame,
            textvariable=selected_config,
            values=self.global_docking_configs.names(),
            state="readonly",
        )

        config_box.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
        )

        form = ttk.Frame(
            window,
            padding=10,
        )

        form.pack(
            fill="both",
            expand=True,
        )

        form.columnconfigure(
            1,
            weight=1,
        )

        flexible = tk.BooleanVar(
            value=bool(
                self.project.active_config.get(
                    "flexible",
                    False,
                )
            )
        )

        ttk.Checkbutton(
            form,
            text="Enable Flexible Receptor Docking",
            variable=flexible,
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=5,
        )

        field_names = [

            "name",

            "receptor",

            "flex_receptor",

            "center_x",

            "center_y",

            "center_z",

            "size_x",

            "size_y",

            "size_z",

            "exhaustiveness",

            "poses",

            "vina",

            "obabel",
        ]

        defaults = {

            "name": "Project Configuration",

            "receptor": "",

            "flex_receptor": "",

            "center_x": "",

            "center_y": "",

            "center_z": "",

            "size_x": "",

            "size_y": "",

            "size_z": "",

            "exhaustiveness": 32,

            "poses": 5,

            "vina": "vina",

            "obabel": "obabel",
        }

        variables = {}

        def browse_pdbqt(
            variable
        ):

            filename = (
                filedialog.askopenfilename(
                    title="Select PDBQT File",
                    filetypes=[
                        (
                            "PDBQT files",
                            "*.pdbqt",
                        ),

                        (
                            "All files",
                            "*.*",
                        ),
                    ],
                )
            )

            if filename:

                variable.set(
                    filename
                )

        row = 1

        for field in field_names:

            ttk.Label(
                form,
                text=field.replace(
                    "_",
                    " "
                ).title(),
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=4,
            )

            value = (
                self.project.active_config.get(
                    field,
                    defaults[field],
                )
            )

            variable = tk.StringVar(
                value=str(value)
            )

            variables[field] = variable

            entry = ttk.Entry(
                form,
                textvariable=variable,
                width=65,
            )

            entry.grid(
                row=row,
                column=1,
                sticky="ew",
                padx=5,
                pady=4,
            )

            if field in [
                "receptor",
                "flex_receptor",
            ]:

                ttk.Button(
                    form,
                    text="Browse",
                    command=lambda v=variable:
                        browse_pdbqt(v),
                ).grid(
                    row=row,
                    column=2,
                    padx=5,
                )

            row += 1

        ttk.Label(
            window,
            text=(
                "Docking receptor files should normally "
                "be AutoDock PDBQT files.\n"
                "Rigid receptor: receptor.pdbqt\n"
                "Flexible receptor: flexible_residues.pdbqt"
            ),
            justify="left",
        ).pack(
            anchor="w",
            padx=20,
            pady=5,
        )

        def get_configuration():

            configuration = {}

            for field, variable in (
                variables.items()
            ):

                configuration[
                    field
                ] = variable.get()

            for field in [

                "center_x",

                "center_y",

                "center_z",

                "size_x",

                "size_y",

                "size_z",
            ]:

                configuration[
                    field
                ] = float(
                    configuration[field]
                )

            configuration[
                "exhaustiveness"
            ] = int(
                configuration[
                    "exhaustiveness"
                ]
            )

            configuration[
                "poses"
            ] = int(
                configuration[
                    "poses"
                ]
            )

            configuration[
                "flexible"
            ] = flexible.get()

            return configuration

        def apply_configuration(
            configuration
        ):

            for key, value in (
                configuration.items()
            ):

                if key == "flexible":

                    flexible.set(
                        bool(value)
                    )

                elif key in variables:

                    variables[key].set(
                        str(value)
                    )

        def load_global():

            name = selected_config.get()

            if not name:

                return

            configuration = (
                self.global_docking_configs.get(
                    name
                )
            )

            apply_configuration(
                configuration
            )

        def save_project():

            try:

                self.project.active_config = (
                    get_configuration()
                )

                self.project.save()

                self.status.set(
                    "Project docking configuration saved."
                )

            except Exception as exc:

                messagebox.showerror(
                    "Configuration Error",
                    str(exc),
                )

        def save_global():

            try:

                configuration = (
                    get_configuration()
                )

                name = (
                    configuration.get(
                        "name",
                        ""
                    )
                )

                if not name:

                    name = simpledialog.askstring(
                        "Configuration Name",
                        "Enter a configuration name:",
                        parent=window,
                    )

                self.global_docking_configs.add(
                    name,
                    configuration,
                )

                config_box[
                    "values"
                ] = (
                    self.global_docking_configs.names()
                )

                selected_config.set(
                    name
                )

            except Exception as exc:

                messagebox.showerror(
                    "Configuration Error",
                    str(exc),
                )

        def delete_global():

            name = selected_config.get()

            if not name:

                return

            if messagebox.askyesno(
                "Delete Configuration",
                f"Delete '{name}'?"
            ):

                self.global_docking_configs.delete(
                    name
                )

                config_box[
                    "values"
                ] = (
                    self.global_docking_configs.names()
                )

                selected_config.set(
                    ""
                )

        buttons = ttk.Frame(
            window,
            padding=10,
        )

        buttons.pack(
            fill="x"
        )

        ttk.Button(
            buttons,
            text="Load Global",
            command=load_global,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            buttons,
            text="Save Project",
            command=save_project,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            buttons,
            text="Save Global",
            command=save_global,
        ).pack(
            side="left",
            padx=3,
        )

        ttk.Button(
            buttons,
            text="Delete Global",
            command=delete_global,
        ).pack(
            side="left",
            padx=3,
        )

    # ============================================================
    # v3.4 EXPERIMENTAL DATA
    # ============================================================

    def _calculate_pactivity(self, value, unit):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return None
        if value <= 0:
            return None
        factors = {
            "pM": 1e-12,
            "nM": 1e-9,
            "uM": 1e-6,
            "µM": 1e-6,
            "mM": 1e-3,
            "M": 1.0,
        }
        factor = factors.get(unit)
        if factor is None:
            return None
        return -math.log10(value * factor)

    def _activity_values(self, compound):
        activity_type = compound.get("activity_type", "IC50")
        raw_value = compound.get("activity_value", "")
        unit = compound.get("activity_unit", "nM")
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            value = None
        pactivity = (
            self._calculate_pactivity(value, unit)
            if value is not None else None
        )
        return activity_type, value, unit, pactivity

    def edit_experimental_data(self):
        if not self.require_selection():
            return

        compound = self.project.compounds[self.current_id]

        window = tk.Toplevel(self.root)
        window.title("Experimental Activity Data")
        window.geometry("650x500")

        ttk.Label(
            window,
            text=f"Compound: {compound.get('name', self.current_id)}",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(anchor="w", padx=15, pady=15)

        form = ttk.Frame(window, padding=15)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        activity_type = tk.StringVar(
            value=compound.get("activity_type", "IC50")
        )
        activity_value = tk.StringVar(
            value=str(compound.get("activity_value", ""))
        )
        activity_unit = tk.StringVar(
            value=compound.get("activity_unit", "nM")
        )
        pactivity = tk.StringVar()

        ttk.Label(form, text="Measurement:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        ttk.Combobox(
            form,
            textvariable=activity_type,
            values=["IC50", "EC50", "Ki", "Kd", "Other"],
            state="readonly",
        ).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="Value:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        ttk.Entry(
            form,
            textvariable=activity_value,
        ).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="Units:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        ttk.Combobox(
            form,
            textvariable=activity_unit,
            values=["pM", "nM", "uM", "µM", "mM", "M"],
            state="readonly",
        ).grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(form, text="pActivity:").grid(
            row=3, column=0, sticky="w", pady=5
        )
        ttk.Label(
            form,
            textvariable=pactivity,
        ).grid(row=3, column=1, sticky="w", pady=5)

        def update_pactivity(*args):
            result = self._calculate_pactivity(
                activity_value.get(),
                activity_unit.get(),
            )
            pactivity.set(
                "" if result is None else f"{result:.3f}"
            )

        activity_value.trace_add("write", update_pactivity)
        activity_unit.trace_add("write", update_pactivity)
        update_pactivity()

        ttk.Label(window, text="Notes:").pack(
            anchor="w", padx=15, pady=(10, 3)
        )
        notes = tk.Text(window, height=8, width=70)
        notes.pack(fill="both", expand=True, padx=15)
        notes.insert("1.0", compound.get("notes", ""))

        def save():
            raw = activity_value.get().strip()
            if raw:
                try:
                    value = float(raw)
                    if value <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror(
                        "Invalid Activity",
                        "Activity must be a positive numerical value.",
                        parent=window,
                    )
                    return
            else:
                value = ""

            if hasattr(self.project, "update_activity"):
                self.project.update_activity(
                    self.current_id,
                    activity_type.get(),
                    value,
                    activity_unit.get(),
                    notes.get("1.0", "end").strip(),
                )
            else:
                compound["activity_type"] = activity_type.get()
                compound["activity_value"] = value
                compound["activity_unit"] = activity_unit.get()
                compound["notes"] = notes.get("1.0", "end").strip()
                self.project.save()

            window.destroy()
            self.refresh_table()
            self.status.set("Experimental data saved.")

        ttk.Button(
            window,
            text="Save",
            command=save,
        ).pack(anchor="e", padx=15, pady=15)

    # ============================================================
    # v3.4 ANALYSIS
    # ============================================================

    def _analysis_rows(self):
        rows = []
        targets = self.project.docking_targets()
        for compound_id, compound in self.project.compounds.items():
            props = compound.get("properties", {})
            _, activity_value, _, pactivity = self._activity_values(compound)
            scores = []
            for target in targets:
                score = self.project.get_docking_score(compound_id, target)
                if score is not None:
                    try:
                        scores.append(float(score))
                    except (TypeError, ValueError):
                        pass
            rows.append({
                "Name": compound.get("name", compound_id),
                "MW": self._numeric(props.get("MW")),
                "LogP": self._numeric(props.get("LogP", props.get("cLogP"))),
                "TPSA": self._numeric(props.get("TPSA")),
                "HBD": self._numeric(props.get("HBD")),
                "HBA": self._numeric(props.get("HBA")),
                "RotB": self._numeric(props.get("RotB")),
                "Rings": self._numeric(props.get("Rings")),
                "Docking Score": min(scores) if scores else None,
                "Activity": activity_value,
                "pActivity": pactivity,
            })
        return rows

    def _numeric(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def open_analysis_window(self):
        if Figure is None or FigureCanvasTkAgg is None:
            messagebox.showerror(
                "Analysis",
                "Install matplotlib with: pip install matplotlib",
            )
            return

        rows = self._analysis_rows()
        if len(rows) < 2:
            messagebox.showwarning(
                "Analysis",
                "At least two compounds are required.",
            )
            return

        window = tk.Toplevel(self.root)
        window.title("AutoSAR Dock Analysis")
        window.geometry("1000x800")

        fields = [
            "MW", "LogP", "TPSA", "HBD", "HBA",
            "RotB", "Rings", "Docking Score",
            "Activity", "pActivity",
        ]

        x_axis = tk.StringVar(value="Docking Score")
        y_axis = tk.StringVar(value="pActivity")

        controls = ttk.Frame(window, padding=10)
        controls.pack(fill="x")

        ttk.Label(controls, text="X Axis:").pack(side="left")
        ttk.Combobox(
            controls,
            textvariable=x_axis,
            values=fields,
            state="readonly",
            width=20,
        ).pack(side="left", padx=5)

        ttk.Label(controls, text="Y Axis:").pack(side="left", padx=(15, 0))
        ttk.Combobox(
            controls,
            textvariable=y_axis,
            values=fields,
            state="readonly",
            width=20,
        ).pack(side="left", padx=5)

        result_label = ttk.Label(window, text="")
        result_label.pack(pady=5)

        plot_frame = ttk.Frame(window)
        plot_frame.pack(fill="both", expand=True)

        canvas_holder = {"canvas": None}

        def generate():
            pairs = []
            for row in rows:
                x = row.get(x_axis.get())
                y = row.get(y_axis.get())
                if x is not None and y is not None:
                    pairs.append((x, y))

            if len(pairs) < 2:
                messagebox.showwarning(
                    "Analysis",
                    "At least two compounds need valid values for both variables.",
                    parent=window,
                )
                return

            xs = [p[0] for p in pairs]
            ys = [p[1] for p in pairs]

            figure = Figure(figsize=(8, 5), dpi=100)
            axis = figure.add_subplot(111)
            axis.scatter(xs, ys)
            axis.set_xlabel(x_axis.get())
            axis.set_ylabel(y_axis.get())
            axis.set_title(f"{y_axis.get()} vs {x_axis.get()}")
            figure.tight_layout()

            old = canvas_holder["canvas"]
            if old is not None:
                old.get_tk_widget().destroy()

            canvas = FigureCanvasTkAgg(figure, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas_holder["canvas"] = canvas

            try:
                import numpy as np
                r = float(np.corrcoef(xs, ys)[0, 1])
                result_label.config(
                    text=f"Pearson r = {r:.3f}    n = {len(pairs)}"
                )
            except Exception:
                result_label.config(text=f"n = {len(pairs)}")

        ttk.Button(
            controls,
            text="Generate Plot",
            command=generate,
        ).pack(side="left", padx=15)

        generate()

    # ============================================================
    # v3.4 CSV / EXCEL EXPORT
    # ============================================================

    def export_rows(self):
        rows = []
        targets = self.project.docking_targets()

        for compound_id, compound in self.project.compounds.items():
            props = compound.get("properties", {})
            activity_type, activity_value, activity_unit, pactivity = self._activity_values(compound)

            row = {
                "ID": compound_id,
                "Name": compound.get("name", compound_id),
                "Parent": compound.get("parent_id", ""),
                "Generation": compound.get("generation", ""),
                "SAR Operation": compound.get("sar_operation", ""),
                "SMILES": compound.get("smiles", ""),
                "MW": props.get("MW", ""),
                "LogP": props.get("LogP", props.get("cLogP", "")),
                "TPSA": props.get("TPSA", ""),
                "HBD": props.get("HBD", ""),
                "HBA": props.get("HBA", ""),
                "RotB": props.get("RotB", ""),
                "Rings": props.get("Rings", ""),
                "Activity Type": activity_type if activity_value is not None else "",
                "Activity": activity_value if activity_value is not None else "",
                "Activity Units": activity_unit if activity_value is not None else "",
                "pActivity": pactivity if pactivity is not None else "",
                "Notes": compound.get("notes", ""),
            }

            for target in targets:
                score = self.project.get_docking_score(
                    compound_id,
                    target,
                )
                row[target] = "" if score is None else score

            rows.append(row)

        return rows

    def export_csv(self):
        if not self.project.compounds:
            messagebox.showwarning(
                "CSV Export",
                "There are no compounds to export.",
            )
            return

        filename = filedialog.asksaveasfilename(
            title="Export AutoSAR Dock CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )

        if not filename:
            return

        try:
            rows = self.export_rows()
            columns = list(rows[0].keys()) if rows else []

            import csv

            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8",
            ) as handle:

                writer = csv.DictWriter(
                    handle,
                    fieldnames=columns,
                )

                writer.writeheader()
                writer.writerows(rows)

            self.status.set(
                f"CSV exported: {filename}"
            )

        except Exception as exc:

            messagebox.showerror(
                "CSV Export Error",
                str(exc),
            )

    def export_excel(self):
        if pd is None:
            messagebox.showerror(
                "Excel Export",
                "Install pandas and openpyxl with: pip install pandas openpyxl",
            )
            return

        if not self.project.compounds:
            messagebox.showwarning(
                "Excel Export",
                "There are no compounds to export.",
            )
            return

        filename = filedialog.asksaveasfilename(
            title="Export AutoSAR Dock Excel Workbook",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx")],
        )

        if not filename:
            return

        try:
            compound_frame = pd.DataFrame(
                self.export_rows()
            )

            docking_rows = []

            for compound_id, compound in self.project.compounds.items():

                results = compound.get(
                    "docking_results",
                    [],
                )

                if isinstance(results, dict):
                    results = [
                        dict(
                            value,
                            target_name=target,
                        )
                        for target, value in results.items()
                    ]

                for result in results:

                    poses = result.get(
                        "poses",
                        [],
                    )

                    if not poses:
                        poses = [
                            {
                                "rank": 1,
                                "score": result.get("score"),
                            }
                        ]

                    for pose in poses:
                        docking_rows.append({
                            "Compound ID": compound_id,
                            "Compound": compound.get(
                                "name",
                                compound_id,
                            ),
                            "Target": result.get(
                                "target_name",
                                "",
                            ),
                            "Pose": pose.get(
                                "rank",
                                "",
                            ),
                            "Score": pose.get(
                                "score",
                                "",
                            ),
                            "Best Pose": result.get(
                                "best_pose",
                                "",
                            ),
                            "Pose File": result.get(
                                "poses_file",
                                "",
                            ),
                            "Log File": result.get(
                                "log_file",
                                "",
                            ),
                        })

            docking_frame = pd.DataFrame(
                docking_rows
            )

            config_frame = pd.DataFrame(
                list(
                    self.available_docking_configs().values()
                )
            )

            with pd.ExcelWriter(
                filename,
                engine="openpyxl",
            ) as writer:

                compound_frame.to_excel(
                    writer,
                    sheet_name="Compounds",
                    index=False,
                )

                docking_frame.to_excel(
                    writer,
                    sheet_name="Docking Results",
                    index=False,
                )

                if not config_frame.empty:

                    config_frame.to_excel(
                        writer,
                        sheet_name="Docking Configs",
                        index=False,
                    )

            self.status.set(
                f"Excel exported: {filename}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Excel Export Error",
                str(exc),
            )

    # ============================================================
    # v3.4 CONDA / PyMOL INTEGRATION
    # ============================================================

    def _detect_conda_pymol(self):
        """Return the PyMOL executable from the active conda/WSL environment."""
        import shutil

        pymol = shutil.which("pymol")

        if pymol:
            return pymol

        conda_prefix = os.environ.get("CONDA_PREFIX")

        if conda_prefix:
            candidate = Path(conda_prefix) / "bin" / "pymol"
            if candidate.exists() and os.access(candidate, os.X_OK):
                return str(candidate)

        return ""

    def _get_pymol_path(self):
        configured = ""

        if hasattr(self.project, "settings"):
            configured = self.project.settings.get("pymol_path", "") or ""

        # Prefer an explicitly configured executable if it still exists.
        if configured:
            configured_path = Path(configured).expanduser()
            if configured_path.exists() or configured_path.name == "pymol":
                return str(configured_path)

        detected = self._detect_conda_pymol()

        return detected

    def configure_pymol(self):
        """
        Configure PyMOL.

        AutoSAR Dock first detects PyMOL from the active conda
        environment. Manual selection is available as a fallback.
        """

        detected = self._detect_conda_pymol()

        if detected:
            use_detected = messagebox.askyesno(
                "PyMOL Detected",
                "AutoSAR Dock detected PyMOL in the current environment:\n\n"
                f"{detected}\n\n"
                "Use this PyMOL executable?",
            )

            if use_detected:
                self.project.set_pymol_path(detected)
                self.status.set(
                    f"PyMOL configured from conda: {detected}"
                )
                return

        filename = filedialog.askopenfilename(
            title="Select PyMOL Executable",
            filetypes=[
                ("All files", "*.*"),
            ],
        )

        if not filename:
            return

        self.project.set_pymol_path(filename)

        self.status.set(
            f"PyMOL configured: {filename}"
        )

    # ============================================================
    # POSE DATA HELPERS
    # ============================================================

    def _get_pose_scores(self, compound_id, target_name):
        """Return all stored pose scores, with backward compatibility."""

        if hasattr(self.project, "get_pose_scores"):
            return self.project.get_pose_scores(
                compound_id,
                target_name,
            )

        result = self.project.get_docking_result(
            compound_id,
            target_name,
        )

        if not result:
            return []

        poses = result.get("poses", [])

        if poses:
            return sorted(
                poses,
                key=lambda x: int(x.get("rank", 0)),
            )

        score = result.get("score")

        if score is None:
            return []

        try:
            return [{
                "rank": 1,
                "score": float(score),
            }]
        except (TypeError, ValueError):
            return []

    def _extract_pose_file(self, poses_file, pose_number):
        """Extract an individual MODEL from a Vina multi-pose PDBQT."""

        poses_file = Path(poses_file)

        if not poses_file.exists():
            raise FileNotFoundError(
                f"Pose file does not exist:\n{poses_file}"
            )

        models = []
        current = []
        current_number = None
        inside = False

        with open(
            poses_file,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as handle:

            for line in handle:
                stripped = line.strip()

                if stripped.startswith("MODEL"):
                    inside = True
                    current = [line]
                    parts = stripped.split()

                    try:
                        current_number = int(parts[1])
                    except (IndexError, ValueError):
                        current_number = len(models) + 1

                elif stripped.startswith("ENDMDL") and inside:
                    current.append(line)
                    models.append(
                        (current_number, list(current))
                    )
                    current = []
                    current_number = None
                    inside = False

                elif inside:
                    current.append(line)

        if not models:
            if int(pose_number) == 1:
                return str(poses_file)
            return None

        selected = None

        for number, lines in models:
            if int(number) == int(pose_number):
                selected = lines
                break

        if selected is None:
            return None

        output_file = (
            poses_file.parent
            / f"{poses_file.stem}_pose_{int(pose_number)}.pdbqt"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as handle:
            handle.writelines(selected)

        return str(output_file)

    # ============================================================
    # POSE SCORE WINDOW
    # ============================================================

    def show_pose_scores(self):
        """Display all stored poses for the selected compound."""

        if not self.require_selection():
            return

        compound_id = self.current_id

        targets = []

        for target in self.project.docking_targets():
            result = self.project.get_docking_result(
                compound_id,
                target,
            )

            if result is not None:
                targets.append(target)

        if not targets:
            messagebox.showwarning(
                "No Docking Results",
                "The selected compound has no docking results.",
            )
            return

        if len(targets) == 1:
            self._open_pose_score_window(
                compound_id,
                targets[0],
            )
            return

        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Docking Target")
        selection_window.geometry("500x250")

        ttk.Label(
            selection_window,
            text="Select the docking target to inspect:",
        ).pack(
            anchor="w",
            padx=15,
            pady=15,
        )

        target_var = tk.StringVar(value=targets[0])

        ttk.Combobox(
            selection_window,
            textvariable=target_var,
            values=targets,
            state="readonly",
            width=50,
        ).pack(
            padx=15,
            pady=10,
        )

        def continue_to_scores():
            target = target_var.get()
            selection_window.destroy()
            self._open_pose_score_window(
                compound_id,
                target,
            )

        ttk.Button(
            selection_window,
            text="Show Pose Scores",
            command=continue_to_scores,
        ).pack(
            pady=15,
        )

    def _open_pose_score_window(
        self,
        compound_id,
        target_name,
    ):

        poses = self._get_pose_scores(
            compound_id,
            target_name,
        )

        if not poses:
            messagebox.showwarning(
                "No Pose Data",
                "No individual pose scores are available for this docking result.",
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Docking Pose Scores")
        window.geometry("700x550")

        ttk.Label(
            window,
            text=(
                f"Compound: {self.compound_name(compound_id)}\n"
                f"Target: {target_name}"
            ),
            justify="left",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=15,
        )

        columns = (
            "Pose",
            "Score",
            "Delta Best",
        )

        tree = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        for column in columns:
            tree.heading(
                column,
                text=column,
            )
            tree.column(
                column,
                width=180,
                anchor="center",
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10,
        )

        best_score = min(
            float(pose["score"])
            for pose in poses
        )

        pose_lookup = {}

        for pose in poses:
            rank = int(pose["rank"])
            score = float(pose["score"])
            delta = score - best_score
            iid = str(rank)

            tree.insert(
                "",
                "end",
                iid=iid,
                values=(
                    rank,
                    f"{score:.3f}",
                    f"{delta:+.3f}",
                ),
            )

            pose_lookup[iid] = pose

        def open_selected():
            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "No Pose Selected",
                    "Select a pose first.",
                    parent=window,
                )
                return

            pose = pose_lookup[selected[0]]

            window.destroy()

            self.view_specific_pose(
                compound_id,
                target_name,
                int(pose["rank"]),
            )

        def double_click(event=None):
            open_selected()

        tree.bind(
            "<Double-1>",
            double_click,
        )

        buttons = ttk.Frame(window)
        buttons.pack(
            fill="x",
            padx=15,
            pady=10,
        )

        ttk.Button(
            buttons,
            text="View Selected Pose",
            command=open_selected,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buttons,
            text="Cycle Poses",
            command=lambda:
                self.pose_navigation_window(
                    compound_id,
                    target_name,
                ),
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buttons,
            text="Close",
            command=window.destroy,
        ).pack(
            side="right",
            padx=5,
        )

    # ============================================================
    # POSE NAVIGATION
    # ============================================================

    def pose_navigation_window(
        self,
        compound_id,
        target_name,
    ):

        poses = self._get_pose_scores(
            compound_id,
            target_name,
        )

        if not poses:
            return

        ranks = [
            int(pose["rank"])
            for pose in poses
        ]

        current = tk.IntVar(
            value=ranks[0]
        )

        window = tk.Toplevel(self.root)
        window.title("Pose Navigation")
        window.geometry("620x360")

        ttk.Label(
            window,
            text=(
                f"{self.compound_name(compound_id)}\n"
                f"{target_name}"
            ),
            justify="center",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(
            fill="x",
            pady=20,
        )

        pose_text = tk.StringVar()

        ttk.Label(
            window,
            textvariable=pose_text,
            justify="center",
            font=("TkDefaultFont", 13),
        ).pack(
            pady=15,
        )

        def get_index():
            try:
                return ranks.index(
                    current.get()
                )
            except ValueError:
                current.set(ranks[0])
                return 0

        def update():
            rank = current.get()

            pose = next(
                (
                    pose
                    for pose in poses
                    if int(pose["rank"]) == rank
                ),
                None,
            )

            if pose is None:
                return

            score = float(
                pose["score"]
            )

            best = min(
                float(p["score"])
                for p in poses
            )

            pose_text.set(
                f"Pose {rank} of {len(poses)}\n\n"
                f"Vina score: {score:.3f} kcal/mol\n"
                f"Delta to best: {score - best:+.3f} kcal/mol"
            )

        def previous():
            index = get_index()

            if index > 0:
                current.set(
                    ranks[index - 1]
                )
                update()

        def next_pose():
            index = get_index()

            if index < len(ranks) - 1:
                current.set(
                    ranks[index + 1]
                )
                update()

        def open_pose():
            self.view_specific_pose(
                compound_id,
                target_name,
                current.get(),
            )

        buttons = ttk.Frame(window)
        buttons.pack(pady=15)

        ttk.Button(
            buttons,
            text="Previous Pose",
            command=previous,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buttons,
            text="Next Pose",
            command=next_pose,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            buttons,
            text="View in PyMOL",
            command=open_pose,
        ).pack(
            side="left",
            padx=5,
        )

        ttk.Button(
            window,
            text="Close",
            command=window.destroy,
        ).pack(
            pady=10,
        )

        window.bind(
            "<Left>",
            lambda event: previous(),
        )

        window.bind(
            "<Right>",
            lambda event: next_pose(),
        )

        window.focus_force()
        update()

    # ============================================================
    # SPECIFIC POSE / PyMOL
    # ============================================================

    def view_selected_pose(self):
        """Open the pose-score selector for the current compound."""
        if not self.require_selection():
            return

        self.show_pose_scores()

    def view_specific_pose(
        self,
        compound_id,
        target_name,
        pose_number,
    ):

        result = self.project.get_docking_result(
            compound_id,
            target_name,
        )

        if result is None:
            messagebox.showerror(
                "Pose Error",
                "Docking result was not found.",
            )
            return

        poses_file = result.get(
            "poses_file"
        )

        if not poses_file:
            messagebox.showerror(
                "Pose Error",
                "No pose file is associated with this docking result.",
            )
            return

        try:
            pose_file = self._extract_pose_file(
                poses_file,
                pose_number,
            )

        except Exception as exc:
            messagebox.showerror(
                "Pose Extraction Error",
                str(exc),
            )
            return

        if not pose_file:
            messagebox.showerror(
                "Pose Error",
                f"Pose {pose_number} could not be extracted.",
            )
            return

        configurations = self.available_docking_configs()

        config = configurations.get(
            target_name
        )

        if config is None:
            messagebox.showerror(
                "Configuration Error",
                (
                    f"Docking configuration '{target_name}' "
                    "could not be found."
                ),
            )
            return

        receptor = config.get(
            "receptor"
        )

        if not receptor:
            messagebox.showerror(
                "Configuration Error",
                "No rigid receptor is associated with this target.",
            )
            return

        flexible_receptor = None

        if config.get(
            "flexible",
            False,
        ):
            flexible_receptor = config.get(
                "flex_receptor"
            )

        pymol = self._get_pymol_path()

        if not pymol:
            messagebox.showerror(
                "PyMOL",
                (
                    "PyMOL could not be found in the current conda environment.\n\n"
                    "Activate the environment containing PyMOL and verify with:\n"
                    "which pymol"
                ),
            )
            return

        script_file = Path(pose_file).with_name(
            f"{Path(pose_file).stem}_view.pml"
        )

        def quote_path(path):
            return str(path).replace(
                "\\",
                "/",
            ).replace(
                "'",
                "\\'",
            )

        script_lines = [
            "reinitialize",
            f"load '{quote_path(receptor)}', receptor",
        ]

        if flexible_receptor:
            script_lines.append(
                f"load '{quote_path(flexible_receptor)}', flexible_receptor"
            )
            script_lines.append(
                "show sticks, flexible_receptor"
            )

        script_lines.extend([
            f"load '{quote_path(pose_file)}', ligand",
            "hide everything, all",
            "show cartoon, receptor",
            "show sticks, ligand",
            "set stick_radius, 0.18, ligand",
            "zoom ligand, 10",
            "bg_color white",
        ])

        script_file.write_text(
            "\n".join(script_lines),
            encoding="utf-8",
        )

        try:
            subprocess.Popen(
                [
                    pymol,
                    str(script_file),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            self.status.set(
                f"Opened pose {pose_number} in PyMOL."
            )

        except Exception as exc:
            messagebox.showerror(
                "PyMOL Error",
                str(exc),
            )

    # ============================================================
    # v3.4 DOCKING TARGETS / CAMPAIGNS
    # ============================================================

    def available_docking_configs(self):

        configurations = {}

        if self.project.active_config:

            config = dict(
                self.project.active_config
            )

            name = (
                config.get("name")
                or config.get("target_name")
                or "Project Configuration"
            )

            configurations[name] = config

        for name in self.global_docking_configs.names():

            try:
                configurations[name] = (
                    self.global_docking_configs.get(name)
                )
            except Exception:
                pass

        for config in getattr(
            self.project,
            "docking_configs",
            [],
        ):

            name = (
                config.get("name")
                or config.get("target_name")
                or "Project Configuration"
            )

            configurations[name] = dict(config)

        return configurations

    def open_docking_campaign_window(self):

        configurations = self.available_docking_configs()

        if not configurations:

            messagebox.showwarning(
                "No Docking Configurations",
                "Create or load a docking configuration first.",
            )

            return

        window = tk.Toplevel(self.root)
        window.title("Docking Campaign")
        window.geometry("800x650")

        ttk.Label(
            window,
            text=(
                "Select one or more docking targets. Each compound "
                "is tracked independently for each target."
            ),
            wraplength=740,
        ).pack(
            anchor="w",
            padx=15,
            pady=15,
        )

        target_frame = ttk.LabelFrame(
            window,
            text="Docking Targets",
            padding=10,
        )

        target_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10,
        )

        selections = {}

        for name in configurations:

            variable = tk.BooleanVar(
                value=True
            )

            selections[name] = variable

            ttk.Checkbutton(
                target_frame,
                text=name,
                variable=variable,
            ).pack(
                anchor="w",
                pady=4,
            )

        skip_existing = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            window,
            text="Skip compounds already docked to selected targets",
            variable=skip_existing,
        ).pack(
            anchor="w",
            padx=15,
            pady=5,
        )

        selected_only = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            window,
            text="Dock only compounds selected in the main table",
            variable=selected_only,
        ).pack(
            anchor="w",
            padx=15,
            pady=5,
        )

        def run():

            targets = [
                (
                    name,
                    configurations[name],
                )
                for name, variable in selections.items()
                if variable.get()
            ]

            if not targets:

                messagebox.showwarning(
                    "No Targets",
                    "Select at least one docking target.",
                    parent=window,
                )

                return

            if selected_only.get():
                compound_ids = list(
                    self.tree.selection()
                )
            else:
                compound_ids = list(
                    self.project.compounds.keys()
                )

            if not compound_ids:

                messagebox.showwarning(
                    "No Compounds",
                    "There are no compounds to dock.",
                    parent=window,
                )

                return

            window.destroy()

            self.run_multi_target_docking_campaign(
                targets,
                compound_ids,
                skip_existing=skip_existing.get(),
            )

        ttk.Button(
            window,
            text="Run Docking Campaign",
            command=run,
        ).pack(
            fill="x",
            padx=15,
            pady=15,
        )

    def run_multi_target_docking_campaign(
        self,
        targets,
        compound_ids,
        skip_existing=True,
    ):

        jobs = []

        for compound_id in compound_ids:

            if compound_id not in self.project.compounds:
                continue

            for target_name, config in targets:

                already = (
                    self.project.compound_docked_to_target(
                        compound_id,
                        target_name,
                    )
                )

                if skip_existing and already:
                    continue

                jobs.append(
                    (
                        compound_id,
                        target_name,
                        config,
                    )
                )

        if not jobs:

            messagebox.showinfo(
                "Docking Campaign",
                "No docking jobs remain.",
            )

            return

        completed = 0
        failures = []

        for job_number, (
            compound_id,
            target_name,
            config,
        ) in enumerate(jobs, start=1):

            compound_name = self.compound_name(
                compound_id
            )

            self.status.set(
                f"Docking {compound_name} against "
                f"{target_name} ({job_number}/{len(jobs)})"
            )

            self.root.update_idletasks()

            try:

                result = self.dock_compound_to_target(
                    compound_id,
                    target_name,
                    config,
                )

                self.project.set_docking_result(
                    compound_id=compound_id,
                    docking_target=target_name,
                    score=result.get("score"),
                    poses_file=result.get("poses_file"),
                    log_file=result.get("log_file"),
                    poses=result.get("poses", []),
                    best_pose=result.get("best_pose", 1),
                )

                completed += 1

            except Exception as exc:

                failures.append(
                    f"{compound_name} -> {target_name}: {exc}"
                )

        self.refresh_table()

        if failures:

            messagebox.showwarning(
                "Docking Campaign",
                (
                    f"{completed} docking job(s) completed.\n\n"
                    f"{len(failures)} failed:\n\n"
                    + "\n".join(failures[:10])
                ),
            )

        else:

            messagebox.showinfo(
                "Docking Campaign",
                f"{completed} docking job(s) completed.",
            )

        self.status.set(
            "Docking campaign complete."
        )

    def dock_compound_to_target(
        self,
        compound_id,
        target_name,
        configuration,
    ):

        compound = self.project.compounds[
            compound_id
        ]

        compound_name = compound.get(
            "name",
            compound_id,
        )

        target_directory = (
            self.project.project_directory
            / "docking_results"
            / safe_filename(target_name)
        )

        target_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        config = dict(configuration)
        config["name"] = target_name
        config["target_name"] = target_name

        engine = DockingEngine(config)

        ligand_file = engine.prepare_ligand(
            compound["mol"],
            compound_name,
            target_directory,
        )

        return engine.dock(
            ligand_pdbqt=ligand_file,
            compound_name=compound_name,
            output_directory=target_directory,
        )


def main():

    root = tk.Tk()

    AutoSARDockApp(root)

    root.mainloop()
