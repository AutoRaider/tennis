import json
import os


origin = os.path.dirname(os.getcwd())
target_json = "/alphapose/alphapose-results.json"
origin = origin + target_json
print(origin)


# with open(origin, encoding='utf-8') as f:
#     line = f.readline()
#     d = json.loads(line)
#     print(len(d))
d = []
with open(origin, 'r', encoding='utf-8') as f:
	try:
	    while True:
	        line = f.readline()
	        if line:
	            d.extend(json.loads(line))
	            # print(len(d))
	        else:
	            break
	except:
	    f.close()
print(len(d))

# image_id = d[0]['image_id']
# category_id = d[0]['category_id']
# score = d[0]['score']
keypoints = d[0]['keypoints']
print(type(d[0]))
print(type(keypoints))
print('len of keypoints:', len(keypoints))
print(keypoints[15], keypoints[16])
print(keypoints)
# print(d[0])
flag_id = d[0]['image_id']
flag = 0
for i in range(len(d)):
	if i == len(d)-1:
		flag = flag+1
		print(flag)
	elif flag_id == d[i]['image_id']:
		flag = flag+1
	else:
		print(flag,flag_id,d[i]['image_id'] )
		flag_id = d[i]['image_id']
		flag = 1
	
	# print(d[i]['image_id'])
	# print('keypoints:', d[i]['keypoints'][15], d[i]['keypoints'][16])
num = 0
for i in range(len(d)):
	if d[i]['image_id'] == '504.jpg':
		num = num+1
print('num:', num)


print(len(d))
print(type(d))

# print('\nimage_id:', image_id)
# print('\ncategory_id:', category_id)
# print('\nscore', score)
# print('\nkeypoints', keypoints)


