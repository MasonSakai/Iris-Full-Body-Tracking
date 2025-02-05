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
        for p in points.xyn[0]:
            # print(p)
            cv.circle(img, (int(p[0]*r.orig_shape[1]), int(p[1]*r.orig_shape[0])), 5, (0,0,255), thickness=3)

    cv.imshow("res", img)

    if cv.pollKey() >= 0:
        break

print(points)

cap.release()
cv.destroyAllWindows()