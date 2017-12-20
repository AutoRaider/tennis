import time
import Queue
import threading

import os

import cv2


class VideoWriter:
    def __init__(self, path, name, fps=30, resolution=(1280, 720)):
        self.save_path = os.path.join(path, name)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(self.save_path, fourcc, fps, resolution)

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        print 'Save video in ', self.save_path
        self.writer.release()


class ClipWriter(VideoWriter):
    AIMING_FRAMES = 30

    def __init__(self, path, name, fps=30, resolution=(1280, 720)):
        VideoWriter.__init__(self, path, name, fps, resolution)
        self.queue = Queue.Queue()
        self.record = False

    def load(self, frame):
        self.queue.put(frame)
        if self.record:
            self.write(self.queue.get())
        if self.queue.qsize() > self.AIMING_FRAMES:
            self.queue.get()

    def begin(self):
        self.record = True

    def end(self):
        while self.queue.qsize() > 0:
            self.write(self.queue.get())
        self.record = False


class ImagesWrite:
    def __init__(self, path):
        self.path = path

    def write(self, frame, file_name):
        file_path = os.path.join(self.path, file_name)
        cv2.imwrite(file_path, frame)
        print '____Save %s in %s____' % (file_name, self.path)


if __name__ == '__main__':
    import scripts.basic.globals as glb
    import scripts.module.media.video.video_capture as capture

    OFFLINE = False

    _app = capture.new(OFFLINE)
    if OFFLINE:
        _path = os.path.join(glb.device_name, glb.game_name)
        _name = 'video.avi'
        _app.run(_path, _name)
    else:
        _path = os.path.join(glb.device_name, 'record')
        _app.run()

    _video_writer = VideoWriter(_path, 'pot9.avi')
    _images_writer = ImagesWrite(_path)
    _clip_writer = ClipWriter(_path, 'clip-debug.avi')
    while True:
        _frame = _app.get()

        if _frame is None:
            print 'Video is over.'
            break

        _video_writer.write(_frame)
        _clip_writer.load(_frame)
        cv2.imshow('rgb', _frame)

        _key = cv2.waitKey(1)
        if _key == ord('s'):
            _images_writer.write(_frame, 'test.jpg')
        elif _key == ord('q'):
            cv2.destroyAllWindows()
            break
        elif _key == ord('w'):
            _clip_writer.begin()
        elif _key == ord('e'):
            _clip_writer.end()

    _video_writer.release()
    _clip_writer.release()
    _app.stop()
