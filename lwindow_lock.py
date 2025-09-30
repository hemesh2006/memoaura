import ctypes
import time
user32 = ctypes.WinDLL('user32', use_last_error=True)

SW_MINIMIZE = 6
SW_RESTORE = 9
GetForegroundWindow = user32.GetForegroundWindow
ShowWindow = user32.ShowWindow
EnableWindow = user32.EnableWindow

class Ard:
    def __init__(self,windowname=None):
        if windowname:
            self.hwnd = windowname
        else:
            self.hwnd = GetForegroundWindow()

    def lock_window(self, lock=True):
        if not self.hwnd:
            print("No active window found.")
            return

        if lock:
            # Minimize and lock
            #ShowWindow(self.hwnd, SW_MINIMIZE)
            EnableWindow(self.hwnd, False)
            print("Window minimized and locked!")
        else:
            # Restore and unlock
            #ShowWindow(self.hwnd, SW_RESTORE)
            EnableWindow(self.hwnd, True)
            print("Window restored and unlocked!")

# Usage
if __name__=="__main__":
    s=Ard()

# Lock the window
    s.lock_window(True)
    time.sleep(10)
# Unlock the window
    s.lock_window(False)
