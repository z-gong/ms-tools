#!/usr/bin/env python3

import os
import sys
import pytest
from mstools.topology import Topology, UnitCell
from mstools.forcefield import Ppf, Padua, Zfp
from mstools.simsys import System
from mstools.wrapper.packmol import Packmol

cwd = os.path.dirname(os.path.abspath(__file__))


def test_compress():
    top = Topology.open(cwd + '/files/10-H2O-5-C3H6.lmp', improper_center=3)
    molecules = top.molecules
    for mol in molecules[4:]:
        for atom in mol.atoms:
            atom.charge *= 2

    top = Topology.open(cwd + '/files/Im11.zmat')
    molecules += top.molecules

    top = Topology.open(cwd + '/files/10-H2O-5-C3H6.lmp', improper_center=3)
    molecules += top.molecules

    top = Topology.open(cwd + '/files/Im11.zmat')
    molecules += top.molecules

    top = Topology()
    top.update_molecules(molecules)
    mols_unique = top.get_unique_molecules()
    for mol, count in mols_unique.items():
        print(str(mol), count)

    assert list(mols_unique.values()) == [4, 6, 5, 1, 10, 5, 1]


def test_scale():
    packmol = Packmol(r'D:\Projects\DFF\Developing\bin32w\Packmol\packmol.exe')
    top = Topology.open(cwd + '/files/Im11.zmat')
    top.cell.set_box([3, 3, 3])
    top.scale_with_packmol(10, packmol)
    top.write(cwd + '/files/packmol.pdb')


def test_guess_connectivity():
    top = Topology.open(cwd + '/files/MoS2-13x8-layer1.xyz')
    top.cell.set_box([4.109, 4.380, 1.230])
    ff = Padua(cwd + '/files/MoS2.ff')
    top.guess_connectivity_from_ff(ff, angle_tolerance=15, pbc='xy')
    assert top.n_bond == 1248
    assert top.n_angle == 3120
    assert top.n_dihedral == 0
    assert top.n_improper == 0