import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def scan_path_visualization_EyeMMV_from_csv(username, user_data, maxr=0.1, image_path='static/newspp.jpg', output_folder='static/scanpaths'):
    x_fix = user_data['gaze_x'].values
    y_fix = user_data['gaze_y'].values
    duration = np.nan_to_num(user_data['fixation_duration'].values, nan=0)
    n_fix = len(x_fix)

    plt.figure()
    if image_path:
        img = mpimg.imread(image_path)
        plt.imshow(img, extent=[0, img.shape[1], img.shape[0], 0])
        plt.xlim(0, img.shape[1])
        plt.ylim(img.shape[0], 0)

    plt.scatter(x_fix, y_fix, c='g', marker='s', label='Fixation Center')
    plt.plot(x_fix, y_fix, '-b', label='Saccade')

    c = np.linspace(0, 2 * np.pi, 100)
    maxr_par = maxr / (np.max(np.sqrt(duration)) + 1e-6)

    for i in range(n_fix):
        x_center = x_fix[i]
        y_center = y_fix[i]
        xc = (maxr_par * np.sqrt(duration[i])) * np.cos(c)
        yc = (maxr_par * np.sqrt(duration[i])) * np.sin(c)
        plt.fill(x_center + xc, y_center + yc, 'r', alpha=0.6)
        plt.text(x_center, y_center, f"{duration[i]:.2f}", ha='left', va='bottom', color='yellow', fontsize=8)

    plt.text(x_fix[0], y_fix[0], 'START', ha='left', va='top', color='cyan', fontsize=10, weight='bold')
    plt.text(x_fix[-1], y_fix[-1], 'END', ha='left', va='top', color='cyan', fontsize=10, weight='bold')

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{username}.png")
    plt.xlabel("Horizontal Coordinate")
    plt.ylabel("Vertical Coordinate")
    plt.title(f"Scanpath for User {username}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return f"{username}.png"