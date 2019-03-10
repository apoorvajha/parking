from imutils.object_detection import non_max_suppression
import numpy as np
import cv2
import pytesseract
import string

MIN_CONFIDENCE = 0.5
PADDING = 0.10
WEIGHTS_PATH = "frozen_east_text_detection.pb"
IMG_WIDTH = 640
IMG_HEIGHT = 480

STATE_CODES = ['AP', 'AR', 'AS', 'BR', 'CG', 'GA','GJ', 'HR', 'HP', 'JK', 'JH', 'KA', 'KL', 'MP', 'MH','MN'	
,'ML', 'MZ', 'NL', 'OD', 'PB', 'RJ', 'SK', 'TN', 'TS', 'TR', 'UA', 'UK', 'UP', 'WB', 'AN', 'CH'	
,'DN', 'DD', 'DL', 'LD', 'PY']

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


def follows_pattern(text):
    # remove -, | {,}
    for x in ['-', '|', '{', '}']:
        text = text.replace(x, '')
    # remove white space
    text = ''.join(text.split())

    eng_char = set(string.ascii_uppercase)
    nums = set([str(i) for i in range(10)])

    try:
        for state in STATE_CODES:
            # HP, PB
            if state in text:
                st = text.find(state)
                # two numbers 01, 22, 67
                if text[st+2] in nums and text[st+3] in nums:
                    # 1 or two alphabets
                    if text[st+4] in eng_char:
                        if text[st+5] in eng_char:
                            # 2 alphabets
                            if text[st+6] in nums and\
                                text[st+7] in nums and\
                                text[st+8] in nums and\
                                text[st+9] in nums:
                                return text[st:st+9+1]
                        else:
                            # 1 alphabet
                            if text[st+5] in nums and\
                                text[st+6] in nums and\
                                text[st+7] in nums and\
                                text[st+8] in nums:
                                return text[st:st+8+1]
        return None
    except:
        return None

def detect_text(net, image):
    orig = image.copy()

    H, W = image.shape[:2]
    # newW, newH = IMG_WIDTH, IMG_HEIGHT
    # rW = W/float(newW)
    # rh = H/float(newH)

    layers = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"
    ]

    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop = False)

    net.setInput(blob)
    scores, geometry = net.forward(layers)

    rectangles, confidences = decode(scores, geometry)

    boxes = non_max_suppression(np.array(rectangles), probs=confidences)

    results = set()
    for padding in [0.20, 0.5]:
        for psm in [7]:
            config = ("-l eng --oem 1 --psm "+str(psm))
            for startX, startY, endX, endY in boxes:
                dX = int((endX - startX) * padding)
                dY = int((endY - startY) * padding)

                startX = max(0, startX - dX)
                startY = max(0, startY - dY)
                endX = min(W, endX + (dX * 2))
                endY = min(H, endY + (dY * 2))

                img_part = image[startY:endY, startX:endX]

                text = pytesseract.image_to_string(img_part, config=config)
                formatted_text = follows_pattern(text)
                if formatted_text:
                    results.add(formatted_text)
    if results:
        return list(results)
    return None

# img = cv2.imread('c.jpg')
# img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
# print(detect_text(img))