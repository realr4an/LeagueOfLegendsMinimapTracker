import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# **1. Daten laden**
file_path = "timeline.csv"
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
    
    # Heatmap erzeugen
    sns.kdeplot(
        data=champ_data, x='X', y='Y',
        cmap="plasma",
        shade=True,
        bw_adjust=0.5,
        levels=40,
        alpha=0.5,  # Transparenz der Heatmap
        ax=ax
    )
    
    # Plot-Anpassungen
    ax.set_title(f"Heatmap: {champion}", fontsize=14)
    ax.set_xlim(0, 580)
    ax.set_ylim(0, 580)
    ax.set_xlabel("X-Koordinate")
    ax.set_ylabel("Y-Koordinate")

# **4. Kombinierte Heatmap: Alle Champions in unterschiedlichen Farben**
plt.figure(figsize=(8, 8))

# Hintergrundbild zeichnen
plt.imshow(
    background_image,
    extent=[0, 580, 0, 580],
    alpha=0.5,  # Transparenz des Hintergrundbilds
    cmap='gray'
)

# Unterschiedliche Farben für jeden Champion
palette = sns.color_palette("hsv", len(champions))

for i, champion in enumerate(champions):
    champ_data = df[df['champion'] == champion]
    
    sns.kdeplot(
        data=champ_data, x='X', y='Y',
        cmap=sns.light_palette(palette[i], as_cmap=True),  # Individuelle Farbpalette
        shade=True,
        bw_adjust=0.5,
        levels=40,
        alpha=0.3,  # Höhere Transparenz für bessere Übersicht
        label=champion
    )

# Plot-Anpassungen
plt.title("Kombinierte Heatmap aller Champions", fontsize=16)
plt.xlabel("X-Koordinate")
plt.ylabel("Y-Koordinate")
plt.xlim(0, 580)
plt.ylim(0, 580)
plt.legend(title="Champions", loc="upper right")
plt.show()
