# Iris Full Body Tracking

Iris FBT is a camera based full body tracking program written in python utilizing pose estimation models.<br>
Other programs can utilize the tracking provided by Iris; a Steam VR driver is provided along side the server.

At least two cameras are needed, the more the better.<br>
While higher resolutions are better for calibration, the models themselves run on 640x480 images.

## Because of school, development will be slow for some time

<hr>
Old description:

# VR-AI-Full-Body-Tracking
## This is in the process of being rewritten, should have a driver version (no input emulator!) soon

An AI driven, camera based Full Body tracking solution for VR systems

This is free, besides the cost of cameras, which are fairly cheap (you can use your phone, and naturally the computer's webcam)

This program, using OpenVR Input Emulator, can create virtual trackers and using cameras placed around the room it can mimic real, vive full body trackers.

Each camera has an associated browser page running a tensorflow pose detection model (AI that can tell where your body is), and the more cameras at different angles the better.

Works on any camera if it can be recognized by the browser as a webcam. GoPros seem weird, but there are workarounds.

This program features _basic Playspace Mover functionality!_ I need to refine it (and on some systems it only half works?), but it has it and is configurable through the UI.

__Supports up to 12 point tracking__ (including the headset and hands, meaning 9 additional trackers); knees are a bit redundant unless the IK is not good enough for you (or there is no IK)

Can be made to room scale with a few well placed cameras, helps if they're wide FOV

Not only works for VRChat, but has also been tested in _Source Film Maker_ with a VR plugin! Also should work for any headset or other system as long as it uses SteamVR/OpenVR

# Notes
This program practically requires **at least** two cameras, and requires decent placement. Details below.<br>
The AI does not capture 3D position or orientation. That is all done by the program and is prone to issues or inaccuracies.<br>
  Hip tracking side-to-side is not great, as the AI can't capture this movement very well (sorry, no wiggles). Hip tracking is fine otherwise<br>
This may be slow on some hardware, especially since the AI is entirely CPU based and running in a browser (if someone can get this on a better system, network details are in the RemoteCamProcessing's readme)<br>
  If the markers on the camera are weirdly or inconsistently offset from the person in frame (noticed using GoPro for example), using OBS Virtual Camera with a solid background layer can make sure it keeps a consistent size (I can't do much about this, it's just part of how the AI initializes)<br>
This has only been tested on windows with chrome, and with Qt may _only_ work on windows<br>
The program (at the time of writing this) is only mildly tested and may be prone to issues. At the moment I don't have access to a headset so I can't do much without feedback.<br>
This program has been developed on the quest 2 over airlink. I do not know the vive controller layout or button masks, so I will need to be given them and will update this later.

# Installation
I don't have any real installer<br>
Just unzip the zip file wherever you want (though it needs to be able to write to config.json)<br>
It **requires** OpenVR Input Emulator, you will likely need this patch for this program to work <br>
https://github.com/Louka3000/OpenVR-InputEmulator-Fixed/releases/tag/v0.1-pimax

# Use
As mentioned, each active camera needs a different browser window<br>
These can be accessed at 127.0.0.1:_portNumber_ if run on the local device, otherwise you need the local IP of the computer running the VR<br>
The port number by default is 2674, but this can be changed in the config.json file<br>
If you're running on another computer, you need to set the flag _Insecure origins treated as secure_ to true with the target URL in your browser (chrome://flags/ on chrome, similar for others)<br>
It needs camera permisions and once you set the camera you need to press apply before starting (and I don't recommend changing while it's running)<br>
If you need to add more cameras, at the moment this is only done through the config.json file<br>
Once a camera is running, it must be calibrated from VR<br>
You will be given instructions both within VR and in the console

I would also not recommend recentering after calibrating cameras, or calibrating a new camera after recentering if others are active<br>
If you need to, after recalibrating there should be a system to recenter the cameras by recalibrating one of them, but if this doesn't work you must calibrate them all<br>
And adding a camera after recentering without recalibrating the others will cause issues until the others are recalibrated<br>
tldr; Just don't recenter

If the trackers dont appear in the middle of the steamvr playspace to begin with, they must be calibrated in the trackers tab<br>
They will follow the position and orientation of your hands, and once they're in a reachable spot press and hold your interact button<br>
You will then move your controller to their position and release the button<br>
This should calibrate them, and it may take time to figure out where you need to be relative to the controllers to center them better<br>
_It is also easier to do this **before** calibrating any cameras_<br>
If they're rotated and aren't really following your controllers, restart steamvr, I can't do much about that

# Camera Count and Placement
The program has been set up to allow at max 16 cameras, though this could easily be increased in code<br>
It practically requires at least 2 decently placed cameras, though benifits the more cameras are present<br>
A decently placed camera requires:<br>
 -  A large amount of the playspace viewable<br>
 -  More than likely you'll want a lot of floor visable (since this is for tracking the hip and feet)<br>
 -  Once a camera is calibrated, it should not move, or it will need to be recalibrated again<br>
 -  If a small amount of cameras (2 or 3) are present:<br>
     -  It is preferable to not have them facing directly towards eachother or in the same direction, instead being orthoganal or having a decent angle between them<br>
     -  If they must be on the same wall, place them as far apart as possible<br>
 -  For Calibration:<br>
     -  At least one place in the room that can see the entire body<br>
     -  Can be reached while remaining inside the guardian boundry (at least with oculus, since button inputs aren't read if outside)

If you wish to use your phone as a camera, DroidCam is a good app (this AI will not run on phones, though laptops are good)

# More Details
This program is a cheap solution for full body tracking through OpenVR (Steam VR) and Input Emulator<br>
It uses Pose Detection on multiple cameras in order to track limbs, and will create virtual trackers mimicking these limbs<br>
It can create trackers for ankles, knees, hip, shoulders, and elbows.<br>
Most things can be configured through the UI, website, and config.json file<br>
Each camera runs on a web-browser tab, of which are recommended to be in different windows and all visible, since most browsers **will** slow them down if they are in the background<br>
Not all browsers need to be on the same device! This means a laptop can use it's webcam and give the results of the AI to another computer running the VR. Though for this, at least in chrome, the flag "Insecure origins treated as secure" needs to be set appropriately<br>
