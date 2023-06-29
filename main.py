# -*- coding: utf-8 -*-


import gtts.tokenizer.pre_processors
import pytesseract
import cv2
import numpy as np
import os
import math
from gtts import gTTS

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

resultsImage = 'Image Results'
resultsAudio = 'Audio Results'

kernel = np.ones((2,2), np.uint8)

NUM_IMAGES = 11

gtts.tokenizer.symbols.SUB_PAIRS.append(('IEEE', 'I Triple E'))
#gtts.tokenizer.symbols.SUB_PAIRS.append(('WIT', 'Wentworth Institute of Technology'))
gtts.tokenizer.symbols.SUB_PAIRS.append(('INYOUR', 'IN YOUR'))


with open("Results.txt", 'w') as file:
    file.write(f"")


def preprocess(image, index):
    if image is None:
        print("Error")
    else:
        image = cv2.resize(image, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(resultsImage, f"{index}_1_ResizeAndColor.jpg"), image)

        h, w = image.shape
        heightMargin = math.floor((h * 0.15)/2)
        widthMargin = math.floor((w * 0.15)/2)
        #image = image[heightMargin:(h-heightMargin), widthMargin:(w - widthMargin)]

        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 19, 9)
        cv2.imwrite(os.path.join(resultsImage, f"{index}_3_Thresh.jpg"), image)

        #image = cv2.erode(image, kernel, iterations=1)
        #cv2.imwrite(os.path.join(resultsImage, f"{index}_4_Erosion.jpg"), image)

        #image = cv2.dilate(image, kernel, iterations=1)
        #cv2.imwrite(os.path.join(resultsImage, f"{index}_5_Dilation.jpg"), image)

        contours, hierarchy =  cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cntsSorted = sorted(contours, key=lambda x: cv2.contourArea(x))
        cnt = cntsSorted[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        image = image[y:y+h, x:x+w]
        cv2.imwrite(os.path.join(resultsImage, f"{index}_6_Remove_Border.jpg"), image)

        coords: object = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle > 45:
            angle = -(angle - 90)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        cv2.imwrite(os.path.join(resultsImage, f"{index}_7_Rotated.jpg"), image)

        return image


def string_replacement(in_string):
    new_string = in_string.translate({ord(i): None for i in '©�__’‘`~!^*()=+[{}¥]\\|<>/»}\'\"'})
    #new_string = new_string.translate({ord(i): ' ' for i in '\n'})
    return new_string


for i in range(NUM_IMAGES):
    imgName = "OCR-Samples/text_test (" + str(i+1) + ").png"
    print(imgName)
    img = cv2.imread(imgName)
    processed = preprocess(img, i+1)
    ocrResult = string_replacement(pytesseract.image_to_string(processed, lang="eng", config='--psm 4'))

    txtName = "testImage" + str(i+1) + ".txt"
    imgName = "testImage" + str(i+1)
    processedResult = gtts.tokenizer.pre_processors.word_sub(ocrResult)
    processedResult = gtts.tokenizer.pre_processors.end_of_line(processedResult)
    processedResult = gtts.tokenizer.pre_processors.abbreviations(processedResult)
    gtts.tokenizer.tokenizer_cases.period_comma()
    processedResult = gtts.tokenizer.pre_processors.tone_marks(processedResult)
    tts = gTTS(processedResult, lang='en', tld='com.au')
    tts.save(os.path.join(resultsAudio, f"00{i+1}_result.mp3"))

    with open("Results.txt", 'a') as file:
        file.write(f"Image {i+1}:\n")
        file.write("________________________\n")
        file.write(f"{processedResult}\n")
        file.write("________________________\n\n")