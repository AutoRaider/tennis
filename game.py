import cv2
import video_capture as camera
from calibration import Calibrater
from geometry import Point

class MyTracker:
    def __init__(self, frame, bbox=None, color=(0, 0, 255)):
        self.tracker = cv2.TrackerKCF.create()
        print self.tracker.getDefaultName()
        # self.tracker.create(cv2.TrackerKCF_CN)
        self.color = color
        self.bbox = bbox
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
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)

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
        bbox = tracker.bbox
        p = Point(int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3]))
        trans_p = mp['calibrater'].transform_point(p)
        mp['strike_points'][striker].append(trans_p)
        print('strike_points: ')
        print('player1: ' + str([str(p) for p in mp['strike_points'][0]]))
        print('player2: ' + str([str(p) for p in mp['strike_points'][1]]))

if __name__ == '__main__':
    camera = camera.Reader()

    camera.run(path='data', name='tennis.mp4')

    _frame = camera.get()
    camera.pause()
    # pause fetching frames from capture
    bbox1 = (880, 430, 120, 150)
    bbox2 = (530, 60, 80, 90)

    tracker1 = MyTracker(_frame, bbox1, color=(255, 0, 0))
    tracker2 = MyTracker(_frame, bbox2)
    # calibrate capture perspective
    tennis_width = 600
    tennis_height = 1000
    shape = _frame.shape
    cal = Calibrater(_frame, img_size=shape[-2::-1], width=tennis_width,height=tennis_height, data_path='./data/tennis_cal.bin')

    camera.resume()
    current_striker = 0
    strike_point = [[],[]]

    mouse_callback_param = dict()
    mouse_callback_param['strike_points'] = strike_point
    mouse_callback_param['current_striker'] = current_striker
    mouse_callback_param['trackers'] = [tracker1, tracker2]
    mouse_callback_param['calibrater'] = cal
    mainwin = 'rgb'
    cv2.namedWindow(mainwin)
    cv2.setMouseCallback(mainwin, rgbMouseCallback, [mouse_callback_param])

    print 'init ok'

    while True:
        # time.sleep(0.1)
        _frame = camera.get()
        timer = cv2.getTickCount()

        tracker1.update(_frame)
        tracker2.update(_frame)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # Display tracker type on frame
        cv2.putText(_frame, " Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

        # Display FPS on frame
        cv2.putText(_frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)
        cv2.imshow(mainwin, _frame)
        # cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cal.save_table_corner(output_path=None)
    cv2.destroyAllWindows()
    camera.stop()
