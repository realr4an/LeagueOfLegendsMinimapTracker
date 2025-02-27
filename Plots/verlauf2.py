import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.widgets import Button

# **1. Daten laden**
file_path = "timeline.csv"
df = pd.read_csv(file_path)

# Anpassen der Y-Koordinaten
background_image = plt.imread("Map-League-of-Legends-70-percent.png")
df['Y'] = 580 - df['Y']

# Konvertiere timestamp zu datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

champions = df['champion'].unique()

# Berechne die Startzeit des Spiels
start_time = df['timestamp'].min()

def format_ingame_time(timestamp):
    delta = timestamp - start_time
    minutes, seconds = divmod(delta.total_seconds(), 60)
    return f"{int(minutes)}:{int(seconds):02d}"

# **2. Laufwege-Logik**
def extract_paths(data, threshold=500):
    paths = []
    current_path = []
    in_safe_zone = data.iloc[0]['X'] >= threshold and data.iloc[0]['Y'] >= threshold
    start_time = None

    for _, row in data.iterrows():
        if in_safe_zone:
            if row['X'] < threshold or row['Y'] < threshold:
                current_path.append((row['X'], row['Y']))
                start_time = row['timestamp']
                in_safe_zone = False
        else:
            current_path.append((row['X'], row['Y']))
            if row['X'] >= threshold and row['Y'] >= threshold:
                paths.append((current_path, start_time, row['timestamp']))
                current_path = []
                in_safe_zone = True

    if current_path:
        paths.append((current_path, start_time, data.iloc[-1]['timestamp']))

    return paths

# **3. Plot für spezifischen Champion mit Navigation**
class PathNavigator:
    def __init__(self, paths, champion_name):
        self.paths = paths
        self.current_index = 0
        self.champion_name = champion_name
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.background_image = background_image
        
        self.next_button_ax = self.fig.add_axes([0.8, 0.01, 0.1, 0.05])
        self.prev_button_ax = self.fig.add_axes([0.1, 0.01, 0.1, 0.05])
        
        self.next_button = Button(self.next_button_ax, 'Nächster')
        self.prev_button = Button(self.prev_button_ax, 'Vorheriger')
        
        self.next_button.on_clicked(self.next_path)
        self.prev_button.on_clicked(self.previous_path)
        
        self.plot_current_path()

    def plot_current_path(self):
        self.ax.clear()
        self.ax.imshow(self.background_image, extent=[0, 580, 0, 580], alpha=0.6, cmap='gray')

        path, start_time, end_time = self.paths[self.current_index]
        path = np.array(path)

        # Fallback, falls start_time oder end_time None ist
        start_time_str = format_ingame_time(start_time) if start_time else "Unbekannt"
        end_time_str = format_ingame_time(end_time) if end_time else "Unbekannt"

        self.ax.plot(path[:, 0], path[:, 1], marker='o', linestyle='-', markersize=3, label=f'Laufweg {self.current_index + 1}')
        self.ax.set_title(f"Laufweg von {self.champion_name} (Ingame: {start_time_str} - {end_time_str})", fontsize=14)
        self.ax.set_xlabel("X-Koordinate")
        self.ax.set_ylabel("Y-Koordinate")
        self.ax.set_xlim(0, 580)
        self.ax.set_ylim(0, 580)
        self.ax.legend(loc="upper right", fontsize=10)
        self.fig.canvas.draw()

    def next_path(self, event):
        if self.current_index < len(self.paths) - 1:
            self.current_index += 1
            self.plot_current_path()

    def previous_path(self, event):
        if self.current_index > 0:
            self.current_index -= 1
            self.plot_current_path()

# **4. Auswahl eines Champions**
def select_and_plot_champion():
    print("Verfügbare Champions:")
    for i, champion in enumerate(champions):
        print(f"{i + 1}: {champion}")

    choice = int(input("Wähle einen Champion (Nummer eingeben): ")) - 1
    if 0 <= choice < len(champions):
        champion_data = df[df['champion'] == champions[choice]]
        paths = extract_paths(champion_data)

        if paths:
            navigator = PathNavigator(paths, champions[choice])
            plt.show()
        else:
            print(f"Keine Laufwege für Champion {champions[choice]} gefunden.")
    else:
        print("Ungültige Auswahl.")

# **5. Aufruf der Funktion**
select_and_plot_champion()
