import cv2
import os
# import shelve
import numpy
# import math
from calibration import Calibrater

# from transform import Corner
import geometry as ge
print(os.getcwd())

origin = os.path.dirname(os.getcwd())
target_path = "/alphapose/badminton.jpg"
target_img = origin + target_path


if __name__ == '__main__':
    people = ge.Point(394,472)
    image = cv2.imread(target_img)
    size = image.shape
    tennis_width = 300
    tennis_height = 400
    # flag = int(input("If you have the transform matrix? \nYes: press '1', No:press '2'\n"))
    # if flag == 2:
    #     print('hhhhhhhhhhhhhhhhhhhhhhh')
    #     cal = Calibrater(image, img_size=size[-2::-1], width=tennis_width, height=tennis_height, data_path=None)
    #     mat = cal._get_trans_matrix()
    #     numpy.savetxt('mat_1.csv', mat, delimiter = ',')
    
    print(size)
    print('origin position:', people)
    # print("origin:", mat)


    my_matrix = numpy.loadtxt(open("mat.csv","rb"),delimiter=",",skiprows=0) 

    print("read origin:", my_matrix)

    people_transf = people.perspective(my_matrix)
    print('++++++++++++++++++:',type(people_transf))
    # pp = cal.transform_point(p)

    print('transform position:', people_transf.int())
    people_transf = people_transf.int().tuple()

###########################################################
    court = cv2.imread("court|.png")
    # court = court[140:705, 160:390, :]
    court = court[140:705, 164:387, :]
    scale = (300,400)
    court = cv2.resize(court, scale) 
###########################################################
    cv2.circle(court, people_transf, 3, (0,0,0),10)
    cv2.imshow('court',court)
    cv2.waitKey()
###########################################################
    # cal = Calibrater(image, img_size=size[-2::-1], width=tennis_width, height=tennis_height, data_path=None)
    # perspective = cal.transform_image(image)
    # cv2.imshow('perspective',perspective)
    # cv2.waitKey()

    # #warp = trasform_remap(perspective, 1.5, float(1)/2*tennis_height, warper=warper)
    # #invwarp = trasform_remap(warp, 1.5, float(1) / 2 * tennis_height, warper=inverse_warper)
    # mx1, my1 = calculate_remap(perspective, 0.1, float(1)/2*tennis_height, warper=warper)
    # cv2.imshow('mask table', perspective)
    # cv2.moveWindow('mask table', 100, 100)
    # warp = trasform_remap(perspective, mx1, my1)
    # cv2.imshow('warp table', warp)
    # #cv2.imshow('invwarp table', invwarp)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cal.save_table_corner(output_path='./data/tennis.bin')
