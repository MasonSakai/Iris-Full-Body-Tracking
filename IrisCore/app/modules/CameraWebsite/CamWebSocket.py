from app import db, socketio
from app.main.models import Camera
import sqlalchemy as sqla

@socketio.on('connect', namespace='/camsite')
def on_connect():
    print("on_connect")
    
@socketio.on('connect', namespace='/camsite')
def on_disconnect(reason):
    print("on_disconnect", reason)
    
    
@socketio.on('declare', namespace='/camsite')
def on_pose(id):
    print("declare", id)

@socketio.on('pose', namespace='/camsite')
def on_pose(data):
    pass

