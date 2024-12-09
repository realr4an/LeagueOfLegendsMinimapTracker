# Overwolf App with Riot API and Minimap Processing

This repository contains an Overwolf app that communicates with the Riot Games API to fetch in-game data and processes minimap data using OpenCV. The app is designed to enhance the gameplay experience by providing real-time insights and visual analytics.

---

## Features

1. **Riot API Integration**: Fetches live game data, player stats, and match details.
2. **Minimap Processing**: Uses OpenCV to analyze minimap data for real-time detection and visualization.
3. **Overwolf Framework**: Integrates seamlessly with Overwolf's overlay functionality.
4. **Customizable UI**: Includes HTML, CSS, and JavaScript for user interface development.

---

## Project Structure

### Overwolf App (`my-overwolf-app`)
The Overwolf app folder contains the main application logic and resources.

#### Key Files and Folders:
- **`icons/`**: Contains application icons.
- **`images/`**: Stores image assets used in the UI.
- **`index.html`**: The main entry point for the app's user interface.
- **`main.js`**: Implements the app's logic and communicates with the Riot API.
- **`manifest.json`**: Defines the app's metadata, permissions, and Overwolf configuration.
- **`plugin/`**: Contains additional plugin modules.
- **`style.css`**: Handles styling for the app.

---

### Minimap Plugin (`MinimapDetectorPlugin`)
The Minimap Detector Plugin is a separate module designed to process minimap images using OpenCV.

#### Key Files and Folders:
- **`.vs/`**: Visual Studio configuration files.
- **`MigrationBackup/`**: Backup files from project migration.
- **`MinimapDetectorPlugin/`**: Contains the main plugin code.
- **`MinimapDetectorPlugin.sln`**: Solution file for Visual Studio.

---

## Requirements

### Software
- Overwolf SDK
- Riot Games API key
- OpenCV library (for minimap processing)
- Visual Studio (for the Minimap Plugin)

### Dependencies
- Node.js (for managing Overwolf app dependencies)
- Overwolf Client (to run and test the app)

---

## Setup and Installation

### Overwolf App
1. Navigate to the `my-overwolf-app` directory.
2. Modify `manifest.json` with your app-specific configurations.
3. Install dependencies using Overwolf's CLI tools.
4. Launch the app using Overwolf's developer mode.

### Minimap Plugin
1. Open `MinimapDetectorPlugin.sln` in Visual Studio.
2. Build the solution to generate the required binary.
3. Ensure the plugin binary is correctly linked with the Overwolf app.

---

## Usage

1. Launch the Overwolf client.
2. Start the app from the Overwolf library.
3. Ensure the Riot API key is valid and configured in `main.js`.
4. The app will display real-time game data and minimap insights during a match.

---

## Contributing

We welcome contributions! Please fork the repository and submit a pull request with your changes. Ensure your code adheres to the project's coding standards.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
