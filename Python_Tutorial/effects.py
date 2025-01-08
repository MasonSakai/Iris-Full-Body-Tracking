import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)


while True:

    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    
    cv.imshow('cam', img)
    
    #blur = cv.GaussianBlur(img, (7,7), cv.BORDER_DEFAULT)
    #cv.imshow('blur', blur)

    canny = cv.Canny(img, 125, 175)
    dilated = cv.dilate(canny, (7,7), iterations=3)
    eroded = cv.erode(dilated, (7,7), iterations=3)
    cv.imshow('eroded', eroded)

    cropped = img[50:200, 200:400]
    cv.imshow('cropped', cropped)
    
    if cv.pollKey() >= 0:
        break

cap.release()
cv.destroyAllWindows()