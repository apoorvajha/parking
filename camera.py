import cv2
import numpy as np
import time
from text_reader import detect_text

IMG_WIDTH = 640
IMG_HEIGHT = 320
FIRST_IMAGE = "data/first_image.jpeg"
SAVED_FRAMES_PATH = "data/saved_frames/"

cap = cv2.VideoCapture(0)

def capture():
    ret, frame = cap.read()
    return frame


def end_capture():
    cap.release()
    cv2.destroyAllWindows()


def reset():
    first_img = capture()
    first_img = cv2.resize(first_img, (IMG_WIDTH, IMG_HEIGHT))
    cv2.imwrite(FIRST_IMAGE, first_img)


def capture_cont(interval=0.1, car_pass_interval=0.2):
    parking = set()
    first_image = cv2.imread(FIRST_IMAGE)
    prev_frame = first_image[:]
    while True:
        frame = capture()
        cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
        #ts = time.time()
        #cv2.imwrite(SAVED_FRAMES_PATH + str(ts) +".jpeg" , frame)
        ts = time.time()
        gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(first_image, cv2.COLOR_BGR2GRAY)
        gray3 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray1 = gray1/np.sum(gray1)
        gray2 = gray2/np.sum(gray2)
        gray3 = gray3/np.sum(gray3)
        vs_first = np.linalg.norm(gray1 - gray2)
        vs_prev = np.linalg.norm(gray1 - gray3)
        if vs_first > vs_prev:
            # we have a car
            ts = time.time()
            text = detect_text(frame)
            print(text)
            cv2.imwrite(SAVED_FRAMES_PATH + str(ts) + ".jpeg", frame)
            if text:
                cv2.imwrite(SAVED_FRAMES_PATH + str(ts) + ".jpeg", frame)
                print(text)

            time.sleep(car_pass_interval)

        prev_frame = frame[:]
        time.sleep(interval)

#reset()
capture_cont()
