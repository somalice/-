import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网商园图片下载 - 测试版")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("✅ GUI界面启动成功！", self)
        label.setStyleSheet("font-size: 24px; color: green;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        label2 = QLabel("如果看到这个窗口，说明PyQt5正常工作", self)
        label2.setStyleSheet("font-size: 14px; color: gray;")
        label2.setAlignment(Qt.AlignCenter)
        layout.addWidget(label2)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
