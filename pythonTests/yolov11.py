import cv2 as cv
from ultralytics import YOLO

model = YOLO("Models/onnx/yolo11n-pose.pt")

# read the image
cap = cv.VideoCapture(0)

points = []

while True:
    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    
    res = model.track(img, stream=True)

    for r in res:
        points = r.keypoints
        l = len(points.xyn) - 1
        t = 0
        for i, data in enumerate(points.data):
            if l > 0:
                t = i / l
            for p in data:
                cv.circle(img, (int(p[0]), int(p[1])), 5, (255*t, 0,255*(1-t)), thickness=int(5*p[2]))

    cv.imshow("res", img)

    if cv.pollKey() >= 0:
        break

print(points)

cap.release()
cv.destroyAllWindows()