from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user

from barchart import plot_total_fixation_duration
from heatmap import generate_heatmaps
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
from collections import Counter
import csv
import os
import requests
from scanpath import scan_path_visualization_EyeMMV_from_csv
from heatmapall import generate_heatmaps_all

API_KEY = "cb8970d4b2324b1f880d39147975ea0b"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'somethingsecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy()

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'

db.init_app(app)
login_manager.init_app(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists!', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('save_and_analyze'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

@app.route('/eye-tracking-news')
@login_required
def eye_tracking_news():
    articles = []
    try:
        response = requests.get('https://newsapi.org/v2/everything?q=eye-tracking&apiKey=cb8970d4b2324b1f880d39147975ea0b')
        response.raise_for_status()
        articles_data = response.json()
        if 'articles' in articles_data:
            articles = articles_data['articles']
    except requests.RequestException as e:
        print(f"API request error: {e}")

    return render_template("dashboard.html", articles=articles)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    username = current_user.username
    heatmap_url = None
    scanpath_url = None
    searched_data = []

    df_path = f'static/mouse_data/{username}/mouse_data.csv'
    if not os.path.exists(df_path):
        return f"No data found for user {username}", 404
    df = pd.read_csv(df_path)
    searched_data = df.to_dict(orient='records')

    if request.method == 'POST':
        if 'generate_both' in request.form:
            with open(df_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    searched_data.append({
                        'gaze_x': row.get('gaze_x'),
                        'gaze_y': row.get('gaze_y'),
                        'fixation_duration': row.get('fixation_duration')
                    })

            heatmap_file = generate_heatmaps(current_user.username)
            if heatmap_file:
                heatmap_url = url_for('static', filename=f'heatmaps/{heatmap_file}')
                print("HEATMAP URL:", heatmap_url)

            scanpath_file = scan_path_visualization_EyeMMV_from_csv(current_user.username, df)
            if scanpath_file:
                scanpath_url = url_for('static', filename=f'scanpaths/{scanpath_file}')
                print("SCANPATH URL:", scanpath_url)

    return render_template('dashboard.html',
                           username=username,
                           heatmap_url=heatmap_url,
                           searched_data=searched_data,
                           scanpath_url=scanpath_url)

@app.route('/all_users', methods=['GET', 'POST'])
@login_required
def all_users():
    plot_total_fixation_duration()
    return render_template('barchart_all_user.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/save_and_analyze', methods=['GET','POST'])
@login_required
def save_and_analyze():
    if request.method == 'GET':
        return render_template('track_data.html')
    if request.method == 'POST':
        mouse_data = request.get_json()

        if not mouse_data:
            return jsonify(message="No data received"), 400

        # screen_width = mouse_data[0]['screen_width']
        # screen_height = mouse_data[0]['screen_height']
        # width_step = screen_width //3
        # height_step = screen_height // 3

        image_width = mouse_data[0]['image_width']
        image_height = mouse_data[0]['image_height']
        width_step = image_width // 3
        height_step = image_height // 3

        aoi_regions = {}
        for i in range(3):
            for j in range(3):
                aoi_name = f'AOI_{(i*3 + j + 1)}'
                aoi_regions[aoi_name] = {
                    'x_min': j * width_step,
                    'x_max': (j + 1) * width_step,
                    'y_min': i * height_step,
                    'y_max': (i + 1) * height_step
                }

        def assign_aoi(x, y, fixation_duration):
            for aoi_name, region in aoi_regions.items():
                if (region['x_min'] <= x < region['x_max'] and
                    region['y_min'] <= y < region['y_max']):
                    return {'aoi': aoi_name, 'x': x, 'y': y, 'fixation_duration': fixation_duration}
            return None


        enriched_data = []
        for d in mouse_data:
            assigned = assign_aoi(int(d['x']), int(d['y']), 0)
            enriched_data.append({
                **d,
                'x': int(d['x']),
                'y': int(d['y']),
                'timestamp': float(d['timestamp']),
                'aoi': assigned['aoi'] if assigned else 'Outside'
            })
        transitions = []
        for i in range(len(enriched_data)-1):
            a, b = enriched_data[i]['aoi'], enriched_data[i+1]['aoi']
            if a != b:
                transitions.append((a, b))
        # Time statistics
        aoi_times = {}
        current_aoi = enriched_data[0]['aoi']
        entry_time = float(enriched_data[0]['timestamp'])

        for i in range(1, len(enriched_data)):
            new_aoi = enriched_data[i]['aoi']
            if new_aoi != current_aoi:
                duration = float(enriched_data[i]['timestamp']) - entry_time
                aoi_times.setdefault(current_aoi, []).append(duration)
                current_aoi = new_aoi
                entry_time = float(enriched_data[i]['timestamp'])

        fixations = []
        current_aoi = enriched_data[0]['aoi']
        start_time = enriched_data[0]['timestamp']
        last_x = enriched_data[0]['x']
        last_y = enriched_data[0]['y']

        for i in range(1, len(enriched_data)):
            point = enriched_data[i]
            if point['aoi'] != current_aoi:
                duration = point['timestamp'] - start_time
                fixations.append({
                    'gaze_x': last_x,
                    'gaze_y': last_y,
                    'fixation_duration': round(duration, 4)
                })
                # update
                current_aoi = point['aoi']
                start_time = point['timestamp']
                last_x = point['x']
                last_y = point['y']

        duration = enriched_data[-1]['timestamp'] - start_time
        fixations.append({
            'gaze_x': enriched_data[-1]['x'],
            'gaze_y': enriched_data[-1]['y'],
            'fixation_duration': round(duration, 4)
        })
        user_folder = f'static/mouse_data/{current_user.username}'
        os.makedirs(user_folder, exist_ok=True)
        filename = os.path.join(user_folder, 'mouse_data.csv')
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['gaze_x', 'gaze_y', 'fixation_duration'])
            writer.writeheader()
            writer.writerows(fixations)

        # at the end of save_and_analyze
        stats = {
            aoi: {
                'Mean': np.mean(times),
                'SD': np.std(times),
                'Min': np.min(times),
                'Max': np.max(times)
            } for aoi, times in aoi_times.items()
        }

        trans_counts = Counter(transitions)
        source_counts = {}
        for (src, _), count in trans_counts.items():
            source_counts[src] = source_counts.get(src, 0) + count

        trans_probs = {
            f"{src} -> {dest}": count / source_counts[src]
            for (src, dest), count in trans_counts.items()
        }

        # Return everything
        return jsonify(
            stats=stats,
            transitions=trans_probs,
            csv=filename)

if __name__ == '__main__':
    app.run(debug=True)
