import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# **1. Daten laden**
file_path = "timeline.csv"  # Pfad zur CSV-Datei
df = pd.read_csv(file_path)

# Y-Koordinate invertieren (basierend auf der Kartenlogik von League of Legends)
df['Y'] = 580 - df['Y']

# Hintergrundbild (Minimap)
background_image = plt.imread("Map-League-of-Legends-70-percent.png")

# **2. Einzigartige Champions herausfiltern**
champions = df['champion'].unique()

# **3. Subplots: Separate Heatmaps für jeden Champion**
n = len(champions)
fig, axes = plt.subplots(1, n, figsize=(5 * n, 5), constrained_layout=True)

for i, champion in enumerate(champions):
    ax = axes[i]
    
    # Champion-spezifische Daten
    champ_data = df[df['champion'] == champion]
    
    # Hintergrundbild zeichnen
    ax.imshow(
        background_image,
        extent=[0, 580, 0, 580],
        alpha=0.5,  # Transparenz des Hintergrundbilds
        cmap='gray'
    )
    
    # Heatmap erzeugen (Kombination: Transparente Fläche + Konturlinien)
    sns.kdeplot(
        data=champ_data, x='X', y='Y',
        cmap="viridis",
        shade=True,
        bw_adjust=0.5,  # Bandbreite der Glättung
        levels=30,
        alpha=0.4,  # Transparenz
        ax=ax
    )
    sns.kdeplot(
        data=champ_data, x='X', y='Y',
        cmap="viridis",
        linewidths=1.2,  # Dünne Konturen
        levels=15,
        ax=ax
    )
    
    # Plot-Anpassungen
    ax.set_title(f"Heatmap: {champion}", fontsize=14)
    ax.set_xlim(0, 580)
    ax.set_ylim(0, 580)
    ax.set_xlabel("X-Koordinate")
    ax.set_ylabel("Y-Koordinate")

# **4. Kombinierte Heatmap: Alle Daten aller Champions zusammen**
plt.figure(figsize=(8, 8))

# Hintergrundbild zeichnen
plt.imshow(
    background_image,
    extent=[0, 580, 0, 580],
    alpha=0.5,  # Transparenz des Hintergrundbilds
    cmap='gray'
)

# Kombinierte Daten für alle Champions
sns.kdeplot(
    data=df, x='X', y='Y',
    cmap="plasma",  # Einheitliche Farbpalette
    shade=True,
    bw_adjust=0.5,
    levels=40,  # Anzahl der Konturlinien
    alpha=0.4  # Transparenz der Heatmap
)
sns.kdeplot(
    data=df, x='X', y='Y',
    cmap="plasma",  # Einheitliche Farbpalette
    linewidths=1,  # Dünne Konturen
    levels=30,
)

# Plot-Anpassungen
plt.title("Kombinierte Heatmap: Alle Daten aller Champions", fontsize=16)
plt.xlabel("X-Koordinate")
plt.ylabel("Y-Koordinate")
plt.xlim(0, 580)
plt.ylim(0, 580)
plt.show()
