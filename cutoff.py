import video_writer
import os
import cv2
import queue



if __name__ == '__main__':
	OFFLINE = False
	origin = os.getcwd()
	video_path = os.path.join(origin, 'badminton.mp4')
	print(video_path)
	device = cv2.VideoCapture(video_path)
	num = device.get(cv2.CAP_PROP_FRAME_COUNT)
	fps = device.get(cv2.CAP_PROP_FPS)
	size = ((int(device.get(cv2.CAP_PROP_FRAME_WIDTH)),int(device.get(cv2.CAP_PROP_FRAME_HEIGHT))))
	print(size)
	success = True
	frame_queue = queue.Queue()

	success, frame = device.read()
	frame_queue.put(frame)
	for i in range(60):
		success, frame = device.read()
		frame_queue.put(frame)

	# _video_writer = VideoWriter(origin, 'badminton.mp4')
	# _clip_writer = ClipWriter(_path, 'clip-debug.avi')

	save_path = os.path.join(origin, 'test.avi')

	fourcc = cv2.VideoWriter_fourcc(*'XVID')
	video_writer = cv2.VideoWriter(save_path, fourcc, 30, (1920, 1080), 1)

	# _video_writer = video_writer.VideoWriter(origin, 'test.avi')


	for i in range(60):
		img = frame_queue.get()
		# _video_writer.write(img)
		video_writer.write(img)
		# cv2.imshow('rgb', img)
		# cv2.waitKey()
	video_writer.release()

    # _app = capture.new(OFFLINE)
    # if OFFLINE:
    #     _path = os.path.join(glb.device_name, glb.game_name)
    #     _name = 'video.avi'
    #     _app.run(_path, _name)
    # else:
    #     _path = os.path.join(glb.device_name, 'record')
    #     _app.run()

    # _video_writer = VideoWriter(_path, 'pot9.avi')
    # _images_writer = ImagesWrite(_path)
    # _clip_writer = ClipWriter(_path, 'clip-debug.avi')
    # while True:
    #     _frame = _app.get()

    #     if _frame is None:
    #         print( 'Video is over.')
    #         break

    #     _video_writer.write(_frame)
    #     _clip_writer.load(_frame)
    #     cv2.imshow('rgb', _frame)

    #     _key = cv2.waitKey(1)
    #     if _key == ord('s'):
    #         _images_writer.write(_frame, 'test.jpg')
    #     elif _key == ord('q'):
    #         cv2.destroyAllWindows()
    #         break
    #     elif _key == ord('w'):
    #         _clip_writer.begin()
    #     elif _key == ord('e'):
    #         _clip_writer.end()

    # _video_writer.release()
    # _clip_writer.release()
    # _app.stop()
