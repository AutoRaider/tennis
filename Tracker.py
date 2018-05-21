import cv2
import numpy

class TrackerCam:
    def __init__(self):
        self.hsv_roi = None
        self.mask = None
        self.roi_hist = None
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 15, 1)

    def getDefaultName(self):
        return "CamshiftTracker"

    def init(self, frame, bbox):
        try:
            # set up the ROI for tracking
            self.box = bbox
            roi = frame[bbox[1]:(bbox[1] + bbox[3]), bbox[0]:(bbox[0] + bbox[2]), :]
            self.hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            self.mask = cv2.inRange(self.hsv_roi, numpy.array((0., 60., 32.)), numpy.array((180., 255., 255.)))
            self.roi_hist = cv2.calcHist([self.hsv_roi], [0], self.mask, [180], [0, 180])
            cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
            return True
        except:
            return False

    def update(self, frame):
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
            # apply meanshift to get the new location and update track window in trackers
            ret, self.box = cv2.meanShift(dst, self.box, self.term_crit)
            return True, self.box
        except:
            return False