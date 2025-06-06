import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_total_fixation_duration(base_folder='static/mouse_data', output_folder='static/summary_charts'):
    user_durations = {}

    for username in os.listdir(base_folder):
        user_csv = os.path.join(base_folder, username, 'mouse_data.csv')
        if os.path.exists(user_csv):
            try:
                df = pd.read_csv(user_csv)
                total_duration = df['fixation_duration'].sum()
                user_durations[username] = total_duration
            except Exception as e:
                print(f'Error reading {user_csv}: {e}')

    os.makedirs(output_folder, exist_ok=True)

    plt.figure(figsize=[10, 6])
    pd.Series(user_durations).plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Tổng thời gian nhìn của mỗi người dùng')
    plt.xlabel('Username')
    plt.ylabel('Tổng thời gian nhìn (s)')
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()

    output_path = os.path.join(output_folder, 'total_fixation_duration.png')
    plt.savefig(output_path)
    plt.close()

    return output_path