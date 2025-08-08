def load_config(file_path="config.txt"):
    config = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                key, value = line.split(":", 1)
                value = value.strip()
                # int versuchen, sonst als String lassen
                try:
                    config[key] = int(value)
                except ValueError:
                    config[key] = value
    except FileNotFoundError:
        config = {"top": 850, "left": 1500, "width": 240, "height": 240,
                  "overlay_color": "#ff0000", "team": "CHAOS"}
    except Exception:
        config = {"top": 850, "left": 1500, "width": 240, "height": 240,
                  "overlay_color": "#ff0000", "team": "CHAOS"}

    # Defaults falls nicht vorhanden
    config.setdefault("overlay_color", "#ff0000")
    config.setdefault("team", "CHAOS")
    return config

def save_config(config: dict, file_path="config.txt"):
    with open(file_path, "w") as f:
        for k, v in config.items():
            f.write(f"{k}:{v}\n")
