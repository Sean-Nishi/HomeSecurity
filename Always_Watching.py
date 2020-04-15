#Sean Nishi
#python version of my Always Watching security software

#TODO:
#1. need to put classifiers into a list so it's easy to search and expand for different things
#2. need to save video and after x-hours of recording, start new video, save old one, send old one to main computer
#3. need to take picture whenever a new person comes into view, send to main computer
#4. update database when we detect a new number of things we want to detect
#5. expand program to incoporate more than one camera, if >1 camera then create a thread for each extra camera
#6. need to add the commands for sending the pictures to google drive or something.


#create threads for detecting but in a class so we can pass new info to the threads w/o creating new ones each time

from threading import Thread
import cv2
import datetime
import time
import concurrent.futures


#use database to store the number of detected things per thing we detect.
#using mqtt

############################################################################################
#creates a thread to retrieve frames
class GetVideo:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(0)
        self.frame_width = int(self.stream.get(3))
        self.frame_height = int(self.stream.get(4))
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
#function given to a thread
#Input: current frame we will look at, xml classifier path
#Output: returns a copy of the input frame with ellipses drawn on areas of interest, also updates database with new entry
def detect(frame, path):
    copyFrame = frame
    classifier = cv2.CascadeClassifier(path)
    if not classifier:
        print("ERROR: bad path for classifier")
        exit(1)

    detect = classifier.detectMultiScale(copyFrame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    #update database if something is detected
    #if not detect 

    #for coords for detected thing draw ellipse
    for(x, y, w, h) in detect:
        copyFrame = cv2.ellipse(img=copyFrame, center=(int(x+0.5*w), int(y+0.5*h)), axes=(int(w*0.5), int(h*0.75)), angle=0, startAngle=0, endAngle=360, color=(255, 0, 255), thickness=1)


    return copyFrame#, detect

############################################################################################
#creates threads for grabbing and showing video frames
#main thread passes the frames between them
def threads4All(src = 0):

    #threads to get and display video
    getter = GetVideo(src).start()
    shower = ShowVideo(src).start()
    time.sleep(1)

    #output video
    recording = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (getter.frame_width, getter.frame_height))

    num_faces = -1

    while True:
        if getter.stopped or shower.stopped:
            getter.stop()
            shower.stop()
            break

        #wont continue until the threads join()
        #need to get data back from thread besides the frame with ovals on detected objects...
        if getter.frame is not None:
            #make sure work is done on the same frame
            now = getter.frame
            with concurrent.futures.ThreadPoolExecutor() as executor:
                face_future = executor.submit(detect, now, face_class_path)
                prof_future = executor.submit(detect, now, profface_class_path)

            #combine images to display one image
            finalImage = cv2.add(face_future.result(), prof_future.result())

            #old code to save a new picture
            """
            if num_faces is -1:
                num_faces = detected_face_data.size()

            if num_faces < detected_face_data.size():
                #need to add the time on the image in cornor of picture
                temp_path = new_person_pic_path
                append(temp_path, string(new_num_faces))
                cv2.imwrite(new_person_pic_path, finalImage)
                new_num_faces+1
            """
            #give image to shower
            shower.frame = finalImage
            #save frame to recording
            recording.write(finalImage)

    #cleanup
    recording.release()
    cv2.destroyAllWindows()
        
########################################################################
#paths to classifiers and init stuff
face_class_path = "D:/opencv/sources/data/haarcascades/haarcascade_frontalface_alt.xml"
profface_class_path = "D:/opencv/sources/data/haarcascades/haarcascade_profileface.xml"

new_num_faces = 0

new_person_pic_path = "C:/Users/Installation02/source/repos/Always_Watching/Pictures/New_Faces/Detected Face "

working = False

#start the program
threads4All(0)