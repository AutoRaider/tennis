import os
import time
import Queue
import threading

import cv2


class VideoCapture:
    WARNING_COUNT = 30

    def __init__(self):
        self.device = None
        self.width = 1280
        self.height = 720
        self.fps = 30
        self.queue = Queue.Queue()

        self.thread = None
        self.stop_event = threading.Event()

    def run(self):
        self.thread = threading.Thread(target=self.__action)

    def _action(self):
        while True:
            # ret = self.capture.grab()
            # ret, frame = self.capture.retrieve()
            ret, frame = self.device.read()
            self._action_handler(ret)

            self.queue.put(frame)

            if self.stop_event.is_set():
                print '-----------------video capture thread stop.-----------------'
                break

            if self.queue.qsize() > self.WARNING_COUNT:
                print 'The VideoCapture is jamming. The queue size is: %d' % self.queue.qsize()

    @staticmethod
    def _action_handler(ret):
        pass

    def get(self):
        pass

    def stop(self):
        """
        stop thread
        """
        self.stop_event.set()
        self.queue.queue.clear()
        if self.thread:
            self.thread.join()
        if self.device:
            self.device.release()


class Camera(VideoCapture):
    def __init__(self):
        VideoCapture.__init__(self)

    def config(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps

    def run(self):
        self.device = cv2.VideoCapture(0)
        if not self.device.isOpened():
            raise IOError('cannot open camera')

        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.device.set(cv2.CAP_PROP_FPS, self.fps)
        print 'FPS is: %d.' % self.device.get(cv2.CAP_PROP_FPS)
        self.thread = threading.Thread(target=self._action)
        self.thread.start()

    @staticmethod
    def _action_handler(ret):
        if not ret:
            raise IOError('cannot read from USB camera')

    def get(self):
        """
        get frame list from video
        :return: frame list
        """
        frame = self.queue.get()
        return frame

    def capture(self, path, name, save):
        """
        get one frame from video
        :param path: image path
        :param name: image name
        :param save: if save the image
        :return: one frame
        """
        if not os.path.exists(path):
            raise IOError('cannot find path: %s' % path)

        self.__open()
        self.__config()

        ret, frame = self.device.read()
        if not ret:
            raise IOError('cannot read from USB camera')

        if save:
            full_path = os.path.join(path, name + '.png')
            ret = cv2.imwrite(full_path, frame)
            if ret:
                print 'camera.Camera.capture: capture picture in success'
            else:
                raise IOError('cannot save image: %s' % full_path)

        self.close()
        return frame


class Reader(VideoCapture):
    def __init__(self):
        VideoCapture.__init__(self)
        self._pause = False
        self._next_frame = False

    def _action_handler(self, ret):
        while self._pause:
            if self._next_frame:
                self._next_frame = False
                break
            time.sleep(0.0001)

        if not ret:
            self.stop_event.set()
        time.sleep(1.0 / self.fps)

    def pause(self):
        print 'pause'
        self._pause = True

    def resume(self):
        print 'resume'
        self._pause = False

    def speed_up(self):
        self.fps += 5
        if self.fps > 1000:
            self.fps = 1000
        print self.fps

    def slow_down(self):
        self.fps -= 5
        self.fps = int(self.fps)
        if self.fps < 1:
            self.fps = 1
        print self.fps

    def next_frame(self):
        # print 'next frame'
        self._next_frame = True

    def run(self, path, name):
        video_path = os.path.join(path, name)
        if not os.path.exists(video_path):
            raise IOError('cannot open video %s' % video_path)

        self.device = cv2.VideoCapture(video_path)
        print self.device.isOpened()
        self.fps = self.device.get(cv2.CAP_PROP_FPS)

        self.thread = threading.Thread(target=self._action)
        if not self.thread.isAlive():
            # TODO: set daemon report error when stop
            self.thread.setDaemon(True)
            self.stop_event.clear()
            self.queue.queue.clear()
            self.thread.start()

    def get(self):
        """
        get frame list from video
        :return: frame list
        """
        try:
            frame = self.queue.get()
        except Queue.Empty:
            print 'Video is over!'
            return None
        return frame

    @staticmethod
    def capture(path, name, save):
        """
        capture one frame from video
        :param path: image path
        :param name: image name
        :return: one frame
        """
        full_path = os.path.join(path, name + '.png')
        if os.path.exists(full_path):
            frame = cv2.imread(full_path)
            return frame
        else:
            raise IOError('cannot read video: %s' % full_path)


def new(offline):
    """
    get video source
    :param offline:
        if True, get video from camera
        else, get video from disk
    :return: camera or reader to generate video
    """
    if offline:
        return Reader()
    else:
        camera = Camera()
        camera.config(glb.camera_width, glb.camera_height, glb.camera_fps)
        return camera


if __name__ == '__main__':
    import scripts.basic.globals as glb
    import scripts.tools.file_rw as loader

    os.chdir(os.path.join('..', '..', '..', '..'))

    loader.init()

    OFFLINE = True

    _app = new(OFFLINE)
    if OFFLINE:
        _path = os.path.join(glb.device_name, glb.game_name)
        _name = 'clip.avi'
        _app.run(_path, _name)
    else:
        _app.run()
    while True:
        _frame = _app.get()
        if _frame is None:
            break
        cv2.imshow('rgb', _frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    _app.stop()

