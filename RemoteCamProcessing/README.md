# RemoteOneCameraProcessing
This is the website used by the core to run the AI.<br>
This technically doesn't need to be a website, and if you want or need to make your own clients networking details will be provided below




# Network Details
**config**<br>
_get_ and _put_ are the only valid methods

values are:<br>
 -  autostart (bool)<br>
 -  confidenceThreshold (float; 0-1)<br>
 -  cameraName (string)<br>
 -  If any others are defined they will be provided (with 2 exceptions given below)

_get_ can be provided an index:<br>
 -  -2 - generates a new config with id `windowconfigs.count()`<br>
 -  -1 - gets an auto-generated id based on the amount of -1 calls before it, maxing at the highest defined config (default if not given)<br>
 -  index within defined configs - gets the associated config<br>
 -  index > defined configs - generates new config and allows that id
 
Generated configs are made from the last defined config, but aren't written to the global config<br>
 -  If no configs are defined, one with the properties listed above will be created
 
All -2 calls will return the same id<br>
Calls will return:<br>
 -  all config values (above)<br>
 -  status (string)<br>
 -  id (int)

_put_ will overwrite/append (whichever is applicable) the given config to the global config<br>
This must contain the property id, which signifies where to write it<br>
It is written exactly as is, besides id and status being removed<br>
If the id is above the defined configs, there is no check to see how far, it is simply appended (so be careful)

**SwitchConfig**<br>
recommended _put_<br>
give:<br>
 -  to (int)<br>
 -  start (int)
 
returns:
 -  same as **config** _get_ with id _to_
 
_start_ should be the current id<br>
_to_ is the desired id, no checks are performed for overlaps<br>
backend details:<br>
 -  Has the same effects as **connect** for _to_<br>
 -  Will disconnect _start,_ so be careful with this

**connect**<br>
recommended _put_<br>
Initializes all camera UI elements<br>
Must be called before **start**<br>
Should be called before **onPoseData**<br>
Does not _need_ to be called until the camera starts<br>
give:<br>
 -  id (int)

**start**<br>
recommended _put_<br>
Allows the camera to calibrate<br>
give:<br>
 -  id (int)

**cameraSize**<br>
recommended _put_<br>
Sets the camera's size in pixels<br>
Should be called before **start**<br>
give:<br>
 -  id (int)<br>
 -  width (int)<br>
 -  height (int)

**poseData**<br>
recommended _put_<br>
Gives pose data<br>
Output of AI, filtered out by _confidenceThreshold_ (config)<br>
give:<br>
 -  id (int)<br>
 -  pose (dict of pose data)

pose data:<br>
 -  x (float)<br>
 -  y (float)<br>
 -  score (float)

valid pose names are:<br>
 -  nose<br>
 -  left_eye<br>
 -  right_eye<br>
 -  left_ear<br>
 -  right_ear<br>
 -  left_shoulder<br>
 -  right_shoulder<br>
 -  left_elbow<br>
 -  right_elbow<br>
 -  left_wrist<br>
 -  right_wrist<br>
 -  left_hip<br>
 -  right_hip<br>
 -  left_knee<br>
 -  right_knee<br>
 -  left_ankle<br>
 -  right_ankle
