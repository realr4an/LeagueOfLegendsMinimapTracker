const BASE_URL = 'https://127.0.0.1:2999';
const PLAYER_LIST_ENDPOINT = '/liveclientdata/playerlist';
const pluginName = "minimap-plugin";
const agentOptions = { mode: 'cors' };

var pluginInstance = null;

async function initializePlugin() {
    try {
        const result = await new Promise((resolve) => {
            overwolf.extensions.current.getExtraObject(pluginName, resolve);
        });
        
        if (result.status === "success") {
            pluginInstance = result.object;
            console.log("Plugin erfolgreich initialisiert.");
        } else {
            throw new Error(`Fehler beim Initialisieren des Plugins: ${result.error}`);
        }
    } catch (error) {
        console.error(error.message);
    }
}

function getChampionPositions(x, y, width, height, championNames, callback) {
    if (!pluginInstance) {
        console.error("Plugin nicht initialisiert.");
        return;
    }
    pluginInstance.CaptureAndDetect(x, y, width, height, championNames, (result) => {
        if (result.status === "success") {
            console.log("Champions erfolgreich erkannt:", result.data);
            callback(result.data);
        } else {
            console.error("Fehler beim Abrufen der Champion-Positionen:", result.error);
        }
    });
}

async function fetchAndProcessData() {
    try {
        const response = await fetch(`${BASE_URL}${PLAYER_LIST_ENDPOINT}`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            ...agentOptions
        });
        
        if (!response.ok) {
            throw new Error(`Fehler beim Abrufen der Spieler-Liste: ${response.statusText}`);
        }

        const playerList = await response.json();

        const x = 400, y = 500, width = 300, height = 300; 
        const opponents = playerList.filter(player => player.team !== 'ORDER');
        const championNames = opponents.map(player => player.championName);
        console.log("Spielernamen:", championNames);

        getChampionPositions(x, y, width, height, championNames, (positions) => {
            console.log("Erkannte Positionen:", positions);
            updateOverlay(playerList, positions);
        });
    } catch (error) {
        console.error("Fehler bei der Kommunikation mit der API:", error.message);
    }
}

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

initializePlugin().then(() => {
    setInterval(fetchAndProcessData, 5000); 
});
