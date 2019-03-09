from imutils.object_detection import non_max_suppression
import numpy as np
import cv2
import pytesseract

MIN_CONFIDENCE = 0.5
PADDING = 0.10
WEIGHTS_PATH = "frozen_east_text_detection.pb"
IMG_WIDTH = 640
IMG_HEIGHT = 320


def decode(scores, geometry):
    numRows, numCols = scores.shape[2:4]
    rectangles = []
    confidences = []

    for y in range(numRows):
        scoresData = scores[0, 0, y]
        x0 = geometry[0, 0, y]
        x1 = geometry[0, 1, y]
        x2 = geometry[0, 2, y]
        x3 = geometry[0, 3, y]
        angles = geometry[0, 4, y]

        for x in range(numCols):
            if scoresData[x] < MIN_CONFIDENCE:
                continue
            offsetX, offsetY = (x * 4.0, y * 4.0)

            angle = angles[x]
            
            h = x0[x] + x2[x]
            w = x1[x] + x3[x]
            endX = int(offsetX + (np.cos(angle) * x1[x]) + (np.sin(angle) * x2[x]))
            endY = int(offsetY - (np.sin(angle) * x1[x]) + (np.cos(angle) * x2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rectangles.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
    return rectangles, confidences
            

def detect_text(image):
    orig = image.copy()

    H, W = image.shape[:2]
    # newW, newH = IMG_WIDTH, IMG_HEIGHT
    # rW = W/float(newW)
    # rh = H/float(newH)

    layers = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"
    ]

    net = cv2.dnn.readNet(WEIGHTS_PATH)

    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop = False)

    net.setInput(blob)
    scores, geometry = net.forward(layers)

    rectangles, confidences = decode(scores, geometry)

    boxes = non_max_suppression(np.array(rectangles), probs=confidences)

    config = ("-l eng --oem 1 --psm 12")



    results = []
    minx = 1000
    miny = 1000
    maxx = 0
    maxy = 0
    for startX, startY, endX, endY in boxes:
        if(startX < minx):
            minx = startX
        if(startY < miny):
            miny = startY
        if(endX > maxx):
            maxx = endX
        if(endY > maxy):
            maxy = endY

    startX = minx
    startY = miny
    endX = maxx
    endY = maxy
    print(startX, startY, endX, endY)
    dX = int((endX - startX) * PADDING)
    dY = int((endY - startY) * PADDING)

    startX = max(0, startX - dX)
    startY = max(0, startY - dY)
    endX = min(W, endX + (dX * 2))
    endY = min(H, endY + (dY * 2))

    img_part = image[startY:endY, startX:endX]

    text = pytesseract.image_to_string(img_part, config=config)
    results.append(text)
    # for startX, startY, endX, endY in boxes:
    #     dX = int((endX - startX) * PADDING)
    #     dY = int((endY - startY) * PADDING)

    #     startX = max(0, startX - dX)
    #     startY = max(0, startY - dY)
    #     endX = min(W, endX + (dX * 2))
    #     endY = min(H, endY + (dY * 2))

    #     img_part = image[startY:endY, startX:endX]

    #     text = pytesseract.image_to_string(img_part, config=config)
    #     results.append(text)

    if results:
        return results
    return None

# img = cv2.imread('b.png')
# img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
# print(detect_text(img))