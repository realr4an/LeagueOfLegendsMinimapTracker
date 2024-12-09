const BASE_URL = 'https://127.0.0.1:2999';
const PLAYER_LIST_ENDPOINT = '/liveclientdata/playerlist';
const pluginName = "minimap-plugin";
const agentOptions = { mode: 'cors' };

let pluginInstance = null;

// Plugin initialisieren
function initializePlugin(callback) {
    overwolf.extensions.current.getExtraObject(pluginName, (result) => {
        if (result.status === "success") {
        pluginInstance = result.object;
        console.log("Plugin erfolgreich initialisiert.");
        if (callback) callback();
        } else {
        console.error("Fehler beim Initialisieren des Plugins:", result.status, result.error);
        }
    });
}

// Plugin-Funktion aufrufen
function getChampionPositions(minimapArea, championImages, callback) {
  if (!pluginInstance) {
    console.error("Plugin nicht initialisiert.");
    return;
  }

  pluginInstance.CaptureAndDetect(minimapArea, championImages, (result) => {
    if (result.status === "success") {
      console.log("Champions erfolgreich erkannt:", result.data);
      callback(result.data);
    } else {
      console.error("Fehler beim Abrufen der Champion-Positionen:", result.error);
    }
  });
}

// Funktion zur Datenabfrage und Verarbeitung
async function fetchAndProcessData() {
  try {
    const response = await fetch(`${BASE_URL}${PLAYER_LIST_ENDPOINT}`, { method: 'GET' ,
      headers: { 'Accept': 'application/json' },
                ...agentOptions
    });
    if (response.ok) {
      const playerList = await response.json();
      console.log("Spielerdaten:", playerList);

      const minimapArea = { x: 400, y: 500, width: 300, height: 300 }; // Beispielwerte
      const championImages = {}; // Muss entsprechend mit deinen Champion-Bildern befüllt sein.

      getChampionPositions(minimapArea, championImages, (positions) => {
        console.log("Erkannte Positionen:", positions);
        updateOverlay(playerList, positions);
      });
    } else {
      console.error("Fehler beim Abrufen der Spieler-Liste:", response.statusText);
    }
  } catch (error) {
    console.error("Fehler bei der Kommunikation mit der API:", error);
  }
}

// Overlay aktualisieren
function updateOverlay(playerList, positions) {
  const overlay = document.getElementById('opponent-champions');
  if (overlay) {
    const opponents = playerList.filter(player => player.team !== 'ORDER');
    const champions = opponents.map(player => player.championName);

    overlay.innerHTML = champions.map((champ, i) => {
      const position = positions[i] || { x: "N/A", y: "N/A" };
      return `<div>${champ} - Position: (${position.x}, ${position.y})</div>`;
    }).join('');
  }
}

// Polling starten
initializePlugin(() => {
  setInterval(fetchAndProcessData, 5000); // Alle 5 Sekunden aktualisieren
});
