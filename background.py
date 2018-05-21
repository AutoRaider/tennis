import numpy
import cv2
from video_capture import SimpleCapture
from config import config
from calibration import Calibrater, calculate_remap, trasform_remap, warper

class BGExtractor:
    def __init__(self):
        self.bg = cv2.createBackgroundSubtractorMOG2()

    def apply(self, frame):
        assert len(frame.shape) > 2
        mask = self.bg.apply(frame)
        mask = mask[:, :, numpy.newaxis]
        return frame*mask

if __name__ == '__main__':
    reader = SimpleCapture(path='data', name='tennis.mp4')

    # camera.run(path='data', name='tennis.mp4')
    #
    # _frame = camera.get()
    # camera.pause()
    # pause fetching frames from capture
    # build configuration object
    cfgs = config()
    trans_param = cfgs.load_trans_param()
    ret, _frame = reader.read()
    shape = _frame.shape
    cal = Calibrater(_frame, img_size=shape[-2::-1], width=cfgs.tennis_width, height=cfgs.tennis_height, data_path='./data/tennis.bin')
    trans_frame = cal.transform_image(_frame)

    map_x, map_y = calculate_remap(trans_frame, gamma=trans_param['r'], threshold=trans_param['th'], warper=warper)

    mainwin = 'rgb'
    cv2.namedWindow(mainwin)

    fgbg = cv2.createBackgroundSubtractorMOG2()

    print 'init ok'

    while True:
        # time.sleep(0.1)
        ret, _frame = reader.read()
        if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
            break

        trans_frame = cal.transform_image(_frame)
        warped = trasform_remap(trans_frame, map_x, map_y)
        fgmask = fgbg.apply(warped)
        cv2.imshow(mainwin, fgmask)
        reader.wait()

    print(fgmask.shape)

