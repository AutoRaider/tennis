import cv2
import os
import shelve
import numpy
import math

from transform import Corner
import geometry as ge

class Calibrater:
    def __init__(self, img, img_size , width, height, data_path=None):
        self.data_path = data_path
        self.width = width
        self.height = height
        self.trans_matrix = None
        self.img = img
        self.img_size = img_size
        self.corner = None

        if not self.data_path:
            # no saved data, manual calibration
            print('select the four corner in transformed map')
            self.corner = Corner()
            tuner = DragCorner(self.img, self.corner,[],'tune corner',size=self.img_size)
            # cv2.moveWindow('tuning corner', 0, 0)
            tuner.run(delay=True)
        else:
            # read saved calibration data
            try:
                self.corner = self._load_corner()
            except :
                raise Exception('Load data failed. No such file %s' % self.data_path)

        self.trans_matrix = self._get_trans_matrix()

    def transform_point(self, point, inverse=False):
        """
        transform a given point in orignal image to a new point in another perspective according to trans_matrix
        :param: point to transform
        :param: inverse to set operation by transformation or inverse transformation
        :return: trans_point: transformed point coordinate
        """
        if not inverse:
            return point.perspective(self.trans_matrix)
        else:
            return point.perspective(self.trans_matrix.I)

    def transform_image(self, inputimage):
        """
        transform a given  image to another perspective according to trans_matrix
        :param: input image
        :return: perpective: transformed image
        """
        return cv2.warpPerspective(inputimage, self.trans_matrix, (self.width, self.height))

    def _load_dat_config(self, key):
        """
        load sections and contents from dat file
        :param key: key to load
        :return: sections and contents
        """
        dat = shelve.open(self.data_path)
        try:
            response = dat[key]
        except ImportError:
            response = None
            print(ImportError)
        except AttributeError:
            response = None
            print (AttributeError)
        dat.close()
        return response

    def _load_corner(self):
        """
        load last tuning table corner data
        or new corner from memory
        """
        dat = shelve.open(self.data_path)
        corner = dat['corner']
        dat.close()
        return corner
    

    def save_table_corner(self, output_path=None):
        """
        save table corner object into file
        :param output_path: the path to save calibration data (default is self.data_path)
        """
        if self.corner != None:
            if not output_path:
                output_path = self.data_path
            if not output_path:
                raise Exception('output_path must be set for saving data')
            try:
                dat = shelve.open(output_path, writeback=True)
            except:
                print("try")
            dat['corner'] = self.corner
            dat.close()

    def _get_trans_matrix(self):
        """
        calculate the camera to table matrix
        :return: camera to table matrix
        """
        target_width = self.width
        target_height = self.height
        # table_corners = numpy.array([(100, 300), (target_width - 100, 300), (100, target_height - 200),
        #                              (target_width - 100, target_height - 200)], numpy.float32)
        table_corners = numpy.array([(0, 0), (target_width, 0), (0, target_height),
                                      (target_width, target_height)], numpy.float32)
        corners = [[self.corner.p1.tuple(), self.corner.p2.tuple(), self.corner.p3.tuple(), self.corner.p4.tuple()]]
        camera_corners = numpy.array(corners, numpy.float32)
        return cv2.getPerspectiveTransform(camera_corners, table_corners)

class DragCorner:

    def __init__(self, img, corners, function, win_name, size=(900, 500), pos=(0, 0), line_thick=2):
        self.img = img
        self.corners = corners
        self.function = function
        self.win_name = win_name
        self.size = size
        self.pos = pos
        self.res = []
        self._point = None
        self.line_thick = line_thick

    def _get_nearest_corner(self):
        """
        get nearest corner
        :return: nearest corner
        """
        nearest = self.corners.p1
        distance = self._point.distance_to_point(nearest)

        dist = self._point.distance_to_point(self.corners.p2)
        if dist < distance:
            distance = dist
            nearest = self.corners.p2

        dist = self._point.distance_to_point(self.corners.p3)
        if dist < distance:
            distance = dist
            nearest = self.corners.p3

        dist = self._point.distance_to_point(self.corners.p4)
        if dist < distance:
            nearest = self.corners.p4

        return nearest

    def _update(self, event, x, y, flag, para):
        """
        mouse event
        """
        image = self.img.copy()
        if event == cv2.EVENT_LBUTTONDOWN:
            self._point = ge.Point(x, y)
            self._point = self._get_nearest_corner()
        elif event == cv2.EVENT_MOUSEMOVE:
            if self._point is not None:
                self._point.update(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self._point = None

        cv2.line(image, self.corners.p1.tuple(), self.corners.p2.tuple(), (255, 255, 255), self.line_thick)
        cv2.line(image, self.corners.p1.tuple(), self.corners.p3.tuple(), (255, 255, 255), self.line_thick)
        cv2.line(image, self.corners.p2.tuple(), self.corners.p4.tuple(), (255, 255, 255), self.line_thick)
        cv2.line(image, self.corners.p3.tuple(), self.corners.p4.tuple(), (255, 255, 255), self.line_thick)

        cv2.circle(image, self.corners.p1.tuple(), 5, [255, 255, 255], 1)
        cv2.circle(image, self.corners.p2.tuple(), 10, [255, 255, 255], 3)
        cv2.circle(image, self.corners.p3.tuple(), 15, [255, 255, 255], 5)
        cv2.circle(image, self.corners.p4.tuple(), 20, [255, 255, 255], 7)

        cv2.imshow(self.win_name, image)

    def run(self, delay):
        """
        start tuning
        :param delay:
            if True, waitKey(0)
        """
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        if self.size == 0:
            cv2.moveWindow(self.win_name, 1800, 0)
            cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.resizeWindow(self.win_name, self.size[0], self.size[1])

        cv2.setMouseCallback(self.win_name, self._update, [])
        cv2.moveWindow(self.win_name, self.pos[0], self.pos[1])
        cv2.imshow(self.win_name, self.img)

        if delay:
            cv2.waitKey(0)
            cv2.destroyAllWindows()


def warper(x, a, b, m, r, th):
    if x >= th:
        return a * math.pow(x, r) + m
    else:
        return x + b

def inverse_warper(y, a, b, m, r, th):
    if y >= th + b:
        return math.pow((y-m)/a, 1.0/r)
    else:
        return y - b

def calculate_remap(image, gamma, threshold, warper):

    """
    calculate remap matrix for a given warper f(x)
    (f(x) = ax^gamma+m when x>threshold, f(x) = x+b when x<threshold)
    with following constraint:
        1. f(height) = height
        2. f'(threshold) = 1
    where height is the height of input image
    :param image: input image for warping
    :param gamma: exponent number in f(x)
    :param threshold: threshold number in f(x)
    :param warper: function f(x)
    :return: output map_x and map_y
    """
    map_shape = image.shape[:2]  # take the width and height of image as the map shape

    h = map_shape[0]
    a = 1.0 / (gamma * math.pow(threshold, gamma - 1))
    m = h - math.pow(float(h), gamma) * a
    b = (1.0 - gamma) / gamma * threshold + m

    map_x = numpy.zeros(map_shape, dtype=numpy.float32)
    map_y = numpy.zeros(map_shape, dtype=numpy.float32)
    # construct map

    for x in range(0, map_shape[1]):
        for y in range(0, map_shape[0]):
            map_x[y, x] = float(x)
            map_y[y, x] = h - inverse_warper(h - y, a, b, m, r=gamma, th=threshold)
            #print(str(y)+' to '+str(map_y[y, x]))
    return map_x, map_y

def trasform_remap(image, map_x, map_y):
    """
    transform input image into warped one according to the a nonlinear coordinate map f(x)
    :return: output warped image
    """


    return cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

if __name__ == '__main__':
    image = cv2.imread('demo.jpg')
    #print image

    tennis_width = 300
    tennis_height = 400
    size = image.shape
    print(size)
    cal = Calibrater(image, img_size=size[-2::-1], width=tennis_width, height=tennis_height, data_path=None)
    perspective = cal.transform_image(image)
    #warp = trasform_remap(perspective, 1.5, float(1)/2*tennis_height, warper=warper)
    #invwarp = trasform_remap(warp, 1.5, float(1) / 2 * tennis_height, warper=inverse_warper)
    mx1, my1 = calculate_remap(perspective, 0.1, float(1)/2*tennis_height, warper=warper)
    cv2.imshow('mask table', perspective)
    cv2.moveWindow('mask table', 100, 100)
    warp = trasform_remap(perspective, mx1, my1)
    cv2.imshow('warp table', warp)
    #cv2.imshow('invwarp table', invwarp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cal.save_table_corner(output_path='./data/tennis.bin')
