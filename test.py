from video_capture import Reader
from video_writer import VideoWriter
import cv2

if __name__ == '__main__':
    # camera = Reader()
    #
    # camera.run(path='data', name='tennis.mp4')
    #
    # _frame = camera.get()
    # shape = _frame.shape

    camera = cv2.VideoCapture('data/tennis.mp4')

    if not camera.isOpened():
        raise Exception
    writer = VideoWriter(path='./data', name='tennis_trans.mp4', fps=camera.get(cv2.CAP_PROP_FPS),
                         resolution=(int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))), isColor=1)
    mainwin = 'test'

    while True:
        ret, _frame = camera.read()
        if not ret:
            break
        writer.write(_frame)
        cv2.imshow(mainwin, _frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.stop()
    writer.release()