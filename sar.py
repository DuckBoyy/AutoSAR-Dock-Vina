from rdkit import Chem


LINKER_LIBRARIES = {

    "Simple Linkers": [
        ("methylene", "C"),
        ("ethylene", "CC"),
        ("propylene", "CCC"),
        ("oxygen", "O"),
        ("amine", "N"),
        ("carbonyl", "C=O"),
        ("amide", "NC=O"),
    ],

    "Medicinal Chemistry": [
        ("methylene", "C"),
        ("ethylene", "CC"),
        ("oxygen", "O"),
        ("sulfur", "S"),
        ("amine", "N"),
        ("amide", "NC=O"),
        ("urea", "NC(=O)N"),
        ("ether", "CO"),
    ],
}


REPLACEMENT_LIBRARIES = {

    "Common Heteroatom Replacements": [
        "N",
        "O",
        "S",
    ],

    "Carbon/Nitrogen Scan": [
        "C",
        "N",
    ],

    "Halogen Scan": [
        "F",
        "Cl",
        "Br",
        "I",
    ],
}


def sanitize_product(mol):
    """
    Sanitize a product while handling common
    aromaticity/kekulization issues.
    """

    mol = Chem.Mol(mol)

    try:

        Chem.SanitizeMol(mol)

        return mol

    except Exception:

        pass

    try:

        for atom in mol.GetAtoms():

            atom.SetIsAromatic(False)

        for bond in mol.GetBonds():

            bond.SetIsAromatic(False)

        Chem.SanitizeMol(mol)

        return mol

    except Exception:

        return None


def linker_library(
    mol,
    atom_a,
    atom_b,
    library_name,
):
    """
    Insert linkers between two selected atoms.

    Atom A and Atom B must already be directly
    connected by a bond.
    """

    if library_name not in LINKER_LIBRARIES:

        raise ValueError(
            f"Unknown linker library: "
            f"{library_name}"
        )

    products = []

    linker_entries = LINKER_LIBRARIES[
        library_name
    ]

    for linker_name, linker_smiles in linker_entries:

        product = insert_linker_between_atoms(
            mol,
            atom_a,
            atom_b,
            linker_smiles,
        )

        if product is not None:

            products.append(
                (
                    linker_name,
                    product,
                )
            )

    return products


def bond_linker_library(
    mol,
    bond_index,
    library_name,
):
    """
    Insert linkers into a selected bond.

    This supports bonds between aromatic atoms,
    including aryl–aryl bonds.
    """

    if bond_index < 0:

        raise ValueError(
            "Bond index cannot be negative."
        )

    if bond_index >= mol.GetNumBonds():

        raise ValueError(
            "Bond index is outside the molecule."
        )

    bond = mol.GetBondWithIdx(
        bond_index
    )

    atom_a = bond.GetBeginAtomIdx()

    atom_b = bond.GetEndAtomIdx()

    return linker_library(
        mol,
        atom_a,
        atom_b,
        library_name,
    )


def insert_linker_between_atoms(
    mol,
    atom_a,
    atom_b,
    linker_smiles,
):
    """
    Remove the bond between atom_a and atom_b,
    then insert a linker fragment.
    """

    if atom_a == atom_b:

        raise ValueError(
            "Atom A and Atom B cannot be the same."
        )

    bond = mol.GetBondBetweenAtoms(
        atom_a,
        atom_b,
    )

    if bond is None:

        raise ValueError(
            "The selected atoms are not "
            "directly connected."
        )

    linker = Chem.MolFromSmiles(
        linker_smiles
    )

    if linker is None:

        return None

    combined = Chem.CombineMols(
        mol,
        linker,
    )

    editable = Chem.RWMol(
        combined
    )

    editable.RemoveBond(
        atom_a,
        atom_b,
    )

    linker_offset = mol.GetNumAtoms()

    linker_atom_count = linker.GetNumAtoms()

    if linker_atom_count == 0:

        return None

    first_linker_atom = linker_offset

    last_linker_atom = (
        linker_offset
        + linker_atom_count
        - 1
    )

    editable.AddBond(
        atom_a,
        first_linker_atom,
        Chem.BondType.SINGLE,
    )

    editable.AddBond(
        last_linker_atom,
        atom_b,
        Chem.BondType.SINGLE,
    )

    product = editable.GetMol()

    return sanitize_product(
        product
    )


def replacement_library(
    mol,
    atom_index,
    library_name,
):
    """
    Generate single atom replacements.
    """

    if library_name not in REPLACEMENT_LIBRARIES:

        raise ValueError(
            f"Unknown replacement library: "
            f"{library_name}"
        )

    if (
        atom_index < 0
        or atom_index >= mol.GetNumAtoms()
    ):

        raise ValueError(
            "Atom index is outside the molecule."
        )

    products = []

    for symbol in REPLACEMENT_LIBRARIES[
        library_name
    ]:

        product = replace_atom(
            mol,
            atom_index,
            symbol,
        )

        if product is not None:

            products.append(
                (
                    f"{symbol}_replacement",
                    product,
                )
            )

    return products


def replace_atom(
    mol,
    atom_index,
    new_symbol,
):
    """
    Replace one atom with another element.

    The product is sanitized afterward so RDKit
    can determine valid implicit hydrogens and
    aromaticity where possible.
    """

    periodic_table = Chem.GetPeriodicTable()

    atomic_number = (
        periodic_table.GetAtomicNumber(
            new_symbol
        )
    )

    editable = Chem.RWMol(
        Chem.Mol(mol)
    )

    old_atom = editable.GetAtomWithIdx(
        atom_index
    )

    new_atom = Chem.Atom(
        atomic_number
    )

    new_atom.SetFormalCharge(
        old_atom.GetFormalCharge()
    )

    new_atom.SetNoImplicit(
        False
    )

    new_index = editable.AddAtom(
        new_atom
    )

    neighbors = []

    for bond in old_atom.GetBonds():

        if (
            bond.GetBeginAtomIdx()
            == atom_index
        ):

            neighbor = (
                bond.GetEndAtomIdx()
            )

        else:

            neighbor = (
                bond.GetBeginAtomIdx()
            )

        neighbors.append(
            (
                neighbor,
                bond.GetBondType(),
                bond.GetIsAromatic(),
            )
        )

    editable.RemoveAtom(
        atom_index
    )

    adjusted_new_index = new_index - 1

    for neighbor, bond_type, aromatic in neighbors:

        adjusted_neighbor = neighbor

        if neighbor > atom_index:

            adjusted_neighbor -= 1

        editable.AddBond(
            adjusted_new_index,
            adjusted_neighbor,
            bond_type,
        )

        new_bond = editable.GetBondBetweenAtoms(
            adjusted_new_index,
            adjusted_neighbor,
        )

        if new_bond is not None:

            new_bond.SetIsAromatic(
                aromatic
            )

    product = editable.GetMol()

    return sanitize_product(
        product
    )


def delete_atom(
    mol,
    atom_index,
):
    """
    Delete a single atom.

    Note:
    This is most useful for terminal or simple
    substituent atoms. Removing a central atom
    may split the molecule into fragments.
    """

    if (
        atom_index < 0
        or atom_index >= mol.GetNumAtoms()
    ):

        raise ValueError(
            "Atom index is outside the molecule."
        )

    editable = Chem.RWMol(
        Chem.Mol(mol)
    )

    editable.RemoveAtom(
        atom_index
    )

    product = editable.GetMol()

    return sanitize_product(
        product
    )


def delete_functional_group(
    mol,
    bond_index,
    keep_atom,
):
    """
    Break a selected bond and retain the
    molecular component containing keep_atom.

    The opposite fragment is deleted.
    """

    if (
        bond_index < 0
        or bond_index >= mol.GetNumBonds()
    ):

        raise ValueError(
            "Bond index is outside the molecule."
        )

    bond = mol.GetBondWithIdx(
        bond_index
    )

    atom_a = bond.GetBeginAtomIdx()

    atom_b = bond.GetEndAtomIdx()

    if keep_atom not in [
        atom_a,
        atom_b,
    ]:

        raise ValueError(
            "Keep Atom must be one of the "
            "two atoms in the selected bond."
        )

    editable = Chem.RWMol(
        Chem.Mol(mol)
    )

    editable.RemoveBond(
        atom_a,
        atom_b,
    )

    broken = editable.GetMol()

    fragments = Chem.GetMolFrags(
        broken,
        asMols=True,
        sanitizeFrags=False,
    )

    for fragment in fragments:

        atom_map = [
            atom.GetAtomMapNum()
            for atom in fragment.GetAtoms()
        ]

        if atom_map:
            pass

    # Determine the component containing
    # the original keep atom by assigning
    # temporary atom map numbers.

    indexed = Chem.Mol(mol)

    for atom in indexed.GetAtoms():

        atom.SetAtomMapNum(
            atom.GetIdx() + 1
        )

    editable = Chem.RWMol(
        indexed
    )

    editable.RemoveBond(
        atom_a,
        atom_b,
    )

    broken = editable.GetMol()

    fragments = Chem.GetMolFrags(
        broken,
        asMols=True,
        sanitizeFrags=False,
    )

    keep_map_number = (
        keep_atom + 1
    )

    for fragment in fragments:

        maps = {
            atom.GetAtomMapNum()
            for atom in fragment.GetAtoms()
        }

        if keep_map_number in maps:

            for atom in fragment.GetAtoms():

                atom.SetAtomMapNum(0)

            return sanitize_product(
                fragment
            )

    return None