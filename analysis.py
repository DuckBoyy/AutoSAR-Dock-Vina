from pathlib import Path
import math
import csv

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


NUMERIC_FIELDS = {
    "mw",
    "logp",
    "tpsa",
    "hbd",
    "hba",
    "rotatable_bonds",
    "docking_score",
    "activity_value",
    "pactivity",
}


def to_float(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def calculate_pactivity(value, unit):
    """
    Convert an activity measurement to a negative log molar value.

    Examples:

        10 nM = 8.0
        100 nM = 7.0
        1 uM = 6.0
        1 mM = 3.0
    """

    value = to_float(value)

    if value is None or value <= 0:
        return None

    unit = str(unit or "nM").strip().lower()

    factors = {
        "m": 1.0,
        "mm": 1e-3,
        "um": 1e-6,
        "µm": 1e-6,
        "nm": 1e-9,
        "pm": 1e-12,
    }

    if unit not in factors:
        return None

    molar = value * factors[unit]

    return -math.log10(molar)


def flatten_project(project):
    """
    Convert the project compound/docking model into flat rows.

    One row is generated per compound.

    The preferred docking result is the best available result.
    All docking results remain available in the raw project data.
    """

    rows = []

    compounds = project.get("compounds", [])

    for compound in compounds:

        row = dict(compound)

        activity_value = to_float(
            compound.get("activity_value")
        )

        activity_unit = compound.get(
            "activity_unit",
            "nM"
        )

        pactivity = calculate_pactivity(
            activity_value,
            activity_unit,
        )

        row["activity_value"] = activity_value
        row["activity_unit"] = activity_unit
        row["pactivity"] = pactivity

        docking_results = compound.get(
            "docking_results",
            []
        )

        scores = []

        for result in docking_results:

            score = to_float(
                result.get("score")
            )

            if score is not None:
                scores.append(
                    (score, result)
                )

        if scores:

            # Lower Vina score is generally better.
            scores.sort(
                key=lambda x: x[0]
            )

            best_score, best_result = scores[0]

            row["docking_score"] = best_score

            row["best_target"] = best_result.get(
                "target_name",
                ""
            )

            row["best_pose_file"] = best_result.get(
                "poses_file",
                ""
            )

        else:

            row["docking_score"] = None
            row["best_target"] = ""
            row["best_pose_file"] = ""

        rows.append(row)

    return rows


def export_csv(project, filename):
    """
    Export the compound table to CSV.
    """

    rows = flatten_project(project)

    if not rows:
        raise RuntimeError(
            "There are no compounds to export."
        )

    filename = Path(filename)

    keys = set()

    for row in rows:
        keys.update(row.keys())

    preferred_order = [

        "name",
        "smiles",

        "mw",
        "logp",
        "tpsa",
        "hbd",
        "hba",
        "rotatable_bonds",

        "docking_score",
        "best_target",
        "best_pose_file",

        "activity_type",
        "activity_value",
        "activity_unit",
        "pactivity",

        "notes",

        "parent",
        "sar_operation",
        "sar_description",
    ]

    columns = [
        key
        for key in preferred_order
        if key in keys
    ]

    columns.extend(
        sorted(
            keys - set(columns)
        )
    )

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return filename


def export_excel(project, filename):
    """
    Export project data to an Excel workbook.

    Requires pandas and openpyxl.
    """

    if pd is None:
        raise RuntimeError(
            "Excel export requires pandas."
        )

    rows = flatten_project(project)

    if not rows:
        raise RuntimeError(
            "There are no compounds to export."
        )

    filename = Path(filename)

    compound_rows = []
    docking_rows = []

    for compound in project.get(
        "compounds",
        []
    ):

        compound_row = dict(compound)

        compound_row.pop(
            "docking_results",
            None
        )

        compound_row["pactivity"] = calculate_pactivity(
            compound.get("activity_value"),
            compound.get("activity_unit"),
        )

        compound_rows.append(
            compound_row
        )

        for result in compound.get(
            "docking_results",
            []
        ):

            row = dict(result)

            row["compound_name"] = compound.get(
                "name",
                ""
            )

            docking_rows.append(
                row
            )

    compound_df = pd.DataFrame(
        compound_rows
    )

    docking_df = pd.DataFrame(
        docking_rows
    )

    with pd.ExcelWriter(
        filename,
        engine="openpyxl",
    ) as writer:

        compound_df.to_excel(
            writer,
            sheet_name="Compounds",
            index=False,
        )

        docking_df.to_excel(
            writer,
            sheet_name="Docking Results",
            index=False,
        )

        configs = project.get(
            "docking_configs",
            []
        )

        if configs:

            pd.DataFrame(
                configs
            ).to_excel(
                writer,
                sheet_name="Docking Configurations",
                index=False,
            )

    return filename


def get_numeric_value(row, field):

    value = row.get(field)

    return to_float(value)


def correlation(rows, x_field, y_field):
    """
    Calculate a simple Pearson correlation.

    Uses pandas when available.
    """

    pairs = []

    for row in rows:

        x = get_numeric_value(
            row,
            x_field,
        )

        y = get_numeric_value(
            row,
            y_field,
        )

        if x is None or y is None:
            continue

        pairs.append(
            (x, y)
        )

    if len(pairs) < 2:
        raise RuntimeError(
            "At least two compounds with valid data are required."
        )

    if pd is not None:

        frame = pd.DataFrame(
            pairs,
            columns=["x", "y"],
        )

        return float(
            frame["x"].corr(
                frame["y"]
            )
        )

    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in pairs
    )

    denominator_x = math.sqrt(
        sum(
            (x - mean_x) ** 2
            for x in xs
        )
    )

    denominator_y = math.sqrt(
        sum(
            (y - mean_y) ** 2
            for y in ys
        )
    )

    denominator = (
        denominator_x
        *
        denominator_y
    )

    if denominator == 0:
        return None

    return numerator / denominator


def plot_relationship(
    rows,
    x_field,
    y_field,
    title=None,
):
    """
    Create a simple scatter plot.

    Returns the matplotlib Figure.
    """

    if plt is None:
        raise RuntimeError(
            "Plotting requires matplotlib."
        )

    xs = []
    ys = []
    labels = []

    for row in rows:

        x = get_numeric_value(
            row,
            x_field,
        )

        y = get_numeric_value(
            row,
            y_field,
        )

        if x is None or y is None:
            continue

        xs.append(x)
        ys.append(y)

        labels.append(
            row.get(
                "name",
                ""
            )
        )

    if len(xs) < 2:
        raise RuntimeError(
            "At least two valid data points are required."
        )

    figure = plt.figure(
        figsize=(7, 5)
    )

    axis = figure.add_subplot(
        111
    )

    axis.scatter(
        xs,
        ys,
    )

    axis.set_xlabel(
        x_field
    )

    axis.set_ylabel(
        y_field
    )

    if title is None:

        title = (
            f"{y_field} vs {x_field}"
        )

    axis.set_title(
        title
    )

    figure.tight_layout()

    return figure