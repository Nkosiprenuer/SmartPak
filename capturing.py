import cv2
from PIL import Image
import pytesseract
import sqlite3
from datetime import datetime
import numpy as np
import warnings

# Suppress DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Function to create SQLite database and table
def create_database():
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS plates
                 (id INTEGER PRIMARY KEY,
                 plate_text TEXT,
                 image BLOB, 
                 capture_date TEXT,
                 capture_time TEXT,
                 cost REAL)''')
    conn.commit()
    conn.close()

# Function to capture plate and extract characters
def capture_and_extract_plate():
    # Create SQLite database and table
    create_database()

    # Open camera capture
    cap = cv2.VideoCapture(0)

    # Loop to continuously capture frames
    while True:
        ret, frame = cap.read()  # Capture frame-by-frame

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Convert the frame to grayscale for better processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use a pre-trained Haar Cascade for license plate detection
        plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

        # Loop through detected plates
        for (x, y, w, h) in plates:
            # Draw a rectangle around the plate
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # Crop the detected plate region
            plate_region = gray[y:y + h, x:x + w]

            # Preprocess the plate region
            plate_region = cv2.bilateralFilter(plate_region, 11, 17, 17)  # Denoising
            plate_region = cv2.threshold(plate_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]  # Thresholding

            # Perform OCR on the plate region
            plate_text = pytesseract.image_to_string(plate_region, config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            # Display the extracted text
            print("Detected Plate:", plate_text.strip())

            # Save the extracted text, image, and capture time to SQLite database
            save_to_database(plate_text.strip(), frame, datetime.now())

        # Display the frame with detected plate
        cv2.imshow('Detected Plates', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close windows
    cap.release()
    cv2.destroyAllWindows()

# Function to save data to SQLite database
def save_to_database(plate_text, image, capture_time):
    conn = sqlite3.connect('plates.db')
    c = conn.cursor()
    # Convert image to binary data
    _, img_encoded = cv2.imencode('.jpg', image)
    img_binary = img_encoded.tobytes()
    # Separate date and time components
    capture_date = capture_time.date()
    capture_time_str = capture_time.strftime('%H:%M:%S')  # Convert time to string
    # Calculate cost based on capture time ($1 per second)
    capture_duration = (datetime.now() - capture_time).seconds / 3600  # Duration in hours
    cost = (capture_duration + 1) * 1  # Adjust the cost calculation
    # Insert data into table
    c.execute("INSERT INTO plates (plate_text, image, capture_date, capture_time, cost) VALUES (?, ?, ?, ?, ?)",
              (plate_text, img_binary, capture_date, capture_time_str, cost))
    conn.commit()
    conn.close()

# Call the function to start capturing and extracting plates
if __name__ == '__main__':
    capture_and_extract_plate()
