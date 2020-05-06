import os
import numpy as np
from ..topology import Topology
from . import Trajectory, Frame


class Xyz(Trajectory):
    '''
    Since xyz format is not very useful, I only parse the first frame
    '''

    def __init__(self, file, mode='r'):
        super().__init__()
        if mode not in ('r', 'w', 'a'):
            raise Exception('Invalid mode')

        if mode == 'r':
            # open it in binary mode so that we can correctly seek despite of line ending
            self._file = open(file, 'rb')
            self._get_info()
        elif mode == 'a':
            self._file = open(file, 'ab')
        elif mode == 'w':
            self._file = open(file, 'wb')

        self._mode = mode
        self._opened = True

    def _get_info(self):
        '''
        Read the number of atoms and record the offset of lines and frames,
        so that we can read arbitrary frame later
        '''
        try:
            self.n_atom = int(self._file.readline())
        except:
            raise Exception('Invalid XYZ file')
        self._file.seek(0)

        # read in the file once and build a list of line offsets
        # the last element is the length of whole file
        self._line_offset = [0]
        offset = 0
        for line in self._file:
            offset += len(line)
            self._line_offset.append(offset)
        self._file.seek(0)

        # build a list of frame offsets
        self.n_frame = len(self._line_offset) // (2 + self.n_atom)
        self._frame_offset = []
        for i in range(self.n_frame + 1):
            line_start = (2 + self.n_atom) * i
            self._frame_offset.append(self._line_offset[line_start])

        self._frame = Frame(self.n_atom)

    def _read_frame(self, i_frame, frame):
        # skip to frame i and read only this frame
        self._file.seek(self._frame_offset[i_frame])
        lines = self._file.read(self._frame_offset[i_frame + 1] - self._frame_offset[i_frame]) \
            .decode().splitlines()
        for i in range(self.n_atom):
            words = lines[i + 2].split()
            x = float(words[1]) / 10  # convert A to nm
            y = float(words[2]) / 10
            z = float(words[3]) / 10
            frame.positions[i][:] = x, y, z

    def _write_frame(self, frame: Frame, topology: Topology, subset=None, **kwargs):
        if subset is None:
            subset = list(range(len(frame.positions)))

        string = '%i\n' % len(subset)
        string += 'Created by mstools: step= %i, t= %f ps\n' % (frame.step, frame.time)

        for ii, id in enumerate(subset):
            atom = topology.atoms[id]
            pos = frame.positions[id] * 10  # convert from nm to A
            # atom.symbol is more friendly than atom.type for visualizing trajectory
            string += '%-8s %10.5f %10.5f %10.5f\n' % (atom.symbol, pos[0], pos[1], pos[2])

        self._file.write(string.encode())
