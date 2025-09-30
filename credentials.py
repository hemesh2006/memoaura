import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout,
    QStackedWidget
)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QSize
import  NOTIFICATION.notify2 as p
import load
CREDENTIALS_FILE = "users.json"
sys_info_path=r"C:\Users\HP\Documents\project\memoaura\memoaura\account.json"
f=open(sys_info_path)
data=json.load(f)
f.close()

# ------------------------------
# Ensure JSON exists
# ------------------------------
def ensure_json():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({"users": []}, f, indent=4)

# ------------------------------
# Login Page
# ------------------------------
class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo GIF at the center
        self.logo_label = QLabel()
        
        # Load GIF from the same directory as this script
        movie_path = os.path.join(os.path.dirname(__file__), "df.gif")
        movie = QMovie(movie_path)
        
        if movie.isValid():
            movie.setScaledSize(QSize(150, 150))
            self.logo_label.setMovie(movie)
            movie.start()
        else:
            self.logo_label.setText("GIF not found")
        
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)

        # Title
        self.title_label = QLabel("Welcome - Login")
        self.title_label.setStyleSheet("color: white; font-size: 23px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFocusPolicy(Qt.StrongFocus)
        self.username_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background: transparent;
                border: 2px solid white;
                padding: 10px;
                border-radius: 8px;
                font-size: 23px;
            }
            QLineEdit:focus {
                border: 2px solid #1DB954;
                background-color: rgba(255,255,255,30);
            }
        """)
        layout.addWidget(self.username_input)

        # Password with eye button
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFocusPolicy(Qt.StrongFocus)
        self.password_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background: transparent;
                border: 2px solid white;
                padding: 10px;
                border-radius: 8px;
                font-size: 23px;
            }
            QLineEdit:focus {
                border: 2px solid #1DB954;
                background-color: rgba(255,255,255,30);
            }
        """)

        self.eye_btn = QPushButton("🙈")
        self.eye_btn.setCheckable(True)
        self.eye_btn.setStyleSheet("background: transparent; border: none; font-size: 23px; color: white;")
        self.eye_btn.toggled.connect(self.toggle_password_visibility)

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.eye_btn)
        layout.addLayout(password_layout)

        # Forgot password
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setStyleSheet("background: transparent; color: white; font-size: 20px; text-decoration: underline;")
        self.forgot_btn.clicked.connect(self.forgot_password)
        layout.addWidget(self.forgot_btn, alignment=Qt.AlignRight)

        # Buttons
        self.login_btn = QPushButton("Login")
        self.signup_btn = QPushButton("Sign Up")
        for btn in (self.login_btn, self.signup_btn):
            btn.setStyleSheet("""
                background: #1DB954;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 23px;
                font-weight: bold;
            """)

        self.login_btn.clicked.connect(self.login)
        self.signup_btn.clicked.connect(lambda: self.parent.switch_page("signup"))

        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)

        self.setLayout(layout)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("👁️")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("🙈")

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)

        for user in data["users"]:
            if user["username"] == username and user["password"] == password:
                QMessageBox.information(self, "Success", f"Welcome {username}!")
                self.parent.close()
                p.threading.Thread(target=p.show_notification, args=("✅ login succeed", "green", "white")).start()
                f=open(sys_info_path,"r")
                datas=json.load(f)
                datas['already_login']="True"
                datas['username']=username
                json.dump(datas,open(sys_info_path,"w"),indent=4)   
                sys.exit(0)
                return

        QMessageBox.warning(self, "Error", "Invalid username or password.")
        p.threading.Thread(target=p.show_notification, args=("⚠️ Invalid Username", "red", "white")).start()


    def forgot_password(self):
        QMessageBox.information(self, "Forgot Password", "Please contact admin to reset your password.")
        p.threading.Thread(target=p.show_notification, args=("⚠️ Password Reset Required", "red", "white")).start()


# ------------------------------
# Signup Page
# ------------------------------
class SignupPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Create Account")
        title.setStyleSheet("color: white; font-size: 23px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFocusPolicy(Qt.StrongFocus)
        self.username_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background: transparent;
                border: 2px solid white;
                padding: 10px;
                border-radius: 8px;
                font-size: 23px;
            }
            QLineEdit:focus {
                border: 2px solid #1DB954;
                background-color: rgba(255,255,255,30);
            }
        """)
        layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFocusPolicy(Qt.StrongFocus)
        self.email_input.setStyleSheet(self.username_input.styleSheet())
        layout.addWidget(self.email_input)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile Number")
        self.mobile_input.setFocusPolicy(Qt.StrongFocus)
        self.mobile_input.setStyleSheet(self.username_input.styleSheet())
        layout.addWidget(self.mobile_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFocusPolicy(Qt.StrongFocus)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        layout.addWidget(self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setFocusPolicy(Qt.StrongFocus)
        self.confirm_input.setStyleSheet(self.username_input.styleSheet())
        layout.addWidget(self.confirm_input)

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setStyleSheet("""
            background: #1DB954;
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 23px;
            font-weight: bold;
        """)
        self.signup_btn.clicked.connect(self.signup)
        layout.addWidget(self.signup_btn)

        self.back_btn = QPushButton("⬅ Back to Login")
        self.back_btn.setStyleSheet("background: transparent; color: white; font-size: 20px;")
        self.back_btn.clicked.connect(lambda: self.parent.switch_page("login"))
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def signup(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not username or not email or not mobile or not password or not confirm:
            QMessageBox.warning(self, "Error", "All fields are required.")
            p.threading.Thread(target=p.show_notification, args=("⚠️ All Fields are required", "red", "white")).start()

            return

        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            p.threading.Thread(target=p.show_notification, args=("⚠️ Password Not Match", "red", "white")).start()

            return

        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)

        if any(u["username"] == username for u in data["users"]):
            QMessageBox.warning(self, "Error", "Username already exists.")
            p.threading.Thread(target=p.show_notification, args=("⚠️ Username Exists", "red", "white")).start()

            return

        data["users"].append({
            "username": username,
            "email": email,
            "mobile": mobile,
            "password": password
        })

        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Success", "Account created! Please login.")
        p.threading.Thread(target=p.show_notification, args=("✅  please login!", "green", "white")).start()
        self.parent.switch_page("login")

# ------------------------------
# Main Overlay
# ------------------------------
class AuthOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(420, 550)

        # Center window
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - self.width()) // 2,
                  (screen.height() - self.height()) // 2)

        # Background overlay
        self.bg_overlay = QWidget(self)
        self.bg_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150); border-radius: 15px;")
        self.bg_overlay.setGeometry(0, 0, self.width(), self.height())
        self.bg_overlay.lower()

        # Stack for pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(self)
        self.signup_page = SignupPage(self)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)

        self.switch_page("login")

    def switch_page(self, page):
        if page == "login":
            self.stack.setCurrentWidget(self.login_page)
        else:
            self.stack.setCurrentWidget(self.signup_page)

# ------------------------------
# Run Application
# ------------------------------
def main():
    ensure_json()
    app = QApplication(sys.argv)
    overlay = AuthOverlay()
    overlay.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    app = load.QApplication(sys.argv)
    loader = load.LoadingOverlay()
    loader.show()
    app.exec_()
    if data['already_login']=="True":
        p.threading.Thread(target=p.show_notification, args=(f"✅  Hello {data['username']}", "green", "white")).start()
        print("Already logged in. Exiting credentials overlay.")
        sys.exit(0)
    main()
