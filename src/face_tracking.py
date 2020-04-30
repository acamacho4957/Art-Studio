import cv2
import sys

import keras
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model, load_model
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D, AveragePooling2D

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

# model = load_model('emotion_model.h5')
model = load_model('models/model_3.h5')

emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

def label_image(model, img):
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis = 0)
    x /= 255

    custom = model.predict(x)
    return emotions[custom[0].tolist().index(max(custom[0]))]

def run():
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            
            #Crop, Resize, Gray, & Reshape Image
            cropped_img = frame[y:y+h, x:x+w].copy()
            resized_img = cv2.resize(src=cropped_img, dsize=(48, 48), interpolation=cv2.INTER_AREA)
            grayed_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
            reshaped_img = grayed_img.reshape((48, 48, 1))

            label = label_image(model, reshaped_img)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, label, org=(50, 50) , fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, 
                color=(0, 0, 255) , thickness=2, lineType= cv2.LINE_AA) 
            # cv2.imshow("cropped", reshaped_img)
            # cv2.imwrite('cropped.png',crop_frame)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    run()