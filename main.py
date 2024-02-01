import os
import pickle

import cv2
import cvzone
import face_recognition
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import  storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancert-1cf09-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancert-1cf09.appspot.com"
})

bucket = storage.bucket()

# Here we have make the web cam with its ratio
cap = cv2.VideoCapture(0)
cap.set(3, 632)
cap.set(4, 465)
# taking bg image the main screen of app
imgbackground = cv2.imread('Resources/Main screen.jpg')

# Define the path to the folder containing mode images
folderModepath = 'Resources/Modes'

# Use os.listdir() to get a list of filenames in the specified folder
modePathList = os.listdir(folderModepath)

# Create an empty list to store the images corresponding to the filenames
imgModeList = []

# Iterate through each filename in the list

for path in modePathList:
    #reading multiple image files from a directory
    imgModeList.append(cv2.imread(os.path.join(folderModepath,path)))

# print(len(imgModeList))

#load the encoding file
print("Loading encoded file .....")

file = open("EncodeFile.p",'rb')
encodelistknownwithIDs = pickle.load(file)
file.close()
encodelistknown,StudentIds = encodelistknownwithIDs

print("Loaded encoded file ......")

modeType = 0
counter = 0
ids = -1
imgStudent =[]

while True:
    success, img = cap.read()

    # Flip the frame horizontally (inverted)
    img = cv2.flip(img, 1)

    imgS = cv2.resize(img, (0,0), None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    # overlay on main screen
    imgbackground[169:169+480, 58:58+640] = img
    imgbackground[42:42+635,790:790+464] = imgModeList[modeType]

    if faceCurFrame:


        for encoFace , faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encodelistknown,encoFace)
            facedis = face_recognition.face_distance(encodelistknown,encoFace)
            # print("matches :",matches)
            # print("face dis :",facedis)

            matchIndex = np.argmin(facedis)
            # print("Match Index :",matchIndex)

            if matches[matchIndex]:
                # print("known face detected")
                # print(StudentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4\

                bbox = 58 + x1, 169 + y1, x2 - x1, y2 - y1
                imgbackground = cvzone.cornerRect(imgbackground, bbox, rt=0)
                ids = StudentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgbackground,"loading",(280,425))
                    cv2.imshow("Face Attendance", imgbackground)
                    cv2.waitKey(1)
                    counter=1
                    modeType=1

        if counter!=0:
            if counter == 1:
                #Get the data
                studentInfo = db.reference(f'Students/{ids}').get()
                print(studentInfo)
                #get image from storage
                blob = bucket.get_blob(f'Images/{ids}.jpg')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGR2RGB)
                #Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last-Attendance-time'],
                                                  '%Y-%m-%d %H:%M:%S')
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed>30:
                    ref = db.reference(f'Students/{ids}')
                    studentInfo['total-attendance']+=1
                    ref.child('total-attendance').set(studentInfo['total-attendance'])
                    ref.child('last-Attendance-time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    modeType = 3
                    counter = 0
                    imgbackground[42:42 + 635, 790:790 + 464] = imgModeList[modeType]

            if modeType!=3:
                if 10<counter<20:
                    modeType = 2
                imgbackground[42:42 + 635, 790:790 + 464] = imgModeList[modeType]

                if counter<=10:



                    cv2.putText(imgbackground,str(studentInfo['total-attendance']),(863,135),
                                cv2.FONT_HERSHEY_TRIPLEX,1,(255,255,255),1)
                    cv2.putText(imgbackground, str(studentInfo['major']), (1007, 547),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgbackground, str(ids), (1007, 505),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgbackground, str(studentInfo['Standing']), (940, 633),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                    cv2.putText(imgbackground, str(studentInfo['Year']), (1050, 633),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                    cv2.putText(imgbackground, str(studentInfo['starting-year']), (1150, 633),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 0.5, 1)
                    offset = (464 - w) // 2
                    cv2.putText(imgbackground, str(studentInfo['name']), (790 + offset, 588),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                    imgStudent = cv2.resize(imgStudent, (236, 236))
                    imgbackground[215:215+236,904:904+236] = imgStudent

                counter+=1

                if counter>=20:
                    counter=0
                    modeType=0
                    studentInfo=[]
                    imgStudent=[]
                    imgbackground[42:42 + 635, 790:790 + 464] = imgModeList[modeType]



            # x, y, w, h = 58 + x1, 169 + y1, x2 - x1, y2 - y1
            # cv2.rectangle(imgbackground, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # cv2.imshow("Webcam", img)
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Face Attendance", imgbackground)
    cv2.waitKey(1)
