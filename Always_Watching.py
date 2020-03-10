#Sean Nishi
#python version of my Always Watching security software

#need to put classifiers in an list so 

from threading import Thread
import cv2
import datetime
import concurrent.futures

############################################################################################
#creates a thread to retrieve frames
class GetVideo:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.stream.read()
        self.thread = None
        self.stopped = False

    def start(self):
        self.thread = Thread(target = self.get, args = ()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True

############################################################################################
#creates a thread to display frames
class ShowVideo:
    def __init__(self, frame = None):
        self.frame = frame
        self.thread = None
        self.stopped = False

    def start(self):
        self.thread = Thread(target = self.show, args = ()).start()
        return self

    def show(self):
        while not self.stopped:
            cv2.imshow("Video", self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True

############################################################################################
#generic class to create a thread to do work, obsolete now
class DetectStuff:
    def __init__(self, frame = None):
        self.frame = frame
        self.copyFrame = self.frame
        self.classifier = None
        self.detect = None
        self.thread = None
        self.stopped = False

    def start(self, casClassPath):
        self.classifier = cv2.CascadeClassifier(casClassPath)
        if not self.classifier:
            print("ERROR: bad path for classifier")
            exit(1)

        print(self.classifier)

        self.thread = Thread(target = self.detect, args = ()).start()
        return self

    def detect(self):
        while not self.stopped:
            print("tick detect")
            #detect stuff
            self.copyFrame = self.frame
            self.detect = self.classifier.detectMultiScale(self.copyFrame, scaleFactor = 1.1, minNeighbors = 5, minSize = (30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

            for(x, y, w, h) in self.detect:
                self.copyFrame = cv2.ellipse(self.copyFrame, (x+0.5*w, y+0.5*h), (w+0.5, h*0.5), 0, 0, 360, (255, 0, 255), 1)

            return self.copyFrame
            #if cv2.waitKey(1) == ord("q"):
            #    self.stopped = true

    def stop(self):
        self.stopped = True

############################################################################################
#function given to a thread
#Input: current frame we will look at, xml classifier path
#Output: returns a copy of the input frame with ellipses drawn on areas of interest
def detect(frame, path):
    copyFrame = frame
    classifier = cv2.CascadeClassifier(path)
    if not classifier:
        print("ERROR: bad path for classifier")
        exit(1)

    detect = classifier.detectMultiScale(copyFrame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    for(x, y, w, h) in detect:
        copyFrame = cv2.ellipse(img=copyFrame, center=(int(x+0.5*w), int(y+0.5*h)), axes=(int(w*0.5), int(h*0.75)), angle=0, startAngle=0, endAngle=360, color=(255, 0, 255), thickness=1)
    return copyFrame

############################################################################################
#creates threads for grabbing and showing video frames
#main thread passes the frames between them
def threads4All(src = 0):
    getter = GetVideo(src).start()
    shower = ShowVideo(src).start()

    while True:
        #stop check
        if getter.stopped or shower.stopped:
            getter.stop()
            shower.stop()
            break

        #wont continue until the threads join()
        #I hope I know what im doing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            face_future = executor.submit(detect, getter.frame, face_class_path)
            prof_future = executor.submit(detect, getter.frame, profface_class_path)

        #combine images to display one image
        finalImage = cv2.add(face_future.result(), prof_future.result())
        #show final
        shower.frame = finalImage
        
########################################################################

face_class_path = "D:/opencv/sources/data/haarcascades/haarcascade_frontalface_alt.xml"
profface_class_path = "D:/opencv/sources/data/haarcascades/haarcascade_profileface.xml"
working = False

threads4All(0)