from pypylon import pylon
import cv2
import time

# Pylon Runtime Environment
tl_factory = pylon.TlFactory.GetInstance()

# Detect cameras
devices = tl_factory.EnumerateDevices()

if len(devices) == 0:
    raise pylon.RuntimeException("No camera present.")

# Create camera object
camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[0]))

# Start grabbing continuously
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# Image format converter
converter = pylon.ImageFormatConverter()

# Convert to OpenCV BGR format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

# Initialize FPS calculation
prev_time = time.time()
frame_count = 0

# Initialize video writer and recording state
video_writer = None
recording = False

while camera.IsGrabbing():
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab_result.GrabSucceeded():
        # Convert image to OpenCV format
        image = converter.Convert(grab_result)
        img = image.GetArray()

        # Calculate FPS
        curr_time = time.time()
        elapsed_time = curr_time - prev_time
        prev_time = curr_time

        fps = 1.0 / elapsed_time
        frame_count += 1

        # Display FPS on the image
        cv2.putText(img, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # If recording is active, write the frame to the video file
        if recording and video_writer is not None:
            video_writer.write(img)

        # Display image using OpenCV
        cv2.imshow("Basler Camera", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Exit loop if 'q' is pressed
            break
        elif key == 13:  # Enter key is pressed
            if not recording:
                # Start recording
                filename = f"output_{int(time.time())}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (img.shape[1], img.shape[0]))
                recording = True
                print(f"Recording started: {filename}")
            else:
                # Stop recording
                recording = False
                video_writer.release()
                video_writer = None
                print("Recording stopped")

    grab_result.Release()

# Cleanup
if video_writer is not None:
    video_writer.release()
camera.StopGrabbing()
cv2.destroyAllWindows()
