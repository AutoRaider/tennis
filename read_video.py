import os
import cv2
import video_capture as camera
import queue
import numpy as np
# court: 565*230
# -: [140:370, 140:705, :] scale = (400,200)
# |: [140:705, 160:390, :] scale = (200,400)
# reader = camera.SimpleCapture(path='data', name='tennis.mp4')
origin = os.getcwd()
video_path = os.path.join(origin, 'badminton.mp4')
device = cv2.VideoCapture(video_path)

i = 1
# num = device.get(cv2.CAP_PROP_FRAME_COUNT)
# fps = device.get(cv2.CAP_PROP_FPS)
# size = ((int(device.get(cv2.CAP_PROP_FRAME_WIDTH)),int(device.get(cv2.CAP_PROP_FRAME_HEIGHT))))

while(device.isOpened()):
    ret, frame = device.read()
    if i%10 == 0:
    	# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    	print(i%10, i)
    	cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i=i+1
print(i)

success = True
frame_queue = queue.Queue()

# success, frame = device.read()
# frame_queue.put(frame)


# while success:
# 	success, frame = device.read()
# 	frame_queue.put(frame)
# 	print(i)
# 	i=i+1

image = frame_queue.get()
# cv2.imwrite(origin+"/demo.png", image)

court = cv2.imread("court|.png")
court = court[140:705, 160:390, :]

scale = (300,400)
resize_court = cv2.resize(court, scale)	

(h,w) = resize_court.shape[:2]
# center = ((50,50),(100,100))
center1 = (50,50)
center2 = (100,100)
# color = np.random.randint(0, high=256, size=3)

cv2.circle(resize_court, center1, 3, (0,0,0),10)
cv2.circle(resize_court, center2, 3, (0,0,0),10)

image[size[1]-scale[1]:size[1], size[0]-scale[0]:size[0], :] = resize_court
image = cv2.resize(image, (0, 0), fx=0.8, fy=0.8, interpolation=cv2.INTER_NEAREST)

cv2.imshow('court',image)
cv2.waitKey()																																


print("frame:", num)

# print("number:", frame_queue.qsize())

# i=0
# while i <= 5:
# 	i += 1
# 	print(i)
# 	qq = frame_queue.get()
# 	cv2.imshow('image', qq)
# 	cv2.waitKey(0)

# qq = qu.get()
# cv2.imshow('image', qq)
# cv2.waitKey()
# print(qq)
print(fps)
print(size[0])
