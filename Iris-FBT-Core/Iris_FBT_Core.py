from iris.config import Config

from iris.app import create_app, db
from iris.cameras.camera import Camera
from iris.model.yolo import YOLOModel

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import cv2 as cv

# app = create_app(Config)
# 
# @app.shell_context_processor
# def make_shell_context():
#     return {'sqla': sqla, 'sqlo': sqlo, 'db': db}
# 
# @app.before_request
# def initDB(*args, **kwargs):
#     if app._got_first_request:
#         db.create_all()

def test_model():
    model = YOLOModel(Config)
    with model as m:
        cam = Camera(0)
        
        while cv.pollKey() == -1:
            ret, img = cam.capture.read()
            if not ret:
                print("failed to grab frame")
                break

            res = m.forward(img)
            for person in res:
                for key in person:
                    data = person[key]
                    # print(f'{key}: {data}')
                    cv.circle(img, (int(data.x), int(data.y)), 5, (0, 0,255), int(2.5*data.conf))
                    cv.putText(img, key, (int(data.x), int(data.y)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0,255), int(data.conf), cv.LINE_AA)
            
            cv.imshow("res", img)
            
        
if __name__ == "__main__":
    test_model()

    # app.run(debug=True)