import subprocess
import os

def run_multiple_py(files):
    processes = []
    for file in files:
        if os.path.exists(file):
            print(f"Starting {file} ...")
            
            # Start each file in a separate process
            p = subprocess.Popen(["python", file])
            processes.append(p)
        else:
            print(f"File not found: {file}")

    # Wait for all processes to complete
    for p in processes:
        p.wait()

if __name__ == "__main__":
    # List of Python files you want to run
    files_to_run = [
        "msg_scr.py",
        "gif_overlay.py",
        "message_of_chat.py",
        "credentials.py",
        "setting.py",
        "debug_mode.py",
        "layer.py"
    ]
    
    run_multiple_py(files_to_run)
