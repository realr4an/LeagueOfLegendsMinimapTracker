# config_loader.py
def load_config(file_path="config.txt"):
    """
    Load configuration values from a file.
    """
    config = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split(":")
                config[key] = int(value)
    except FileNotFoundError:
        print(f"Config file {file_path} not found. Using default values.")
        config = {"top": 850, "left": 1500, "width": 240, "height": 240}
    except ValueError:
        print(f"Error in config file {file_path}. Using default values.")
        config = {"top": 850, "left": 1500, "width": 240, "height": 240}
    return config
