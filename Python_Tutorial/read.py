import cv2 as cv

# img = cv.imread('')
cap = cv.VideoCapture(0)

while True:

    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    
    cv.imshow('cam', img)
    if cv.pollKey() >= 0:
        break

cap.release()
cv.destroyAllWindows()