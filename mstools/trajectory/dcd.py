import numpy as np
from . import Trajectory, Frame


class Dcd(Trajectory):
    '''
    Currently mstools use mdtraj to parse DCD format
    Only box and positions are parsed
    '''

    def __init__(self, file, mode='r'):
        super().__init__()

        try:
            from mdtraj.formats import DCDTrajectoryFile
        except:
            raise ImportError(
                'Currently mstools use mdtraj to parse DCD format. Cannot import mdtraj')

        if mode == 'r':
            self._dcd = DCDTrajectoryFile(file, mode='r')
            self._get_info()
        elif mode == 'w':
            self._dcd = DCDTrajectoryFile(file, mode='w')
        else:
            raise Exception('Appending not supported for DCD')

        self._mode = mode
        self._opened = True

    def close(self):
        try:
            self._dcd.close()
        except:
            pass
        self._opened = False

    def _get_info(self):
        '''
        Read the number of atoms and record the offset of lines and frames,
        so that we can read arbitrary frame later
        '''
        self.n_frame = len(self._dcd)
        if self.n_frame == 0:
            raise Exception('Empty DCD file')
        positions, lengths, angles = self._dcd.read(1)
        _, self.n_atom, _ = positions.shape
        self._frame = Frame(self.n_atom)

    def _read_frame(self, i_frame, frame):
        self._dcd.seek(i_frame)
        positions, box_lengths, box_angles = self._dcd.read(1)
        angle = box_angles[0]
        angle[np.abs(angle - 90) < 1E-4] = 90  # in case precision issue
        frame.positions = positions[0] / 10  # convert A to nm
        frame.cell.set_box([box_lengths[0] / 10, angle])  # convert A to nm

    def write_frame(self, frame, topology=None, subset=None, **kwargs):
        if subset is None:
            positions = frame.positions
        else:
            positions = frame.positions[subset]
        self._dcd.write(positions * 10, frame.cell.lengths * 10,
                        frame.cell.angles)  # convert nm to A
