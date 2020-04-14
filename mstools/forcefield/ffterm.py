from collections import namedtuple


class FFTerm():
    def __init__(self):
        self.name = 'ffterm'
        self.version = None

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self) + ' at 0x' + str(hex(id(self))[2:].upper())

    def to_zfp(self) -> {str: str}:
        raise NotImplementedError('This method should be implemented by subclass')

    @property
    def identifier(self):
        return self.__class__.__name__


class AtomType(FFTerm):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.symbol = 'UNK'
        self.mass = 0.
        self.charge = 0.
        self.eqt_vdw = name
        self.eqt_charge_increment = name
        self.eqt_bond = name
        self.eqt_angle_center = name
        self.eqt_angle_side = name
        self.eqt_dihedral_center = name
        self.eqt_dihedral_side = name
        self.eqt_improper_center = name
        self.eqt_improper_side = name
        self._eqt_charge = name

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def to_zfp(self) -> {str: str}:
        return {
            'name'     : self.name,
            'symbol'   : self.symbol,
            'mass'     : '%.4f' % self.mass,
            'charge'   : '%.6f' % self.charge,
            'eqt_vdw'  : self.eqt_vdw,
            'eqt_inc'  : self.eqt_charge_increment,
            'eqt_bond' : self.eqt_bond,
            'eqt_ang_c': self.eqt_angle_center,
            'eqt_ang_s': self.eqt_angle_side,
            'eqt_dih_c': self.eqt_dihedral_center,
            'eqt_dih_s': self.eqt_dihedral_side,
            'eqt_imp_c': self.eqt_improper_center,
            'eqt_imp_s': self.eqt_improper_side,
        }


class ChargeIncrementTerm(FFTerm):
    def __init__(self, type1: str, type2: str, value: float):
        super().__init__()
        at1, at2 = sorted([type1, type2])
        self.type1 = at1
        self.type2 = at2
        self.value = value if at1 == type1 else -value
        self.name = '%s,%s' % (self.type1, self.type2)

    def __lt__(self, other):
        return [self.type1, self.type2] < [other.type1, other.type2]

    def __gt__(self, other):
        return [self.type1, self.type2] > [other.type1, other.type2]

    def to_zfp(self) -> {str: str}:
        return {
            'type1': self.type1,
            'type2': self.type2,
            'value': '%.6f' % self.value,
        }


class VdwTerm(FFTerm):
    def __init__(self, type1: str, type2: str):
        super().__init__()
        at1, at2 = sorted([type1, type2])
        self.type1 = at1
        self.type2 = at2
        self.name = '%s,%s' % (self.type1, self.type2)

    def __lt__(self, other):
        return [self.type1, self.type2] < [other.type1, other.type2]

    def __gt__(self, other):
        return [self.type1, self.type2] > [other.type1, other.type2]


class BondTerm(FFTerm):
    def __init__(self, type1: str, type2: str, length: float, fixed=False):
        super().__init__()
        at1, at2 = sorted([type1, type2])
        self.type1 = at1
        self.type2 = at2
        self.length = length
        self.fixed = fixed
        self.name = '%s,%s' % (self.type1, self.type2)

    def __lt__(self, other):
        return [self.type1, self.type2] < [other.type1, other.type2]

    def __gt__(self, other):
        return [self.type1, self.type2] > [other.type1, other.type2]


class AngleTerm(FFTerm):
    def __init__(self, type1: str, type2: str, type3: str, theta: float, fixed=False):
        super().__init__()
        at1, at3 = sorted([type1, type3])
        self.type1 = at1
        self.type2 = type2
        self.type3 = at3
        self.theta = theta
        self.fixed = fixed
        self.name = '%s,%s,%s' % (self.type1, self.type2, self.type3)

    def __lt__(self, other):
        return [self.type1, self.type2, self.type3] < [other.type1, other.type2, other.type3]

    def __gt__(self, other):
        return [self.type1, self.type2, self.type3] > [other.type1, other.type2, other.type3]


class DihedralTerm(FFTerm):
    '''
    DihedralTerm allows wildcard(*) for side atoms
    '''

    def __init__(self, type1: str, type2: str, type3: str, type4: str):
        super().__init__()
        if '*' in [type2, type3]:
            raise Exception('Wildcard not allowed for center atoms in DihedralTerm')
        if [type1, type4].count('*') in [0, 2]:
            at1, at2, at3, at4 = min([(type1, type2, type3, type4), (type4, type3, type2, type1)])
        elif type1 == '*':
            at1, at2, at3, at4 = (type4, type3, type2, type1)
        else:
            at1, at2, at3, at4 = (type1, type2, type3, type4)
        self.type1 = at1
        self.type2 = at2
        self.type3 = at3
        self.type4 = at4
        self.name = '%s,%s,%s,%s' % (self.type1, self.type2, self.type3, self.type4)

    def __lt__(self, other):
        return [self.type1, self.type2, self.type3, self.type4] \
               < [other.type1, other.type2, other.type3, other.type4]

    def __gt__(self, other):
        return [self.type1, self.type2, self.type3, self.type4] \
               > [other.type1, other.type2, other.type3, other.type4]


class ImproperTerm(FFTerm):
    '''
    ImproperTerm allows wildcard(*) for side atoms
    Center atom is the first, following the convention of GROMACS
    '''

    def __init__(self, type1: str, type2: str, type3: str, type4: str):
        super().__init__()
        if type1 == '*':
            raise Exception('Wildcard not allowed for center atoms in ImproperTerm')
        non_wildcard = [t for t in (type2, type3, type4) if t != '*']
        at2, at3, at4 = list(sorted(non_wildcard)) + ['*'] * (3 - len(non_wildcard))
        self.type1 = type1
        self.type2 = at2
        self.type3 = at3
        self.type4 = at4
        self.name = '%s,%s,%s,%s' % (self.type1, self.type2, self.type3, self.type4)

    def __lt__(self, other):
        return [self.type1, self.type2, self.type3, self.type4] \
               < [other.type1, other.type2, other.type3, other.type4]

    def __gt__(self, other):
        return [self.type1, self.type2, self.type3, self.type4] \
               > [other.type1, other.type2, other.type3, other.type4]


class LJ126Term(VdwTerm):
    '''
    LJ126 is commonly used, so don't generalize it with MieTerm
    U = 4*epsilon*((sigma/r)^12-(sigma/r)^6)
    '''

    def __init__(self, type1, type2, epsilon, sigma):
        super().__init__(type1, type2)
        self.epsilon = epsilon
        self.sigma = sigma

    def to_zfp(self) -> {str: str}:
        return {
            'type1'  : self.type1,
            'type2'  : self.type2,
            'epsilon': '%.5f' % self.epsilon,
            'sigma'  : '%.5f' % self.sigma,
        }


class MieTerm(VdwTerm):
    '''
    Mainly used for SDK and SAFT-gamma Coarse-Grained force field
    U = C * epsilon * ((sigma/r)^n - (sigma/r)^m)
    C = n/(n-m) * (n/m)^(m/(n-m))
    r_min = (n/m)^(1/(n-m)) * sigma
    '''

    def __init__(self, type1, type2, epsilon, sigma, repulsion, attraction):
        super().__init__(type1, type2)
        self.epsilon = epsilon
        self.sigma = sigma
        self.repulsion = repulsion
        self.attraction = attraction

    def to_zfp(self) -> {str: str}:
        return {
            'type1'     : self.type1,
            'type2'     : self.type2,
            'epsilon'   : '%.5f' % self.epsilon,
            'sigma'     : '%.5f' % self.sigma,
            'repulsion' : '%.3f' % self.repulsion,
            'attraction': '%.3f' % self.attraction,
        }

    @staticmethod
    def factor_energy(rep, att):
        return rep / (rep - att) * (rep / att) ** (att / (rep - att))

    @staticmethod
    def factor_r_min(rep, att):
        return (rep / att) ** (1 / (rep - att))


class HarmonicBondTerm(BondTerm):
    '''
    U = k * (b-b0)^2
    '''

    def __init__(self, type1, type2, length, k, fixed=False):
        super().__init__(type1, type2, length, fixed=fixed)
        self.k = k

    def to_zfp(self) -> {str: str}:
        return {
            'type1' : self.type1,
            'type2' : self.type2,
            'length': '%.5f' % self.length,
            'k'     : '%.5f' % self.k,
        }


class HarmonicAngleTerm(AngleTerm):
    '''
    U = k * (theta-theta0)^2
    '''

    def __init__(self, type1, type2, type3, theta, k, fixed=False):
        super().__init__(type1, type2, type3, theta, fixed=fixed)
        self.k = k

    def to_zfp(self) -> {str: str}:
        return {
            'type1': self.type1,
            'type2': self.type2,
            'type3': self.type3,
            'theta': '%.3f' % self.theta,
            'k'    : '%.5f' % self.k,
        }


class SDKAngleTerm(AngleTerm):
    '''
    U = k * (theta-theta0)^2 + LJ96
    LJ96 = 6.75 * epsilon * ((sigma/r)^9 - (sigma/r)^6) + epsilon, r < 1.144714 * sigma
    '''

    def __init__(self, type1, type2, type3, theta, k, epsilon, sigma):
        super().__init__(type1, type2, type3, theta, fixed=False)
        self.k = k
        self.epsilon = epsilon
        self.sigma = sigma

    def to_zfp(self) -> {str: str}:
        return {
            'type1'  : self.type1,
            'type2'  : self.type2,
            'type3'  : self.type3,
            'theta'  : '%.3f' % self.theta,
            'k'      : '%.5f' % self.k,
            'epsilon': '%.5f' % self.epsilon,
            'sigma'  : '%.5f' % self.sigma,
        }


class PeriodicDihedralTerm(DihedralTerm):
    '''
    U = k * (1+cos(n*phi-phi0_n))
    '''

    def __init__(self, type1, type2, type3, type4, n_list: [int], k_list: [float],
                 phi_list: [float]):
        super().__init__(type1, type2, type3, type4)
        if len(set(n_list)) != len(n_list):
            raise Exception('Duplicated multiplicities for PeriodicDihedralTerm: %s' % self.name)
        if any([not isinstance(n, int) or n < 1 for n in n_list]):
            raise Exception('Multiplicities should be positive integer: %s' % self.name)
        self.n_list = n_list[:]
        self.k_list = k_list[:]
        self.phi_list = phi_list[:]

    def add_parameter(self, n, k, phi):
        if not isinstance(n, int) or n < 1:
            raise Exception('Multiplicity should be positive integer: %s' % self.name)
        self.n_list.append(n)
        self.k_list.append(k)
        self.phi_list.append(phi)

    def to_zfp(self) -> {str: str}:
        return {
            'type1'   : self.type1,
            'type2'   : self.type2,
            'type3'   : self.type3,
            'type4'   : self.type4,
            'n_list'  : ','.join(['%i' % n for n in self.n_list]),
            'k_list'  : ','.join(['%.5f' % k for k in self.k_list]),
            'phi_list': ','.join(['%.3f' % phi for phi in self.phi_list]),
        }


class OplsDihedralTerm(DihedralTerm):
    '''
    OplsDihedral is a more convenient version of PeriodicDihedral
    U = (k1*(1+cos(phi)) + k2*(1-cos(2*phi)) + k3*(1+cos(3*phi)) + k4*(1-cos(4*phi)))
    '''

    def __init__(self, type1, type2, type3, type4, k1, k2, k3, k4):
        super().__init__(type1, type2, type3, type4)
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        self.k4 = k4

    def to_zfp(self) -> {str: str}:
        return {
            'type1': self.type1,
            'type2': self.type2,
            'type3': self.type3,
            'type4': self.type4,
            'k1'   : '%.5f' % self.k1,
            'k2'   : '%.5f' % self.k2,
            'k3'   : '%.5f' % self.k3,
            'k4'   : '%.5f' % self.k4,
        }


class PeriodicImproperTerm(ImproperTerm):
    '''
    Normally for keeping 3-coordinated structures in the same plane, in which case xi0=180
    U = k * (1+cos(2*phi-phi0))
    '''

    def __init__(self, type1, type2, type3, type4, phi, k):
        super().__init__(type1, type2, type3, type4)
        self.phi = phi
        self.k = k

    def to_zfp(self) -> {str: str}:
        return {
            'type1': self.type1,
            'type2': self.type2,
            'type3': self.type3,
            'type4': self.type4,
            'phi'  : '%.3f' % self.phi,
            'k'    : '%.5f' % self.k,
        }


class HarmonicImproperTerm(ImproperTerm):
    '''
    U = k * (phi-phi0)^2
    '''

    def __init__(self, type1, type2, type3, type4, phi, k):
        super().__init__(type1, type2, type3, type4)
        self.phi = phi
        self.k = k

    def to_zfp(self) -> {str: str}:
        return {
            'type1': self.type1,
            'type2': self.type2,
            'type3': self.type3,
            'type4': self.type4,
            'phi'  : '%.3f' % self.phi,
            'k'    : '%.5f' % self.k,
        }
