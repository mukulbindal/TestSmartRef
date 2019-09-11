from imageai.Detection import ObjectDetection
import os
import random
import h5py

class ModelOfHell:
    def __init__(self):
        self.execution_path = os.getcwd()
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(os.path.join(self.execution_path , "./restorent/yolo.h5"))
        self.detector.loadModel()

    def apna_model(self):        
        d = {"banana":0,"pineapple":0,"cabbage":0,"fanta":0,"capsicum":0}
        # try:.join(execution_path , "./restorent/image1.jpg"), output_image_path=os.path.join(execution_path , "./restorent/image1.jpg"))
        # except Exception as e:
        #     print(type(e).__name__)
        #     detections = detector.detectObjectsFromImage(input_image=os.path
        #     detections={"nothing":"detected"
        detections = self.detector.detectObjectsFromImage(input_image=os.path.join(self.execution_path , "./restorent/image1.jpg"), output_image_path=os.path.join(self.execution_path , "./restorent/image2.jpg"))
        print(detections)
        for eachObject in detections:
            try:
                object_name = eachObject["name"]
                if(eachObject["percentage_probability"]>50):
                    if object_name=="bottle":
                        object_name = "fanta"
                    d[object_name.lower()] += 1
            except:
                pass
            
        #print(eachObject["name"] , " : " , eachObject["percentage_probability"])

        #print(d)
        return d




