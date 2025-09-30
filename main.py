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
        r"C:\Users\HP\Documents\project\memoaura\memoaura\image_overlay.py",
        r"C:\Users\HP\Documents\project\memoaura\memoaura\msg_scr.py",
        r"C:\Users\HP\Documents\project\memoaura\memoaura\gif_overlay.py",
        r"C:\Users\HP\Documents\project\memoaura\memoaura\message_of_chat.py",
        r"C:\Users\HP\Documents\project\memoaura\memoaura\credentials.py",
        r"C:\Users\HP\Documents\project\memoaura\memoaura\setting.py",
        r"C:\Users\HP\Documents\project\memoaura\memoaura\debug_mode.py",
        "test_run.py"
    ]
    
    run_multiple_py(files_to_run)
