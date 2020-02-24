import simtk.openmm as mm
from simtk import unit
from simtk.unit import bar
from simtk.unit import kilojoule_per_mole as kj_mol, kelvin
from .grofile import GroFile


def print_omm_info():
    print(mm.__version__)
    print(mm.version.openmm_library_path)
    print([mm.Platform.getPlatform(i).getName() for i in range(mm.Platform.getNumPlatforms())])
    print(mm.Platform.getPluginLoadFailures())


def minimize(sim, tolerance, gro_out=None):
    print('Minimizing...')
    state = sim.context.getState(getEnergy=True)
    print('    Initial Energy: ' + str(state.getPotentialEnergy()))

    sim.minimizeEnergy(tolerance=tolerance * kj_mol)
    state = sim.context.getState(getPositions=True, getEnergy=True)
    print('    Final   Energy: ' + str(state.getPotentialEnergy()))

    if gro_out is not None:
        with open(gro_out, 'w') as f:
            GroFile.writeFile(sim.topology, state.getTime(), state.getPositions(), state.getPeriodicBoxVectors(), f)


def apply_mc_barostat(system, pcoupl, P, T):
    if pcoupl == 'iso':
        print('    Isotropic barostat')
        system.addForce(mm.MonteCarloBarostat(P * bar, T * kelvin, 25))
    elif pcoupl == 'xyz':
        print('    Anisotropic barostat')
        system.addForce(mm.MonteCarloAnisotropicBarostat([P * bar] * 3, T * kelvin, True, True, True, 25))
    elif pcoupl == 'xy':
        print('    Anisotropic barostat only for X and Y')
        system.addForce(mm.MonteCarloAnisotropicBarostat([P * bar] * 3, T * kelvin, True, True, False, 25))
    elif pcoupl == 'z':
        print('    Anisotropic barostat only for Z')
        system.addForce(mm.MonteCarloAnisotropicBarostat([P * bar] * 3, T * kelvin, False, False, True, 25))
    else:
        raise Exception('Available pressure coupling types: iso, xyz, xy, z')