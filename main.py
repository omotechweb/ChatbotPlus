import sys
import json
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QScrollArea, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt
from datetime import datetime

class BubbleLabel(QLabel):
    def __init__(self, text, is_user):
        super().__init__(text)
        self.is_user = is_user
        self.setWordWrap(True)
        self.setContentsMargins(15, 10, 15, 10)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        if self.is_user:
            # Apple Messages mavi baloncuk sağda
            return """
                QLabel {
                    background-color: #0A84FF;
                    color: white;
                    border-radius: 16px;
                    padding: 10px;
                    font-size: 14pt;
                }
            """
        else:
            # Apple Messages gri baloncuk solda
            return """
                QLabel {
                    background-color: #2C2C2E;
                    color: white;
                    border-radius: 16px;
                    padding: 10px;
                    font-size: 14pt;
                }
            """

class ChatMessage(QWidget):
    def __init__(self, text, is_user):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft)

        bubble = BubbleLabel(text, is_user)
        max_width = 350
        bubble.setMaximumWidth(max_width)

        if is_user:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()

        self.setLayout(layout)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Apple Mesajlar Temalı Chatbot (Dark Mode)")
        self.resize(500, 700)
        self.setStyleSheet("background-color: #1C1C1E;")

        main_layout = QVBoxLayout(self)

        # Scroll alanı ve içerik widgetı
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.addStretch()
        self.scroll.setWidget(self.chat_content)

        # Input ve buton
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Mesajınızı yazın...")
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #3A3A3C;
                border: none;
                padding: 12px;
                font-size: 14pt;
                border-radius: 18px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0A84FF;
            }
        """)

        self.send_button = QPushButton("Gönder")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0A84FF;
                color: white;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 18px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #0063E0;
            }
        """)

        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)

        main_layout.addWidget(self.scroll)
        main_layout.addLayout(input_layout)

        self.send_button.clicked.connect(self.send_message)
        self.input_line.returnPressed.connect(self.send_message)

        self.load_rules()

    def load_rules(self):
        with open("rules.json", "r", encoding="utf-8") as f:
            self.rules_data = json.load(f)

        # Kuralları tek bir listeye indiriyoruz
        self.rules = []
        for category_block in self.rules_data:
            inputs = [word.lower() for word in category_block.get("input", [])]
            response = category_block["response"]
            if isinstance(response, str):
                response = [response]

            self.rules.append({
                "input": inputs,
                "response": response,
                "category": category_block.get("category", "Genel")
            })

    def send_message(self):
        user_text = self.input_line.text().strip()
        if not user_text:
            return

        self.add_chat_message(user_text, True)
        self.input_line.clear()

        response = self.get_response(user_text)
        self.add_chat_message(response, False)

    def add_chat_message(self, text, is_user):
        msg = ChatMessage(text, is_user)
        # Mesajları scroll alanına en üstte değil en altta ekle
        self.chat_layout.insertWidget(self.chat_layout.count()-1, msg)
        # Scrollu en alta getir
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def get_response(self, user_text):
        user_text_lower = user_text.lower()

        best_rule = None
        best_score = 0

        for rule in self.rules:
            match_count = 0
            for kw in rule["input"]:
                if kw in user_text_lower:
                    match_count += 1
            if match_count > best_score:
                best_score = match_count
                best_rule = rule

        if best_rule and best_score > 0:
            response = random.choice(best_rule["response"])
            response = response.replace("{time}", datetime.now().strftime("%H:%M"))
            response = response.replace("{date}", datetime.now().strftime("%d %B %Y"))
            return response
        else:
            fallback = [
                "Üzgünüm, tam anlayamadım. Başka bir şekilde söyler misin? 🤔",
                "Hmm, bu konuda bilgim yok. Başka bir şey sormak ister misin?",
                "Bana biraz daha ipucu verir misin? 🎯",
                "İlginç! Ama bunu tam anlayamadım. Başka bir şey deneyelim mi?"
            ]
            return random.choice(fallback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
