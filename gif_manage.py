import json
import os

def gif_add(json_path, filename, position):
    """
    Add a new image entry to the JSON file.
    
    Args:
        json_path (str): Path to the JSON file.
        filename (str): Image filename (e.g., "new.png" or "circle.gif").
        position (list): [x, y] coordinates.
    """
    # Ensure JSON exists
    if not os.path.exists(json_path):
        data = []
    else:
        with open(json_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # If file is empty or broken

    # Add new entry
    data.append([filename, position])

    # Save back
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Added {filename} at {position} to {json_path}")


#gif_add("gif.json", "circle.png", [200, 500])
#gif_add("gif.json", "star.gif", [300, 600])



import json
import os

def gif_remove(json_path, filename=None, remove_all=False):
    """
    Remove GIF(s) from the JSON file.

    Args:
        json_path (str): Path to the JSON file.
        filename (str): GIF filename to remove (ignored if remove_all=True).
        remove_all (bool): If True, clears the entire JSON file.
    """
    if not os.path.exists(json_path):
        print("⚠️ JSON file not found.")
        return

    if remove_all:
        # Clear everything
        with open(json_path, "w") as f:
            json.dump([], f, indent=4)
        print(f"✅ Cleared all entries from {json_path}")
        return

    # Normal mode → remove by filename
    with open(json_path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSON is empty or corrupted.")
            return

    new_data = [entry for entry in data if entry[0] != filename]

    with open(json_path, "w") as f:
        json.dump(new_data, f, indent=4)

    print(f"✅ Removed {filename} from {json_path}")
