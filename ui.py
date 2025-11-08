# ui.py
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QDateEdit, QComboBox, QFrame, QMessageBox
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QDate
from datetime import date
from core.loshu import render_loshu_grid
from core.numerology_calculations import calculate_all


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔮 Numerology Analyzer")
        self.setGeometry(200, 100, 1150, 720)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0B0D17;
            }
            QLabel {
                color: #E0E6F8;
                font-family: 'Segoe UI';
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #141A29;
                color: #E0E6F8;
                border: 1px solid #2A3348;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QPushButton {
                border-radius: 10px;
                font-weight: 600;
                color: white;
                padding: 8px 16px;
                font-family: 'Segoe UI';
            }
            QPushButton#computeBtn {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00C853, stop:1 #009624);
            }
            QPushButton#computeBtn:hover {
                background-color: #00BFA5;
            }
            QPushButton#pdfBtn {
                background-color: #1976D2;
            }
            QPushButton#pdfBtn:hover {
                background-color: #0D47A1;
            }
            QPushButton#clearBtn {
                background-color: #424242;
            }
            QPushButton#clearBtn:hover {
                background-color: #616161;
            }
            QFrame#card {
                background-color: #141A29;
                border-radius: 12px;
                border: 1px solid #2A3348;
                padding: 12px;
            }
        """)

        # Main container
        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # LEFT PANEL
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)

        # App title
        title = QLabel("🔢 Numerology Analyzer")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #9BE7FF;")
        left_panel.addWidget(title, alignment=Qt.AlignLeft)

        # Input Section
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Full Name")

        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate(2000, 1, 1))

        self.gender_box = QComboBox()
        self.gender_box.addItems(["Male", "Female", "Other"])

        input_labels = ["Full Name", "Date of Birth", "Gender"]
        input_widgets = [self.name_input, self.dob_input, self.gender_box]

        for label, widget in zip(input_labels, input_widgets):
            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI", 11))
            left_panel.addWidget(lbl)
            left_panel.addWidget(widget)

        # Buttons layout
        btn_layout = QHBoxLayout()
        self.compute_btn = QPushButton("Compute")
        self.compute_btn.setObjectName("computeBtn")
        self.compute_btn.clicked.connect(self.compute_analysis)

        self.pdf_btn = QPushButton("Export PDF")
        self.pdf_btn.setObjectName("pdfBtn")

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.clicked.connect(self.clear_all)

        btn_layout.addWidget(self.compute_btn)
        btn_layout.addWidget(self.pdf_btn)
        btn_layout.addWidget(self.clear_btn)
        left_panel.addLayout(btn_layout)

        # Result Card
        self.result_card = QFrame()
        self.result_card.setObjectName("card")
        result_layout = QVBoxLayout(self.result_card)

        result_title = QLabel("🧮 Your Numerology Results")
        result_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        result_title.setStyleSheet("color: #80DEEA; margin-bottom: 8px;")
        result_layout.addWidget(result_title)

        self.mulank_label = QLabel("Mulank (Birth Number): —")
        self.bhagyank_label = QLabel("Bhagyank (Destiny Number): —")
        self.name_label = QLabel("Name Number (Chaldean): —")
        self.angel_label = QLabel("Angel Number: —")

        for lbl in [self.mulank_label, self.bhagyank_label, self.name_label, self.angel_label]:
            lbl.setFont(QFont("Segoe UI", 11))
            result_layout.addWidget(lbl)

        left_panel.addWidget(self.result_card)

        # RIGHT PANEL (Lo Shu Grid)
        self.grid_label = QLabel()
        self.grid_label.setAlignment(Qt.AlignCenter)
        self.grid_label.setStyleSheet("""
            background-color: #10131F;
            border-radius: 15px;
            border: 1px solid #2A3348;
        """)

        main_layout.addLayout(left_panel, stretch=4)
        main_layout.addWidget(self.grid_label, stretch=6)

        self.setCentralWidget(container)

    # -----------------------
    # Compute Function
    # -----------------------
    def compute_analysis(self):
        name = self.name_input.text().strip()
        gender = self.gender_box.currentText()
        qdate = self.dob_input.date()
        dob = date(qdate.year(), qdate.month(), qdate.day())

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter your full name.")
            return

        results = calculate_all(name, dob, gender)

        # Display results
        self.mulank_label.setText(f"Mulank (Birth Number): {results['Mulank']}")
        self.bhagyank_label.setText(f"Bhagyank (Destiny Number): {results['Bhagyank']}")
        self.name_label.setText(
            f"Name Number (Chaldean): {results['Name Total']} → {results['Name Number']}"
        )
        self.angel_label.setText(f"Angel Number: {results['Angel Number']}")

        # Combine DOB digits + numerology results for Lo Shu grid
        digits = []

        # 1️⃣ Add all digits from full date of birth
        dob_digits = [int(d) for d in f"{dob.day:02d}{dob.month:02d}{dob.year}"]
        digits.extend(dob_digits)

        # 2️⃣ Add Mulank, Bhagyank, Name Number, Angel Number digits
        for key in ["Mulank", "Bhagyank", "Angel Number"]:
            digits.extend(int(d) for d in str(results[key]))


        # Render and display Lo Shu Grid
        img = render_loshu_grid(digits, size=520)
        img.save("loshu_preview.png")
        self.grid_label.setPixmap(
            QPixmap("loshu_preview.png").scaled(520, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    # -----------------------
    # Clear Function
    # -----------------------
    def clear_all(self):
        self.name_input.clear()
        self.mulank_label.setText("Mulank (Birth Number): —")
        self.bhagyank_label.setText("Bhagyank (Destiny Number): —")
        self.name_label.setText("Name Number (Chaldean): —")
        self.angel_label.setText("Angel Number: —")
        self.grid_label.clear()


# Run app directly
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
