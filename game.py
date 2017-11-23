import cv2
import video_capture as camera
from calibration import Calibrater
from calibration import trasform_remap, warper, inverse_warper, calculate_remap
from geometry import Point
import numpy as np
import math

class MyTracker:
    def __init__(self, frame, bbox=None, color=(0, 0, 255)):
        self.tracker = cv2.TrackerKCF.create()
        print self.tracker.getDefaultName()
        # self.tracker.create(cv2.TrackerKCF_CN)
        self.color = color
        self.bbox = bbox
        self.center = (0, 0)
        if self.bbox:
            res = self.tracker.init(frame, self.bbox)
            print 'Tracker init: ', res
        else:
            print 'Please select  ROI.'
            self.bbox = cv2.selectROI('Select bbox', frame)
            res = self.tracker.init(frame, self.bbox)
            print 'Tracker init: ', res

    def update(self, frame):
        res, self.bbox = self.tracker.update(frame)
        if res:
            p1 = (int(self.bbox[0]), int(self.bbox[1]))
            p2 = (int(self.bbox[0] + self.bbox[2]), int(self.bbox[1] + self.bbox[3]))
            cv2.rectangle(frame, p1, p2, self.color, 2, 1)
            self.center = (self.bbox[0]+self.bbox[2]/2, self.bbox[1]+self.bbox[3])
            return self.center
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)
            self.center = (0, 0)
            return False

def rgbMouseCallback(event, x, y, flag, para):
    """
    mouse event on rgb window
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        # add strike points
        mp = para[0]
        striker = mp['current_striker']
        tracker = mp['trackers'][striker]
        mp['current_striker'] = 1 - mp['current_striker']
        center = tracker.center
        p = Point(center[0], h - inverse_warper(h - center[1], a, b, m, gamma, threshold))
        mp['strike_points'][striker].append(p)
        print('strike_points: ')
        print('player1: ' + str([str(p) for p in mp['strike_points'][0]]))
        print('player2: ' + str([str(p) for p in mp['strike_points'][1]]))

if __name__ == '__main__':
    camera = camera.Reader()

    camera.run(path='data', name='tennis.mp4')

    _frame = camera.get()
    camera.pause()
    # pause fetching frames from capture
    tennis_width = 600
    tennis_height = 900
    shape = _frame.shape
    cal = Calibrater(_frame, img_size=shape[-2::-1], width=tennis_width, height=tennis_height, data_path='./data/tennis.bin')
    trans_frame = cal.transform_image(_frame)
    h = tennis_height
    gamma = 2.5
    threshold = tennis_height * 2.0 / 3.0
    a = 1.0 / (gamma * math.pow(threshold, gamma - 1))
    m = h - math.pow(float(h), gamma) * a
    b = (1.0 - gamma) / gamma * threshold + m
    map_x, map_y = calculate_remap(trans_frame, gamma=gamma, threshold=threshold, warper=warper)
    warped = trasform_remap(trans_frame, map_x, map_y)

    # bbox1 = (880, 430, 120, 150)
    # bbox2 = (530, 60, 80, 90)
    bbox1 = None
    bbox2 = None

    tracker1 = MyTracker(warped, bbox1, color=(255, 0, 0))
    tracker2 = MyTracker(warped, bbox2)
    # calibrate capture perspective

    camera.resume()
    current_striker = 0
    strike_point = [[], []]

    mouse_callback_param = dict()
    mouse_callback_param['strike_points'] = strike_point
    mouse_callback_param['current_striker'] = current_striker
    mouse_callback_param['trackers'] = [tracker1, tracker2]
    mouse_callback_param['calibrater'] = cal
    mainwin = 'rgb'
    cv2.namedWindow(mainwin)
    cv2.setMouseCallback(mainwin, rgbMouseCallback, [mouse_callback_param])

    p1 = (50, 600)
    p2 = (250, 600)
    p3 = (50, 300)
    p4 = (250, 300)

    micro_win_points = np.array([p1, p2, p4, p3])

    print 'init ok'

    while True:
        # time.sleep(0.1)
        _frame = camera.get()
        timer = cv2.getTickCount()

        trans_frame = cal.transform_image(_frame)
        warped = trasform_remap(trans_frame, map_x, map_y)

        center1 = tracker1.update(warped)
        center2 = tracker2.update(warped)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # Display tracker type on frame
        cv2.putText(_frame, " Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

        # Display FPS on frame
        cv2.putText(_frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)
        cv2.fillConvexPoly(_frame, micro_win_points, (200, 0, 60))

        if center1:
            x = int(center1[0] / tennis_width * 200 + 50)
            y = int((h - inverse_warper(h - center1[1], a, b, m, gamma, threshold)) / tennis_height * 300 + 300)
            cv2.circle(_frame, (x, y), 10, (0, 0, 255), thickness=-1)
        if center2:
            x = int(center2[0] / tennis_width * 200 + 50)
            y = int((h - inverse_warper(h - center2[1], a, b, m, gamma, threshold)) / tennis_height * 300 + 300)
            cv2.circle(_frame, (x, y), 10, (255, 255, 0), thickness=-1)

        for p in strike_point[0]:
            x = int(p.tuple()[0] / tennis_width * 200 + 50)
            y = int(p.tuple()[1] / tennis_height * 300 + 300)
            cv2.circle(_frame, (x, y), 10, (0, 0, 255), thickness=3)
        for p in strike_point[1]:
            x = int(p.tuple()[0] / tennis_width * 200 + 50)
            y = int(p.tuple()[1] / tennis_height * 300 + 300)
            cv2.circle(_frame, (x, y), 10, (255, 255, 0), thickness=3)

        cv2.imshow(mainwin, _frame)
        # cv2.imshow('warp', warped)
        # cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cal.save_table_corner(output_path='./data/tennis.bin')
    cv2.destroyAllWindows()
    camera.stop()
