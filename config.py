import math
import numpy as np

class config:
    """
    store the default configuration value as a config class
    """
    def __init__(self):
        self.threshold_ratio = 1.0/2.0
        self.tennis_width = 600
        self.tennis_height = 900

        self.gamma = 0.3
        self.threshold = self.tennis_height * self.threshold_ratio

        self.micro_window = np.array([(50, 600) ,(250, 600) ,(250, 300) ,(50, 300)])
        self.micro_window_h = self.micro_window[0][1] - self.micro_window[2][1]
        self.micro_window_w = self.micro_window[1][0] - self.micro_window[0][0]
        # coordinate of micro_windows left up points
        self.micro_window_x = self.micro_window[3][0]
        self.micro_window_y = self.micro_window[3][1]
        # micro_window_color
        self.micro_window_color = (200, 0, 60)

        # player color
        self.player_colors = [(0, 0, 255), (255, 255, 0)]

    def load_trans_param(self):
        a = 1.0 / (self.gamma * math.pow(self.threshold, self.gamma - 1))
        m = self.tennis_height - math.pow(float(self.tennis_height), self.gamma) * a
        b = (1.0 - self.gamma) / self.gamma * self.threshold + m
        return {'a':a, 'b':b, 'm':m, 'r': self.gamma, 'th':self.threshold}

    def set_gamma(self, val):
        self.gamma = val

    def set_threshold_ratio(self, val):
        assert val <= 1, 'threshold ratio must be in interval (0, 1]'
        assert val >= 0, 'threshold ratio must be in interval (0, 1]'
        self.threshold_ratio = val
        self.threshold = self.tennis_height * self.threshold_ratio

    def set_tennis_size(self, size):
        assert isinstance(size, tuple), 'size must be a tuple object'
        if len(size) == 1:
            self.tennis_height = size[0]
            self.tennis_width = size[0]
        elif len(size) == 2:
            self.tennis_width = size[0]
            self.tennis_height = size[1]
        else:
            raise NotImplementedError

        self.threshold = self.tennis_height * self.threshold_ratio

    def set_micro_window_size(self, window_points):
        assert len(window_points) == 4
        for idx, p in enumerate(window_points):
            assert len(p) == 2
            self.micro_window[idx] = p
        self.micro_window_h = self.micro_window[0][1] - self.micro_window[2][1]
        self.micro_window_w = self.micro_window[1][0] - self.micro_window[0][0]
        self.micro_window_x = self.micro_window[3][0]
        self.micro_window_y = self.micro_window[3][1]

    def set_micro_window_color(self, color):
        assert len(color) == 3
        for val in color:
            if val >=256 or val < 0:
                raise ValueError
        self.micro_window_color = color

    def set_player_color(self, val):
        if isinstance(val, tuple) or isinstance(val, list):
            for idx, color in enumerate(val):
                assert isinstance(color, tuple)
                assert len(color) == 3
                self.player_colors[idx] = color

