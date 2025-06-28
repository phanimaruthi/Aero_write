import base64
import os
import cv2
import numpy as np
import streamlit as st
from cvzone.HandTrackingModule import HandDetector
import tempfile
from PIL import Image
# import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"


# Background image with base64 encoding
st.markdown("""
<style>
    /* Main container styling */
    .parent{
    background-color: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .command-card {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Each command row */
    .command-row {
        display: flex;
        align-items: center;
        margin: 12px 0;
        padding: 8px 10px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    /* Hover effect */
    .command-row:hover {
        background-color: rgba(74, 140, 255, 0.1);
    }
    
    /* Emoji icon styling */
    .command-emoji {
        font-size: 24px;
        min-width: 40px;
        text-align: center;
        margin-right: 12px;
    }
    
    /* Text container */
    .command-content {
        flex: 1;
    }
    
    /* Command name */
    .command-name {
        font-weight: 600;
        font-size: 16px;
        color: #2c3e50;
        margin-bottom: 2px;
        display: block;
    }
    
    /* Command description */
    .command-desc {
        color: #666;
        font-size: 14px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="title">AeroWrite</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Please Observe the below notations before writing</p>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([2, 1])

# Command instructions - FIXED VERSION
with col1:
   st.markdown("""
<div class="parent">
<div class="command-card">
    <!-- Thumb Up -->
    <div class="command-row">
        <div class="command-emoji">👍</div>
        <div class="command-content">
            <span class="command-name">Thumb Up</span>
            <span class="command-desc">Previous slide</span>
        </div>
    </div>
</div>
    <div class="command-card">
    <!-- Pinky Up -->
    <div class="command-row">
        <div class="command-emoji">👋</div>
        <div class="command-content">
            <span class="command-name">Pinky Up</span>
            <span class="command-desc">Next slide</span>
        </div>
    </div>
</div>
    <div class="command-card">
    <!-- Two Fingers -->
    <div class="command-row">
        <div class="command-emoji">✌️</div>
        <div class="command-content">
            <span class="command-name">Two Fingers</span>
            <span class="command-desc">Show pointer</span>
        </div>
    </div>
</div>
    <div class="command-card">
    <!-- Index Finger -->
    <div class="command-row">
        <div class="command-emoji">☝️</div>
        <div class="command-content">
            <span class="command-name">Index Finger</span>
            <span class="command-desc">Draw annotations</span>
        </div>
    </div>
</div>
    <div class="command-card">
    <!-- Open Hand -->
    <div class="command-row">
        <div class="command-emoji">🖐️</div>
        <div class="command-content">
            <span class="command-name">Open Hand</span>
            <span class="command-desc">Erase annotations</span>
        </div>
    </div>
</div>
    <div class="command-card">
    <!-- Press Q -->
    <div class="command-row">
        <div class="command-emoji">❌</div>
        <div class="command-content">
            <span class="command-name">Press 'Q'</span>
            <span class="command-desc">Close camera window</span>
        </div>
    </div>
</div>
</div>

""", unsafe_allow_html=True)

# Rest of your code remains the same...
# [Keep all the existing file uploader and camera control code below]

# File uploader
with col2:
    st.markdown("### 📂 Upload the images to start writing")
    uploaded_files = st.file_uploader("", 
                                   type=["png", "jpg", "jpeg"], 
                                   accept_multiple_files=True,
                                   label_visibility="collapsed")

def run_camera_control(folderPath):
    """Function containing your original camera control logic"""
    width, height = 1000, 720
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    
    pathimages = os.listdir(folderPath)
    
    # Variables
    imgnumber = 0
    buttonpressed = False
    buttoncounter = 0
    buttondelay = 30
    annotations = [[]]
    annotationnumber = 0
    annotationstart = False
    hs, ws = int(150*1), int(120*1)
    gesturethreshold = 300
    
    # Hand Detector
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    
    while True:
        # Import Images
        success, img = cap.read()
        if not success:
            break
        
        img = cv2.flip(img, 1)
        pathFullImage = os.path.join(folderPath, pathimages[imgnumber])
        imgCurrent = cv2.imread(pathFullImage)

        hands, img = detector.findHands(img)
        cv2.line(img, (0, gesturethreshold), (width, gesturethreshold), (0, 255, 0), 10)

        if hands and buttonpressed is False:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            cx, cy = hand['center']
            lmlist = hand['lmList']
            indexFinger = lmlist[8][0], lmlist[8][1]
            xval = int(np.interp(lmlist[8][0], [width//2, width-50], [0, width]))
            yval = int(np.interp(lmlist[8][1], [150, height-150], [0, height]))
            indexFinger = xval, yval

            if cy <= gesturethreshold:
                annotationstart = False
                if fingers == [1, 0, 0, 0, 0]:
                    annotationstart = False
                    if imgnumber > 0:
                        buttonpressed = True
                        imgnumber -= 1

                if fingers == [0, 0, 0, 0, 1]:
                    annotationstart = False
                    if imgnumber < len(pathimages)-1:
                        buttonpressed = True
                        annotations = [[]]
                        annotationnumber = 0
                        imgnumber += 1

            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, indexFinger, 12, (0, 255, 0), cv2.FILLED)
                annotationstart = False

            if fingers == [0, 1, 0, 0, 0]:
                if annotationstart is False:
                    annotationstart = True
                    annotationnumber += 1
                    annotations.append([])
                cv2.circle(imgCurrent, indexFinger, 12, (0, 255, 0), cv2.FILLED)
                annotations[annotationnumber].append(indexFinger)
            else:
                annotationstart = False

            if fingers == [1, 1, 1, 1, 1]:
                if annotations: 
                    if annotationnumber>=0:
                        annotations.pop(-1)
                        annotationnumber = -1
                        buttonpressed = True
        else:
            annotationstart = False

        if buttonpressed:
            buttoncounter += 1
            if buttoncounter > buttondelay:
                buttoncounter = 0
                buttonpressed = False

        for i in range(len(annotations)):
            for j in range(len(annotations[i])):
                if j != 0:
                    cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 10)

        # Adding webcam image on the slides
        imgsmall = cv2.resize(img, (ws, hs))
        h, w, _ = imgCurrent.shape
        imgCurrent[0:hs, w-ws:w] = imgsmall

        cv2.imshow("Camera Feed", img)
        cv2.imshow("Presentation Slides", imgCurrent)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Camera control section
st.markdown("### 🎥 Camera Control")

if uploaded_files:
    # Save files to temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Start camera button
        if st.button("🚀 Start Camera", type="primary"):
            st.info("Camera window opening... Use your fingers to write.")
            st.warning("Press 'Q' in the camera window to close it when done.")
            
            # Run the camera control function
            run_camera_control(temp_dir)
else:
    st.warning("Please upload  slides first")

# Requirements check
st.markdown("---")
st.markdown("### 💻 System Requirements")
st.code("""
Required Python packages:
- streamlit
- opencv-python
- numpy
- mediapipe
- cvzone
- Pillow
""")

