import numpy as np
from ..forcefield import Topology
from . import Trajectory, Frame


class XYZ(Trajectory):
    '''
    Since xyz format is not very useful, I only parse the first frame
    '''

    def __init__(self, file, mode='r'):
        super().__init__()
        self._file = open(file, mode)
        if mode == 'r':
            self._get_info()
        elif mode == 'w':
            pass

    def _get_info(self):
        '''
        Read the number of atoms and record the offset of lines and frames,
        so that we can read arbitrary frame later
        '''
        try:
            self.n_atom = int(self._file.readline())
        except:
            print('Invalid XYZ file')
            raise
        self._file.seek(0)

        self.n_frame = 1

    def read_frame(self, i_frame):
        if i_frame != 0:
            raise Exception('Can only read the first frame')

        return self.read_frame_from_string(self._file.read())

    def read_frame_from_string(self, string: str):
        frame = Frame(self.n_atom)
        lines = string.splitlines()

        for i in range(self.n_atom):
            words = lines[i + 2].split()
            frame.positions[i] = np.array(list(map(float, words[1:4]))) / 10  # convert from A to nm

        return frame

    def write_frame(self, topology: Topology, frame: Frame, subset=None):
        self._file.write('%i\n' % topology.n_atom)
        self._file.write('\n')

        if subset is None:
            subset = list(range(topology.n_atom))
        for ii, id in enumerate(subset):
            atom = topology.atoms[id]
            position = frame.positions[id] * 10  # convert from nm to A
            line = '%-8s %10.5f %10.5f %10.5f\n' % (atom.type, position[0], position[1], position[2])
            self._file.write(line)

    def close(self):
        self._file.close()
