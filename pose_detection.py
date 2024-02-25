import mediapipe as mp
import cv2
import tempfile

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def process_video(uploaded_video):
    # Temp file to save uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
        tmpfile.write(uploaded_video.getvalue())
        video_file = tmpfile.name

    # Initialize pose detection
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=2)
    
    # Read the video file
    cap = cv2.VideoCapture(video_file)
    
    # Prepare for processing
    frame_count = 0
    processed_video_frames = []
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        
        # Convert the BGR image to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect the pose
        results = pose.process(image)
        
        # Draw pose annotations on the image
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        processed_video_frames.append(image)
        frame_count += 1
    
    cap.release()
    
    # Here you can choose how to return or save the processed frames
    # For simplicity, this example will only return the count of processed frames
    return frame_count, processed_video_frames

import streamlit as st

# Upload video file
uploaded_video = st.file_uploader("Upload a video for pose detection", type=['mp4', 'avi'])

if uploaded_video is not None:
    # Process the video and detect poses
    frame_count, processed_frames = process_video(uploaded_video)
    st.success(f"Processed {frame_count} frames.")
    
    # Optionally display the processed frames (or save them)
    # Note: Displaying a large number of frames directly in Streamlit can be very resource-intensive
    #       and may cause the app to crash. Use with caution.

    # Display the processed frames
    for i in range(0,len(processed_frames),50):
        st.image(processed_frames[i], channels="BGR", use_column_width=True)
