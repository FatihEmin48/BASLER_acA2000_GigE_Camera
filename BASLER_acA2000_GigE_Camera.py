from pypylon import pylon
import cv2
import time


tl_factory = pylon.TlFactory.GetInstance()
devices = tl_factory.EnumerateDevices()
if len(devices) == 0:
    raise pylon.RuntimeException("No camera present.")

camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[0]))

camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

prev_time = time.time()
frame_count = 0

video_writer = None
recording = False

while camera.IsGrabbing():
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab_result.GrabSucceeded():
        image = converter.Convert(grab_result)
        img = image.GetArray()

       
        curr_time = time.time()
        elapsed_time = curr_time - prev_time
        prev_time = curr_time

        fps = 1.0 / elapsed_time
        frame_count += 1

       
        cv2.putText(img, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        if recording and video_writer is not None:
            video_writer.write(img)

       
        cv2.imshow("Basler Camera", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Exit loop if 'q' is pressed
            break
        elif key == 13:  # Enter key is pressed
            if not recording:
                                filename = f"output_{int(time.time())}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (img.shape[1], img.shape[0]))
                recording = True
                print(f"Recording started: {filename}")
            else:                
                recording = False
                video_writer.release()
                video_writer = None
                print("Recording stopped")

    grab_result.Release()

if video_writer is not None:
    video_writer.release()
camera.StopGrabbing()
cv2.destroyAllWindows()
