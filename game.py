import cv2
import video_capture as camera
from calibration import Calibrater
from calibration import trasform_remap, warper, inverse_warper, calculate_remap
from geometry import Point
from config import config
from video_writer import VideoWriter
from background import BGExtractor

class MyTracker:
    def __init__(self, frame, bbox=None, color=(0, 0, 255)):
        self.tracker = cv2.TrackerKCF.create()
        #self.tracker = TrackerCam()
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
            self.center = (self.bbox[0]+self.bbox[2]/2, self.bbox[1] + self.bbox[3])
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
        p = Point(center[0], cfgs.tennis_height - inverse_warper(cfgs.tennis_height - center[1], **trans_param))
        mp['strike_points'][striker].append(p)
        print('strike_points: ')
        print('player1: ' + str([str(p) for p in mp['strike_points'][0]]))
        print('player2: ' + str([str(p) for p in mp['strike_points'][1]]))


def DrawMiniWindow(frame, center1, center2):

    # draw a mini stadium diagram
    cv2.fillConvexPoly(frame, cfgs.micro_window, cfgs.micro_window_color)
    mini_h = cfgs.micro_window_h
    mini_w = cfgs.micro_window_w
    mini_x = cfgs.micro_window_x
    mini_y = cfgs.micro_window_y

    delta_w = mini_w/8
    delta_h = mini_h/10

    cv2.line(frame,(mini_x, mini_y+delta_h),(mini_x+mini_w,mini_y+delta_h),(255,255,255), 2)
    cv2.line(frame, (mini_x, mini_y + mini_h - delta_h), (mini_x + mini_w, mini_y + mini_h - delta_h), (255, 255, 255), 2)
    cv2.line(frame, (mini_x + delta_w, mini_y + delta_h), (mini_x + delta_w, mini_y + mini_h - delta_h), (255, 255, 255), 2)
    cv2.line(frame, (mini_x + mini_w - delta_w, mini_y + delta_h), (mini_x + mini_w - delta_w, mini_y + mini_h - delta_h), (255, 255, 255),2)
    cv2.line(frame,(mini_x + delta_w, mini_y+mini_h/2), (mini_x + mini_w - delta_w, mini_y+mini_h/2),(255,255,255), 2)

    if center1:
        x = int(center1[0] / cfgs.tennis_width * mini_w + mini_x)
        y = int((cfgs.tennis_height - inverse_warper(cfgs.tennis_height - center1[1], **trans_param)) / cfgs.tennis_height * mini_h + mini_y)
        cv2.circle(frame, (x, y), 10, cfgs.player_colors[0], thickness=-1)
    if center2:
        x = int(center2[0] / cfgs.tennis_width * mini_w + mini_x)
        y = int((cfgs.tennis_height - inverse_warper(cfgs.tennis_height - center2[1], **trans_param)) / cfgs.tennis_height * mini_h + mini_y)
        cv2.circle(frame, (x, y), 10, cfgs.player_colors[1], thickness=-1)

    for p in strike_point[0]:
        x = int(p.tuple()[0] / cfgs.tennis_width * mini_w + mini_x)
        y = int(p.tuple()[1] / cfgs.tennis_height * mini_h + mini_y)
        cv2.circle(frame, (x, y), 10, cfgs.player_colors[0], thickness=3)
    for p in strike_point[1]:
        x = int(p.tuple()[0] / cfgs.tennis_width * mini_w + mini_x)
        y = int(p.tuple()[1] / cfgs.tennis_height * mini_h + mini_y)
        cv2.circle(frame, (x, y), 10, cfgs.player_colors[1], thickness=3)

    return frame

if __name__ == '__main__':
    reader = camera.SimpleCapture(path='data', name='tennis.mp4')

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
    warped = trasform_remap(trans_frame, map_x, map_y)
    bg = BGExtractor()
    # warped = bg.apply(warped)

    bbox1 = None
    bbox2 = None

    tracker1 = MyTracker(warped, bbox1, color=cfgs.player_colors[0])
    tracker2 = MyTracker(warped, bbox2, color=cfgs.player_colors[1])
    # calibrate capture perspective
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

    writer = VideoWriter('./data', 'tennis_trans.mp4', fps=int(reader.fps), resolution=reader.size, isColor=1)

    print 'init ok'

    while True:
        # time.sleep(0.1)
        ret, _frame = reader.read()
        if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
            break

        timer = cv2.getTickCount()

        trans_frame = cal.transform_image(_frame)
        warped = trasform_remap(trans_frame, map_x, map_y)
        # warped = bg.apply(warped)

        center1 = tracker1.update(warped)
        center2 = tracker2.update(warped)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # Display tracker type on frame
        cv2.putText(_frame, " Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)

        # Display FPS on frame
        cv2.putText(_frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 0, 255), 2)

        _frame = DrawMiniWindow(_frame, center1, center2)

        if cfgs.save:
            writer.write(_frame)
        cv2.imshow(mainwin, _frame)
        reader.wait()
        # save video
        cv2.imshow('warp', warped)
        # cv2.waitKey(0)

    writer.release()
    cal.save_table_corner(output_path='./data/tennis.bin')
    cv2.destroyAllWindows()

