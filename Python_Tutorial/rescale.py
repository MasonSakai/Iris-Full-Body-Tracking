import cv2 as cv

def rescaleFrame(frame, scale=0.75):
    height = int(frame.shape[0] * scale)
    width = int(frame.shape[1] * scale)

    dimentions = (width, height)

    return cv.resize(frame, dimentions, interpolation=cv.INTER_AREA)

def changeRes(width, height):
    cap.set(3, width)
    cap.set(4, height)

cap = cv.VideoCapture(0)
changeRes(64, 64)

while True:

    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    
    img2 = rescaleFrame(img, 8)

    cv.imshow('cam', img)
    cv.imshow('cam resize', img2)
    if cv.pollKey() >= 0:
        break

cap.release()
cv.destroyAllWindows()