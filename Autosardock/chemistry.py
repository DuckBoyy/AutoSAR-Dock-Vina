from io import BytesIO

from rdkit import Chem
from rdkit.Chem import (
    AllChem,
    Crippen,
    Descriptors,
    Draw,
    Lipinski,
    rdDepictor,
)


def load_molecule(filename):
    """
    Load a molecule from an SDF, MOL, MOL2, or SMILES file.
    """

    filename_lower = filename.lower()

    mol = None

    if filename_lower.endswith(".sdf"):
        supplier = Chem.SDMolSupplier(
            filename,
            removeHs=False,
        )

        for candidate in supplier:
            if candidate is not None:
                mol = candidate
                break

    elif filename_lower.endswith(".mol"):
        mol = Chem.MolFromMolFile(
            filename,
            removeHs=False,
        )

    elif filename_lower.endswith(".mol2"):
        mol = Chem.MolFromMol2File(
            filename,
            removeHs=False,
        )

    elif filename_lower.endswith(".smi"):

        with open(
            filename,
            "r",
            encoding="utf-8",
        ) as handle:

            line = handle.readline().strip()

        if line:
            smiles = line.split()[0]
            mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        raise ValueError(
            "Could not load a valid molecule."
        )

    Chem.SanitizeMol(mol)

    return mol


def prepare_2d(mol):
    """
    Create a clean molecule suitable for
    consistent 2D visualization.
    """

    mol = Chem.Mol(mol)

    try:

        Chem.SanitizeMol(mol)

    except Exception:

        pass

    try:

        mol.RemoveAllConformers()

    except Exception:

        pass

    try:

        rdDepictor.Compute2DCoords(mol)

    except Exception:

        pass

    return mol


def molecule_image(
    mol,
    width=900,
    height=650,
    atom_indices=True,
    bond_indices=False,
):
    """
    Render a molecule as PNG bytes.
    """

    mol = prepare_2d(mol)

    drawer = Draw.MolDraw2DCairo(
        width,
        height,
    )

    options = drawer.drawOptions()

    options.addAtomIndices = atom_indices
    options.addBondIndices = bond_indices

    drawer.DrawMolecule(mol)

    drawer.FinishDrawing()

    return drawer.GetDrawingText()


def molecule_properties(mol):
    """
    Calculate common medicinal chemistry properties.
    """

    mol = Chem.Mol(mol)

    try:

        Chem.SanitizeMol(mol)

    except Exception:

        pass

    return {
        "MW": round(
            Descriptors.MolWt(mol),
            2,
        ),

        "LogP": round(
            Crippen.MolLogP(mol),
            2,
        ),

        "TPSA": round(
            Descriptors.TPSA(mol),
            2,
        ),

        "HBD": int(
            Lipinski.NumHDonors(mol)
        ),

        "HBA": int(
            Lipinski.NumHAcceptors(mol)
        ),

        "RotB": int(
            Lipinski.NumRotatableBonds(mol)
        ),

        "Rings": int(
            Lipinski.RingCount(mol)
        ),
    }


def molecule_to_smiles(mol):
    """
    Generate canonical SMILES.
    """

    return Chem.MolToSmiles(
        mol,
        canonical=True,
    )


def atom_information(mol):
    """
    Return a list describing every atom.
    """

    rows = []

    for atom in mol.GetAtoms():

        rows.append(
            {
                "index": atom.GetIdx(),
                "symbol": atom.GetSymbol(),
                "atomic_number": atom.GetAtomicNum(),
                "aromatic": atom.GetIsAromatic(),
                "degree": atom.GetDegree(),
                "hydrogens": atom.GetTotalNumHs(),
            }
        )

    return rows


def bond_information(mol):
    """
    Return a list describing every bond.
    """

    rows = []

    for bond in mol.GetBonds():

        rows.append(
            {
                "index": bond.GetIdx(),
                "atom_a": bond.GetBeginAtomIdx(),
                "atom_b": bond.GetEndAtomIdx(),
                "type": str(
                    bond.GetBondType()
                ),
                "aromatic": bond.GetIsAromatic(),
            }
        )

    return rows


def write_sdf(mol, filename):
    """
    Save one molecule to SDF.
    """

    writer = Chem.SDWriter(
        str(filename)
    )

    writer.write(mol)

    writer.close()
