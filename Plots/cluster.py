import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# **1. Daten laden**
file_path = "timeline.csv"
df = pd.read_csv(file_path)

# Y-Koordinate invertieren (basierend auf der Kartenlogik von League of Legends)
df['Y'] = 580 - df['Y']

# Hintergrundbild (Minimap)
background_image = plt.imread("Map-League-of-Legends-70-percent.png")

# **2. Einzigartige Champions herausfiltern**
champions = df['champion'].unique()

# **3. K-Means ohne scikit-learn**
def kmeans(X, k, max_iters=100):
    # Zufällige Initialisierung der Cluster-Zentren
    centers = X[np.random.choice(range(len(X)), size=k, replace=False)]
    prev_centers = np.zeros_like(centers)
    labels = np.zeros(len(X))
    
    for _ in range(max_iters):
        # Berechne Distanzen zwischen den Punkten und den Zentren
        distances = np.linalg.norm(X[:, np.newaxis] - centers, axis=2)
        
        # Weisen Sie jedem Punkt den nächsten Cluster zu
        labels = np.argmin(distances, axis=1)
        
        # Speichern der vorherigen Zentren
        prev_centers = centers.copy()
        
        # Berechne neue Zentren
        for i in range(k):
            centers[i] = np.mean(X[labels == i], axis=0)
        
        # Überprüfen, ob sich die Zentren geändert haben
        if np.all(centers == prev_centers):
            break

    return labels, centers

# **4. Visualisierung der Cluster**
k = 5  # Anzahl der Cluster
X = df[['X', 'Y']].values  # Daten für das Clustering

# K-Means-Clustering ohne scikit-learn
labels, centers = kmeans(X, k)

# Visualisiere die Cluster auf der Karte
plt.figure(figsize=(8, 8))
plt.imshow(background_image, extent=[0, 580, 0, 580], alpha=0.6, cmap='gray')

# Cluster-Daten anzeigen
sns.scatterplot(data=df, x='X', y='Y', hue=labels, palette='viridis', marker='o', alpha=0.6, legend=None)

# Cluster-Zentren darstellen
centers_x, centers_y = centers[:, 0], centers[:, 1]
plt.scatter(centers_x, centers_y, marker='X', s=200, color='red', label='Zentren')

# Titel und Achsenbezeichner
plt.title("Cluster der Bewegungen der Champions ohne scikit-learn", fontsize=14)
plt.xlabel("X-Koordinate")
plt.ylabel("Y-Koordinate")
plt.xlim(0, 580)
plt.ylim(0, 580)
plt.legend(loc="upper right")
plt.show()

