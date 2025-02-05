import cv2 as cv
from ultralytics import YOLO

model = YOLO("Models/onnx/yolo11n-pose.pt")

# read the image
cap = cv.VideoCapture(0)

while True:
    ret, img = cap.read()
    if not ret:
        print("failed to grab frame")
        break
    
    res = model.track(img, stream=True)

    for r in res:
        # print(r)
        points = r.keypoints
        for p in points.xyn[0]:
            # print(p)
            cv.circle(img, (int(img.shape[1]*p[0]), int(img.shape[0]*p[1])), 5, (0,0,255), thickness=3)

    cv.imshow("res", img)

    if cv.pollKey() >= 0:
        break

cap.release()
cv.destroyAllWindows()