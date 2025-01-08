import cv2 as cv
import numpy as np

cap = cv.VideoCapture(0)


while True:

    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break

    #cv.rectangle(img, (0,0), (img.shape[1]//2, img.shape[0]//2), (0,255,0), thickness=-1)

    cv.circle(img, (int(img.shape[1]*0.65), int(img.shape[0]*0.55)), 80, (0,0,255), thickness=3)
    
    cv.line(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.4)), (int(img.shape[1]*0.3), int(img.shape[0]*0.2)), (0,0,255), thickness=3)
    cv.line(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.4)), (int(img.shape[1]*0.5), int(img.shape[0]*0.3)), (0,0,255), thickness=3)
    cv.line(img, (int(img.shape[1]*0.5), int(img.shape[0]*0.4)), (int(img.shape[1]*0.41), int(img.shape[0]*0.4)), (0,0,255), thickness=3)

    cv.rectangle(img, (0,0), (int(img.shape[1]), 75), (255, 255, 255), thickness=-1)
    cv.putText(img, "Live Mason Reaction", (0, 50), cv.FONT_HERSHEY_TRIPLEX, 1.8, (0,0,255), 5)

    cv.imshow('cam', img)
    if cv.pollKey() >= 0:
        break

cap.release()
cv.destroyAllWindows()