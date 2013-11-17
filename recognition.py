#!/usr/bin/python
## The equivalent of:
##  "Working with the Skeleton"
## in the OpenNI user guide.

"""
This shows how to identify when a new user is detected, look for a pose for
that user, calibrate the users when they are in the pose, and track them.

Specifically, it prints out the location of the users' head,
as they are tracked.
"""

# Pose to use to calibrate the user
pose_to_use = 'Psi'


from openni import *
import math, pygame, SimpleCV


pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Head")


ctx = Context()
ctx.init()

kinectImage = ImageGenerator()
kinectImage.create(ctx)



depth = DepthGenerator()
depth.create(ctx)


# Create the user generator
user = UserGenerator()
user.create(ctx)

# Obtain the skeleton & pose detection capabilities
skel_cap = user.skeleton_cap
pose_cap = user.pose_detection_cap

# Declare the callbacks
def new_user(src, id):
    print "1/4 User {} detected. Looking for pose..." .format(id)
    pose_cap.start_detection(pose_to_use, id)

def pose_detected(src, pose, id):
    print "2/4 Detected pose {} on user {}. Requesting calibration..." .format(pose,id)
    pose_cap.stop_detection(id)
    skel_cap.request_calibration(id, True)

def calibration_start(src, id):
    print "3/4 Calibration started for user {}." .format(id)

def calibration_complete(src, id, status):
    if status == CALIBRATION_STATUS_OK:
        print "4/4 User {} calibrated successfully! Starting to track." .format(id)
        skel_cap.start_tracking(id)
    else:
        print "ERR User {} failed to calibrate. Restarting process." .format(id)
        new_user(user, id)

def lost_user(src, id):
    print "--- User {} lost." .format(id)

# Register them
user.register_user_cb(new_user, lost_user)
pose_cap.register_pose_detected_cb(pose_detected)
skel_cap.register_c_start_cb(calibration_start)
skel_cap.register_c_complete_cb(calibration_complete)

# Set the profile
skel_cap.set_profile(SKEL_PROFILE_ALL)

# Start generating
ctx.start_generating_all()
print "0/4 Starting to detect users. Press Ctrl-C to exit."
maxx = -10000
minn = 100000
while True:
    # Update to next frame
    ctx.wait_and_update_all()
    image = kinectImage.get_raw_image_map_bgr()
    newImage = pygame.image.fromstring(image,(640,480),"RGB")
    finalImage = SimpleCV.Image(pygame.surfarray.array2d(newImage)).flipHorizontal()
    
    finalImage.save('asd.png')
    finalImage = pygame.image.load('asd.png')
    screen.blit(finalImage,(0,0))

    # Extract head position of each tracked user
    for id in user.users:
        if skel_cap.is_tracking(id):
            head = skel_cap.get_joint_position(id, SKEL_HEAD)
            headCenter = head.point
            if headCenter[0] > maxx:
                maxx = headCenter
            if headCenter[0] < minn:
                minn = headCenter

            # print maxx[0], minn[0]

            pygame.draw.circle(screen, (255,0,0), (-1 * int(head.point[0]),int(-1 * head.point[1])), 100, 4)
            pygame.display.flip()

            # print "  {}: head at ({loc[0]}, {loc[1]}, {loc[2]}) [{conf}]" .format(id, loc=head.point, conf=head.confidence)
