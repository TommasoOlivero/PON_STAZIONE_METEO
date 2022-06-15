# PROGRAM TO TEST THE CAMERA
__author__ = "PyTrimons"

# import the opencv library
import cv2
  
  
camera_port = 0
ramp_frames = 30

#Getting the camera references
cam_l = cv2.VideoCapture(1)

#Camera Settings

brightness=20
cam_l.set(cv2.CAP_PROP_BRIGHTNESS,brightness)

contrast=40
cam_l.set(cv2.CAP_PROP_CONTRAST,contrast)

saturation=0
cam_l.set(cv2.CAP_PROP_SATURATION,saturation)

exposure=-20
cam_l.set(cv2.CAP_PROP_EXPOSURE,exposure)

  
while(True):
      
    # Capture the video frame
    # by frame
    ret, frame = cam_l.read()
  
    # Display the resulting frame
    cv2.imshow('frame', frame)
      
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    cv2.imwrite("C:/Users/Tommy/Desktop/4A Rob/pon/sdr-master/data/prova_luce.png", frame)
    #break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()
