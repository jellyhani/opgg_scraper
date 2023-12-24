import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup
import json

class FetchThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nickname = None

    def set_nickname(self, nickname):
        self.nickname = nickname

    def run(self):
        if self.nickname:
            url = f"https://www.op.gg/summoners/KR/{self.nickname.lower()}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

            if script_tag:
                json_data = script_tag.string
                with open(f'{self.nickname}_opgg_data.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json.loads(json_data), json_file, ensure_ascii=False, indent=2)

                self.finished_signal.emit()
            else:
                QMessageBox.warning(None, 'Error', 'Script tag not found.')
        else:
            QMessageBox.warning(None, 'Error', 'Please enter a nickname.')

class OPGGScraper(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.fetch_thread = FetchThread()
        self.fetch_thread.finished_signal.connect(self.on_fetch_finished)

    def init_ui(self):
        self.setWindowTitle('OP.GG Scraper')
        self.setGeometry(300, 300, 400, 150)

        layout = QVBoxLayout()

        self.input_nickname = QLineEdit(self)
        self.input_nickname.setPlaceholderText('Nickname#Tag')
        layout.addWidget(self.input_nickname)

        self.fetch_button = QPushButton('저장', self)
        self.fetch_button.clicked.connect(self.start_fetch_thread)
        layout.addWidget(self.fetch_button)

        self.setLayout(layout)

    def start_fetch_thread(self):
        nickname = self.input_nickname.text()
        self.fetch_thread.set_nickname(nickname)
        self.fetch_thread.start()

    def on_fetch_finished(self):
        QMessageBox.information(self, 'Success', f"JSON data saved to {self.fetch_thread.nickname}_opgg_data.json")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OPGGScraper()
    window.show()
    sys.exit(app.exec_())
