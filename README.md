Link youtube record: https://youtu.be/1DlHWwoYaEE 

1. Web Eye Tracking Simulator with Cursor
This project is a web-based eye tracking simulator using mouse cursor as a proxy for gaze data. It allows researchers or educators to visualize and analyze user interaction on a webpage through heatmaps, scanpaths, and AOI (Area of Interest) statistics.

2. Features

2.1 User Authentication
Users can sign up and log in to start tracking sessions.

Each user's tracking data is saved and analyzed individually.

2.2 AOI-Based Mouse Tracking
Once logged in, users can click Start Tracking to begin recording their mouse movements.

Mouse movements are tracked over a 3x3 AOI grid on the webpage.

Upon clicking Stop Tracking, the app:

Computes and displays AOI statistics

Shows how often each AOI was visited and for how long

2.3 Heatmaps & Gaze Analysis
Click Heatmap to view:

User’s gaze data (mouse x, y positions and fixation durations)

A heatmap showing gaze density

A scanpath visualizing the sequence of gaze points

2.4 Multi-User Gaze Overview
Click Heatmap for All Users to view:

A table summarizing fixation durations per AOI across all users

Useful for group behavior analysis or usability testing

3. Technologies Used
Flask (Python) — web backend

HTML/CSS/JavaScript — frontend interaction and visualization

Plotly / heatmap.js — gaze heatmap and scanpath visualization

SQLite — user and tracking data storage

4. Usage
4.1 Clone the repository:
git clone https://github.com/yourusername/eye-tracking-simulator.git
cd eye-tracking-simulator
4.2 Install required packages:
pip install -r requirements.txt
4.3 Run the Flask app:
python app.py
4.4 Open your browser and navigate to http://127.0.0.1:5000.


