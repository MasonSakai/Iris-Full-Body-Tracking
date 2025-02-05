import cv2 as cv

print('\n\n')
print('test')


haar_cascade = cv.CascadeClassifier('Python_Tutorial/haar_face.xml')

cap = cv.VideoCapture(0)

while True:


    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    
    grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces_rect = haar_cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=3)

    for (x,y,w,h) in faces_rect:
        cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0), thickness=2)
    
    cv.imshow('detected', img)
    
    if cv.pollKey() >= 0:
        break

cap.release()
cv.destroyAllWindows()