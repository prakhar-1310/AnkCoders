# ui.py — FULL UPDATED MODERN UI

import os
from datetime import date
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QDateEdit, QComboBox, QFrame, QMessageBox,
    QSizePolicy, QFileDialog, QSpacerItem, QScrollArea
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QDate
from PIL.ImageQt import ImageQt

from core.numerology_calculations import calculate_all
from core.loshu import render_loshu_grid
from core.driver_conductor import get_phase_analysis
from core.pdf_report import create_pdf_report

HALF_STAR = "⯨"
FULL_STAR = "★"

def make_chip(text):
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
    lbl.setStyleSheet(
        "QLabel { background-color: #1E2A3B; color: #CFE9FF; "
        "border-radius: 12px; padding: 6px 12px; margin-right:4px; }"
    )
    lbl.setContentsMargins(0, 0, 0, 0)
    return lbl

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔮 Numerology Analyzer")
        self.setGeometry(100, 40, 1360, 820)
        self._last_report = None
        self.setStyleSheet(self._main_styles())

        # Root layout
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0,0,0,0)
        root_layout.setSpacing(0)

        # Left Panel (scrollable)
        left_panel = self._build_left_panel()
        left_panel.setMinimumWidth(400)
        left_panel.setMaximumWidth(600)
        left_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Right Panel (Lo Shu)
        right_panel = self._build_right_panel()
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Layout ratio: Left wider, right narrower
        root_layout.addWidget(left_panel, 3)
        root_layout.addWidget(right_panel, 2)

        self.setCentralWidget(root)

    # -----------------------
    # Styles
    # -----------------------
    def _main_styles(self):
        return """
        QMainWindow { background-color: #071018; }
        QLabel { color: #E8F1FF; font-family: 'Segoe UI'; }
        QLineEdit, QComboBox, QDateEdit {
            background-color: #0F1720;
            border: 1px solid #24313f;
            color: #E8F1FF;
            border-radius: 8px;
            padding: 8px;
        }
        QPushButton { border-radius: 10px; padding: 8px 14px; font-weight:600; }
        QPushButton#computeBtn { background-color: #00C853; color:black; }
        QPushButton#exportBtn { background-color: #1976D2; color:white; }
        QPushButton#clearBtn { background-color: #424242; color:white; }
        QFrame#card { background-color: #0E1620; border-radius: 16px; border:1px solid #263144; padding:14px; }
        QScrollArea { border:none; }
        """

    # -----------------------
    # Left Panel
    # -----------------------
    def _build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(8)

        # Title
        title = QLabel("🔢 Numerology Analyzer")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color:#7BD1FF;")
        layout.addWidget(title)

        # Inputs
        layout.addWidget(self._label("Full Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        layout.addWidget(self.name_input)

        layout.addWidget(self._label("Date of Birth"))
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("dd-MM-yyyy")
        self.dob_input.setDate(QDate(2000,1,1))
        layout.addWidget(self.dob_input)

        layout.addWidget(self._label("Gender"))
        self.gender_box = QComboBox()
        self.gender_box.addItems(["Male","Female","Other"])
        layout.addWidget(self.gender_box)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignHCenter)

        self.compute_btn = QPushButton("Compute")
        self.compute_btn.setObjectName("computeBtn")
        self.compute_btn.clicked.connect(self.compute_analysis)

        self.export_btn = QPushButton("Export PDF")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.clicked.connect(self.export_pdf)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.clicked.connect(self.clear_all)

        for b in (self.compute_btn, self.export_btn, self.clear_btn):
            b.setMinimumWidth(110)
            b.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            btn_row.addWidget(b)

        layout.addLayout(btn_row)

        # Cards
        layout.addWidget(self._result_card())
        layout.addWidget(self._phase_card())

        layout.addStretch(1)

        # Scrollable wrapper
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(panel)
        return scroll

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet("color:#B7D6E8;")
        return lbl

    # -----------------------
    # Result Card
    # -----------------------
    def _result_card(self):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        hdr = QLabel("📘 Numerology Summary")
        hdr.setFont(QFont("Segoe UI",14,QFont.Weight.Bold))
        hdr.setStyleSheet("color:#80D8FF;")
        layout.addWidget(hdr)

        def mk(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI",11))
            lbl.setWordWrap(True)
            return lbl

        self.mulank_label = mk("Mulank (Birth Number): —")
        self.bhagyank_label = mk("Bhagyank (Destiny Number): —")
        self.name_label = mk("Name Number (Chaldean): —")
        self.angel_label = mk("Angel Number: —")

        for w in (self.mulank_label, self.bhagyank_label, self.name_label, self.angel_label):
            layout.addWidget(w)

        return card

    # -----------------------
    # Driver–Conductor Card
    # -----------------------
    def _phase_card(self):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(6)

        hdr = QLabel("🧿 Driver–Conductor Analysis")
        hdr.setFont(QFont("Segoe UI",14,QFont.Weight.Bold))
        hdr.setStyleSheet("color:#80D8FF;")
        layout.addWidget(hdr)

        # Phase 1
        self.ph1_title = QLabel("0–40 Years (Mulank → Bhagyank)")
        self.ph1_title.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
        self.ph1_title.setStyleSheet("color:#9BE7FF;")
        layout.addWidget(self.ph1_title)

        self.ph1_stars = QLabel("Stars: —")
        self.ph1_rating = QLabel("Rating: —")
        self.ph1_meaning = QLabel("Meaning: —")
        self.ph1_keywords_layout = QHBoxLayout()
        self.ph1_keywords_layout.setSpacing(6)

        for w in (self.ph1_stars, self.ph1_rating, self.ph1_meaning):
            w.setFont(QFont("Segoe UI",10))
            w.setWordWrap(True)
            layout.addWidget(w)

        kw_widget = QWidget()
        kw_widget.setLayout(self.ph1_keywords_layout)
        layout.addWidget(kw_widget)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1f2a36; margin:6px 0;")
        layout.addWidget(sep)

        # Phase 2
        self.ph2_title = QLabel("40–80 Years (Bhagyank → Mulank)")
        self.ph2_title.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
        self.ph2_title.setStyleSheet("color:#9BE7FF;")
        layout.addWidget(self.ph2_title)

        self.ph2_stars = QLabel("Stars: —")
        self.ph2_rating = QLabel("Rating: —")
        self.ph2_meaning = QLabel("Meaning: —")
        self.ph2_keywords_layout = QHBoxLayout()
        self.ph2_keywords_layout.setSpacing(6)

        for w in (self.ph2_stars,self.ph2_rating,self.ph2_meaning):
            w.setFont(QFont("Segoe UI",10))
            w.setWordWrap(True)
            layout.addWidget(w)

        kw_widget2 = QWidget()
        kw_widget2.setLayout(self.ph2_keywords_layout)
        layout.addWidget(kw_widget2)

        return card

    # -----------------------
    # Right Panel
    # -----------------------
    def _build_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background-color:#061018;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(26, 12, 26, 12)  # slightly reduced top/bottom margins
        layout.setSpacing(12)

        title = QLabel("🧮 Lo Shu Grid")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color:#80D8FF;")
        layout.addWidget(title, alignment=Qt.AlignHCenter)

        # Grid label container (to center and scale properly)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.grid_label = QLabel("Your Lo Shu Grid will appear here.")
        self.grid_label.setAlignment(Qt.AlignCenter)
        self.grid_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_label.setMinimumSize(0, 0)
        self.grid_label.setStyleSheet(
            "background-color:#0b1320; border-radius:20px; border:2px solid #263144; color:#6D8297;"
        )

        container_layout.addWidget(self.grid_label)
        layout.addWidget(container, stretch=1)  # stretch ensures grid fills panel vertically

        return panel


    # -----------------------
    # Compute Analysis
    # -----------------------
    def compute_analysis(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self,"Missing Input","Please enter your full name.")
            return

        dob_q = self.dob_input.date()
        dob = date(dob_q.year(),dob_q.month(),dob_q.day())
        gender = self.gender_box.currentText()

        try:
            results = calculate_all(name,dob,gender)
        except Exception as e:
            QMessageBox.critical(self,"Calculation Error",f"Failed to compute numerology:\n{e}")
            return

        self.mulank_label.setText(f"Mulank (Birth Number): {results['Mulank']}")
        self.bhagyank_label.setText(f"Bhagyank (Destiny Number): {results['Bhagyank']}")
        self.name_label.setText(f"Name Number (Chaldean): {results['Name Number']} (Total: {results['Name Total']})")
        self.angel_label.setText(f"Angel Number: {results['Angel Number']}")

        phases = get_phase_analysis(results["Mulank"],results["Bhagyank"])
        p1, p2 = phases["0-40"],phases["40-80"]

        self.ph1_stars.setText(f"Stars: {p1.get('stars_raw') or 'Unknown'}")
        self.ph1_rating.setText(f"Rating: {p1.get('rating_clean') or 'N/A'}")
        self.ph1_meaning.setText(f"Meaning: {p1.get('meaning_raw') or '—'}")
        self._populate_chips(self.ph1_keywords_layout,p1.get("meaning_clean",[]))

        self.ph2_stars.setText(f"Stars: {p2.get('stars_raw') or 'Unknown'}")
        self.ph2_rating.setText(f"Rating: {p2.get('rating_clean') or 'N/A'}")
        self.ph2_meaning.setText(f"Meaning: {p2.get('meaning_raw') or '—'}")
        self._populate_chips(self.ph2_keywords_layout,p2.get("meaning_clean",[]))

        # Lo Shu digits
        digits = [int(d) for d in f"{dob.day:02d}{dob.month:02d}{dob.year}"]
        for key in ["Mulank","Bhagyank","Angel Number"]:
            digits.extend(int(d) for d in str(results[key]))

        try:
            pil_img = render_loshu_grid(digits,size=800)
            self.loshu_original = pil_img
            qim = ImageQt(pil_img)
            pix = QPixmap.fromImage(qim)
            pix = pix.scaled(self.grid_label.width(), self.grid_label.width(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.grid_label.setPixmap(pix)
            pil_img.save("loshu_preview.png")
        except Exception as e:
            QMessageBox.warning(self,"Lo Shu Error",f"Failed to render Lo Shu grid:\n{e}")

        self._last_report = {
            "name":name,"dob":dob,"gender":gender,
            "results":results,"phases":phases,
            "loshu_image":os.path.abspath("loshu_preview.png") if os.path.exists("loshu_preview.png") else None
        }


    def _populate_chips(self, layout, keywords):
        while layout.count():
            item = layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        if not keywords:
            lbl = QLabel("—")
            lbl.setFont(QFont("Segoe UI",10))
            lbl.setStyleSheet("color:#8EAFC8;")
            layout.addWidget(lbl)
            return
        for kw in keywords:
            layout.addWidget(make_chip(kw))

    # -----------------------
    # Export PDF
    # -----------------------
    def export_pdf(self):
        if not self._last_report:
            QMessageBox.information(self,"Nothing to export","Please compute analysis first.")
            return
        path,_ = QFileDialog.getSaveFileName(self,"Save PDF Report","Numerology_Report.pdf","PDF Files (*.pdf)")
        if not path: return
        try:
            create_pdf_report(path,self._last_report)
            QMessageBox.information(self,"Exported",f"PDF saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self,"Export Error",f"Failed to create PDF:\n{e}")

    # -----------------------
    # Clear All
    # -----------------------
    def clear_all(self):
        self.name_input.clear()
        self.mulank_label.setText("Mulank (Birth Number): —")
        self.bhagyank_label.setText("Bhagyank (Destiny Number): —")
        self.name_label.setText("Name Number (Chaldean): —")
        self.angel_label.setText("Angel Number: —")
        self.grid_label.clear()
        self.grid_label.setText("Your Lo Shu Grid will appear here.")
        self._populate_chips(self.ph1_keywords_layout,[])
        self._populate_chips(self.ph2_keywords_layout,[])
        self.ph1_stars.setText("Stars: —")
        self.ph1_rating.setText("Rating: —")
        self.ph1_meaning.setText("Meaning: —")
        self.ph2_stars.setText("Stars: —")
        self.ph2_rating.setText("Rating: —")
        self.ph2_meaning.setText("Meaning: —")
        if os.path.exists("loshu_preview.png"):
            try: os.remove("loshu_preview.png")
            except: pass
        self._last_report = None
    
    def resizeEvent(self, event):
        if hasattr(self, "_loshu_original") and self._loshu_original:
            qim = ImageQt(self._loshu_original)
            pix = QPixmap.fromImage(qim)
            size = self.grid_label.width()  # make square
            pix = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.grid_label.setPixmap(pix)
        super().resizeEvent(event)




if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
