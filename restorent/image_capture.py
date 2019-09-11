import cv2
import numpy as np
import requests
def putimage(i):
	img_res = requests.get("http://192.168.43.79:8080/shot.jpg")
	img_arr = np.array(bytearray(img_res.content) , dtype = np.uint8)
	img = cv2.imdecode(img_arr , -1)
	cv2.imwrite("./restorent/image"+str(i)+".jpg" , img)


	
	# cap = cv2.VideoCapture(1)

	# #i = 1
	# r,f = cap.read()
 #    cv2.imwrite("image"+str(i)+".jpg",f)
 #    cv2.waitKey(6000)
 #    i += 1
 #    cap.release()


