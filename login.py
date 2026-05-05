import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('登录')
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        
        title = QLabel('网商园图片下载')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        layout.addWidget(QLabel('用户名:'))
        self.username_input = QLineEdit()
        self.username_input.setText('admin')
        layout.addWidget(self.username_input)
        
        layout.addWidget(QLabel('密码:'))
        self.password_input = QLineEdit()
        self.password_input.setText('123456')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(20)
        
        login_btn = QPushButton('登录')
        login_btn.clicked.connect(self.check_login)
        login_btn.setMinimumHeight(40)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
        
    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if username == 'admin' and password == '123456':
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '用户名或密码错误！')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = LoginDialog()
    if dialog.exec_() == QDialog.Accepted:
        print('登录成功')
