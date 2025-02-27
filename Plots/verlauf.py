import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# **1. Daten laden**
file_path = "timeline.csv"
df = pd.read_csv(file_path)

df['Y'] = 580 - df['Y']

background_image = plt.imread("Map-League-of-Legends-70-percent.png")

champions = df['champion'].unique()

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
        
        # Berechne neue Centuide 
        for i in range(k):
            centers[i] = np.mean(X[labels == i], axis=0)
        
        # Überprüfen, ob sich die Zentren geändert haben
        if np.all(centers == prev_centers):
            break

    return labels, centers


# **4. Visualisierung des Vergleichs der Bewegungsmuster aller Champions**
def plot_comparative_paths():
    plt.figure(figsize=(8, 8))
    plt.imshow(background_image, extent=[0, 580, 0, 580], alpha=0.6, cmap='gray')
    
    # Unterscheidliche Farben für verschiedene Champions
    palette = sns.color_palette("hsv", len(champions))

    for i, champion in enumerate(champions):
        # Daten für den Champion
        champ_data = df[df['champion'] == champion]

        # Bewegungsverlauf zeichnen
        plt.plot(champ_data['X'], champ_data['Y'], marker='o', color=palette[i], alpha=0.7, linestyle='-', markersize=3, label=champion)

    # Plot-Anpassungen
    plt.title("Vergleich der Bewegungsmuster aller Champions", fontsize=14)
    plt.xlabel("X-Koordinate")
    plt.ylabel("Y-Koordinate")
    plt.xlim(0, 580)
    plt.ylim(0, 580)
    plt.legend(title="Champions", loc="upper right", fontsize=10)
    plt.show()


# **5. Visualisierung der Cluster**
def plot_cluster(X, k=5):
    labels, centers = kmeans(X, k)

    # Visualisiere die Cluster auf der Karte
    plt.figure(figsize=(8, 8))
    plt.imshow(background_image, extent=[0, 580, 0, 580], alpha=0.6, cmap='gray')

    # Cluster-Daten anzeigen
    sns.scatterplot(x=X[:, 0], y=X[:, 1], hue=labels, palette='viridis', marker='o', alpha=0.6, legend=None)

    # Cluster-Zentren darstellen
    centers_x, centers_y = centers[:, 0], centers[:, 1]
    plt.scatter(centers_x, centers_y, marker='X', s=200, color='red', label='Cluster Zentren')

    # Titel und Achsenbezeichner
    plt.title("Cluster der Bewegungen der Champions ohne scikit-learn", fontsize=14)
    plt.xlabel("X-Koordinate")
    plt.ylabel("Y-Koordinate")
    plt.xlim(0, 580)
    plt.ylim(0, 580)
    plt.legend(loc="upper right")
    plt.show()


# **6. Kombination: Vergleich von Bewegungsmustern + Cluster-Zentren**
def plot_comparative_with_clusters(k=5):
    plt.figure(figsize=(8, 8))
    plt.imshow(background_image, extent=[0, 580, 0, 580], alpha=0.6, cmap='gray')
    
    # Unterscheidliche Farben für verschiedene Champions
    palette = sns.color_palette("hsv", len(champions))
    
    for i, champion in enumerate(champions):
        # Daten für den Champion
        champ_data = df[df['champion'] == champion]

        # Bewegungsverlauf zeichnen
        plt.plot(champ_data['X'], champ_data['Y'], marker='o', color=palette[i], alpha=0.7, linestyle='-', markersize=3, label=champion)
    
    # Kombiniere alle Bewegungen und führe K-Means aus
    X = df[['X', 'Y']].values  # Daten für das Clustering
    labels, centers = kmeans(X, k)

    # Visualisiere die Cluster-Zentren
    centers_x, centers_y = centers[:, 0], centers[:, 1]
    plt.scatter(centers_x, centers_y, marker='X', s=200, color='red', label='Cluster Zentren')
    
    # Titel und Achsenbezeichner
    plt.title(f"Bewegungsmuster aller Champions mit K-Means-Clustering (k={k})", fontsize=14)
    plt.xlabel("X-Koordinate")
    plt.ylabel("Y-Koordinate")
    plt.xlim(0, 580)
    plt.ylim(0, 580)
    plt.legend(title="Champions + Cluster Zentren", loc="upper right", fontsize=10)
    plt.show()


# **7. Aufruf der Funktionen**

# Vergleich der Bewegungsmuster aller Champions
plot_comparative_paths()

# Optional: Anzeige der Bewegungen + Cluster
X = df[['X', 'Y']].values  # Extrahiere die X- und Y-Koordinaten als Matrix
plot_comparative_with_clusters(k=5)  # K-Means Cluster-Analyse und Bewegungsvergleich
