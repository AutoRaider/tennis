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
print(len(keypoints))
# print('\nimage_id:', image_id)
# print('\ncategory_id:', category_id)
# print('\nscore', score)
# print('\nkeypoints', keypoints)


