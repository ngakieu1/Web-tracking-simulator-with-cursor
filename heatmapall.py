import pandas as pd
import numpy as np
from tqdm import tqdm
import cv2
import os

def GaussianMask(sizex, sizey, sigma=33, center=None, fix=1):
    x = np.arange(0, sizex, 1, float)
    y = np.arange(0, sizey, 1, float)
    x, y = np.meshgrid(x, y)

    if center is None:
        x0 = sizex // 2
        y0 = sizey // 2
    else:
        if not np.isnan(center[0]) and not np.isnan(center[1]):
            x0 = center[0]
            y0 = center[1]
        else:
            return np.zeros((sizey, sizex))

    return fix * np.exp(-4 * np.log(2) * ((x - x0) ** 2 + (y - y0) ** 2) / sigma ** 2)

def Fixpos2Densemap(fix_arr, width, height, imgfile=None, alpha=0.5, threshold=10):
    heatmap = np.zeros((height, width), np.float32)
    for n_subject in tqdm(range(fix_arr.shape[0])):
        x, y, duration = fix_arr[n_subject]  # Extract x, y, and duration from fix_arr
        heatmap += GaussianMask(width, height, sigma=25, center=(x, y), fix=duration)

        # Normalization
    heatmap = heatmap / np.amax(heatmap)
    heatmap = heatmap * 255
    heatmap = heatmap.astype("uint8")

    if imgfile.any():
        # Resize heatmap to imgfile shape
        h, w, _ = imgfile.shape
        heatmap = cv2.resize(heatmap, (w, h))
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

        # Create mask
        mask = np.where(heatmap <= threshold, 1, 0)
        mask = np.reshape(mask, (h, w, 1))
        mask = np.repeat(mask, 3, axis=2)

        # Marge images
        marge = imgfile * mask + heatmap_color * (1 - mask)
        marge = marge.astype("uint8")
        marge = cv2.addWeighted(imgfile, 1 - alpha, marge, alpha, 0)
        return marge

    else:
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        return heatmap
def generate_heatmaps_all(img_path='newspp.jpg', csv_file='data/5_users_gaze.csv', output_folder='static/heatmaps'):
    df = pd.read_csv(csv_file)

    img_file = cv2.imread(img_path)

    if img_file is None:
        raise FileNotFoundError('Image not found')
    H, W, _ = img_file.shape

    fix_arr = df[['gaze_x', 'gaze_y', 'fixation_duration']].to_numpy()
    heatmap = Fixpos2Densemap(fix_arr, W, H, imgfile=img_file, alpha=0.7, threshold=5)

    os.makedirs(output_folder, exist_ok=True)
    output_filename = f"{output_folder}/heatmap_all.png"
    cv2.imwrite(output_filename, heatmap)

    return output_filename
