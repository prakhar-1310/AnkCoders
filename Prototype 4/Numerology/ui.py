# ui.py — SOFT PURPLE UI + FULL RIGHT BG IMAGE + TRANSPARENT GRID

import os
# from core.util import resource_path

from datetime import date
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QDateEdit, QComboBox, QFrame, QMessageBox,
    QSizePolicy, QFileDialog, QScrollArea
)
from PySide6.QtGui import QFont, QPixmap, QPainter
from PySide6.QtCore import Qt, QDate, QTimer
from PIL.ImageQt import ImageQt
from PIL import Image

from core.numerology_calculations import calculate_all
from core.driver_conductor import get_phase_analysis
from core.pdf_report import create_pdf_report
from core.loshu import render_loshu_grid


def make_chip(text):
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
    lbl.setStyleSheet(
        "QLabel { background-color: #ccc4ff; color: #3a2a60; "
        "border-radius: 12px; padding: 6px 12px; margin-right:4px; }"
    )
    return lbl


class MainWindow(QMainWindow):
    MAX_GRID_SIZE = 600  # cap grid size—no fullscreen zoom

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔮Numerology Analyzer")
        self.setGeometry(100, 40, 1360, 820)

        self._last_report = None
        self._loshu_original = None
        self._loshu_display_size = None

        self.setStyleSheet(self._main_styles())  # Apply theme

        # Root layout
        root = QWidget()
        root.setStyleSheet("background-color:#C9AOFF;")  # Soft Lavender Purple
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        root_layout.addWidget(left_panel, 3)
        root_layout.addWidget(right_panel, 2)

        self.setCentralWidget(root)

        QTimer.singleShot(0, self.show_default_loshu_background)

    # =====================================================================
    # GLOBAL STYLES
    # =====================================================================
    def _main_styles(self):
        return """
        QMainWindow { background-color: #C9AOFF; }
        QLabel { color: #3A2A60; font-family: 'Segoe UI'; }

        QLineEdit, QComboBox, QDateEdit {
            background-color: #FFFFFF;
            border: 1px solid #A78BFA;
            color: #3A2A60;
            border-radius: 8px;
            padding: 8px;
        }

        QPushButton { 
            border-radius: 10px; 
            padding: 8px 14px; 
            font-weight:600; 
        }
        QPushButton#computeBtn { background-color: #7C4DFF; color:white; }
        QPushButton#exportBtn { background-color: #5E35B1; color:white; }
        QPushButton#clearBtn { background-color: #8E24AA; color:white; }

        QFrame#card {
            background-color: #3A2A60;
            border-radius: 16px;
            border:1px solid #7C4DFF;
            padding:14px;
            color:white;
        }

        QScrollArea { background-color:#C9AOFF; border:none; }
        """

    # =====================================================================
    # LEFT PANEL
    # =====================================================================
    def _build_left_panel(self):

        panel = QWidget()
        panel.setStyleSheet("background-color:#C9AOFF;")
        layout = QVBoxLayout(panel)

        title = QLabel("Numerology Analyzer")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color:#7c4dff;")
        layout.addWidget(title)

        # Inputs
        layout.addWidget(self._label("Full Name"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(self._label("Date of Birth"))
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDisplayFormat("dd-MM-yyyy")
        self.dob_input.setDate(QDate(2000, 1, 1))
        layout.addWidget(self.dob_input)

        layout.addWidget(self._label("Gender"))
        self.gender_box = QComboBox()
        self.gender_box.addItems(["Male", "Female", "Other"])
        layout.addWidget(self.gender_box)

        # Buttons
        btn_row = QHBoxLayout()
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
            b.setMinimumWidth(120)
            btn_row.addWidget(b)

        layout.addLayout(btn_row)

        layout.addWidget(self._result_card())
        layout.addWidget(self._phase_card())
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(panel)
        return scroll

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setStyleSheet("color:#7c4dff;")
        return lbl

    # =====================================================================
    # SUMMARY CARD
    # =====================================================================
    def _result_card(self):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        hdr = QLabel("📘 Numerology Summary")
        hdr.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#C3B3FF;")
        layout.addWidget(hdr)

        def mk(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet("color:white;")
            return lbl

        self.mulank_label = mk("Mulank (Birth Number): —")
        self.bhagyank_label = mk("Bhagyank (Destiny Number): —")
        self.name_label = mk("Name Number (Chaldean): —")
        self.angel_label = mk("Angel Number: —")

        for w in (self.mulank_label, self.bhagyank_label, self.name_label, self.angel_label):
            layout.addWidget(w)

        return card

    # =====================================================================
    # DRIVER–CONDUCTOR CARD
    # =====================================================================
    def _phase_card(self):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        hdr = QLabel("🧿 Driver–Conductor Analysis")
        hdr.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hdr.setStyleSheet("color:#C3B3FF;")
        layout.addWidget(hdr)

        def new_lbl(t):
            lab = QLabel(t)
            lab.setFont(QFont("Segoe UI", 11))
            lab.setStyleSheet("color:white;")
            return lab

        self.ph1_title = new_lbl("0–40 Years (Mulank → Bhagyank)")
        self.ph1_stars = new_lbl("Stars: —")
        self.ph1_rating = new_lbl("Rating: —")
        self.ph1_meaning = new_lbl("Meaning: —")
        self.ph1_keywords_layout = QHBoxLayout()

        layout.addWidget(self.ph1_title)
        layout.addWidget(self.ph1_stars)
        layout.addWidget(self.ph1_rating)
        layout.addWidget(self.ph1_meaning)

        kw1 = QWidget()
        kw1.setLayout(self.ph1_keywords_layout)
        layout.addWidget(kw1)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:white; margin:8px 0;")
        layout.addWidget(sep)

        self.ph2_title = new_lbl("40–80 Years (Bhagyank → Mulank)")
        self.ph2_stars = new_lbl("Stars: —")
        self.ph2_rating = new_lbl("Rating: —")
        self.ph2_meaning = new_lbl("Meaning: —")
        self.ph2_keywords_layout = QHBoxLayout()

        layout.addWidget(self.ph2_title)
        layout.addWidget(self.ph2_stars)
        layout.addWidget(self.ph2_rating)
        layout.addWidget(self.ph2_meaning)

        kw2 = QWidget()
        kw2.setLayout(self.ph2_keywords_layout)
        layout.addWidget(kw2)

        return card

    # =====================================================================
    # RIGHT PANEL (FULL BACKGROUND IMAGE)
    # =====================================================================
    def _build_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet("background-color:#white;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Lo Shu Grid")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet("color:#7c4dff; padding:10px;")
        layout.addWidget(title)

        # BACKGROUND IMAGE LABEL (fills entire right side)
        self.bg_label = QLabel()
        self.bg_label.setAlignment(Qt.AlignCenter)
        self.bg_label.setStyleSheet("border:none;")
        self.bg_label.setScaledContents(True)  # FULL AREA

        layout.addWidget(self.bg_label, stretch=1)
        return panel

    # =====================================================================
    # SHOW FULL-SIZE BACKGROUND IMAGE
    # =====================================================================
    def show_default_loshu_background(self):
        bg_path = "assets/bg.png"

        if os.path.exists(bg_path):
            bg = QPixmap(bg_path)
        else:
            bg = QPixmap(800, 800)
            bg.fill(Qt.darkMagenta)

        # Fill entire background area → NO size limit
        self.bg_label.setPixmap(bg.scaled(
            self.bg_label.width(),
            self.bg_label.height(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        ))

    # =====================================================================
    # COMPUTE NUMEROLOGY + DRAW TRANSPARENT GRID ON TOP OF BACKGROUND
    # =====================================================================
    def compute_analysis(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Input", "Enter a full name.")
            return

        dob_q = self.dob_input.date()
        dob = date(dob_q.year(), dob_q.month(), dob_q.day())
        gender = self.gender_box.currentText()

        results = calculate_all(name, dob, gender)

        # SUMMARY UI UPDATE
        self.mulank_label.setText(f"Mulank (Birth Number): {results['Mulank']}")
        self.bhagyank_label.setText(f"Bhagyank (Destiny Number): {results['Bhagyank']}")
        self.name_label.setText(f"Name Number (Chaldean): {results['Name Number']} (Total: {results['Name Total']})")
        self.angel_label.setText(f"Angel Number: {results['Angel Number']}")

        # PHASE DATA
        phases = get_phase_analysis(results["Mulank"], results["Bhagyank"])
        p1 = phases["0-40"]
        p2 = phases["40-80"]

        self.ph1_stars.setText(f"Stars: {p1['stars_raw']}")
        self.ph1_rating.setText(f"Rating: {p1['rating_clean']}")
        self.ph1_meaning.setText(f"Meaning: {p1['meaning_raw']}")
        self._populate_chips(self.ph1_keywords_layout, p1["meaning_clean"])

        self.ph2_stars.setText(f"Stars: {p2['stars_raw']}")
        self.ph2_rating.setText(f"Rating: {p2['rating_clean']}")
        self.ph2_meaning.setText(f"Meaning: {p2['meaning_raw']}")
        self._populate_chips(self.ph2_keywords_layout, p2["meaning_clean"])

        # DIGITS FOR LOSHU GRID
        digits = []
        digits.extend(int(d) for d in str(dob.day))
        digits.extend(int(d) for d in str(dob.month))
        digits.extend(int(d) for d in str(dob.year))

        mulank = results["Mulank"]
        bhagyank = results["Bhagyank"]
        angel = results["Angel Number"]

        if mulank != dob.day:
            digits.extend(int(d) for d in str(mulank))

        digits.extend(int(d) for d in str(bhagyank))
        digits.extend(int(d) for d in str(angel))

        # RENDER LOSHU GRID
        pil_img = render_loshu_grid(digits, size=800)
        qim = ImageQt(pil_img)
        grid_pix = QPixmap.fromImage(qim)
        self._loshu_original = grid_pix
        self.overlay_grid_on_background()

        # ---- SAVE LOSHU GRID TEMP FILE ----
        os.makedirs("core/temp", exist_ok=True)
        loshu_path = "core/temp/loshu_grid.png"
        pil_img.save(loshu_path)

        # ---- SAVE CORRECT PAYLOAD FOR PDF ----
        self._last_report = {
            "name": name,
            "dob": dob,
            "gender": gender,
            "results": results,
            "loshu_image": loshu_path,
            "phases": {
                "0-40": p1,
                "40-80": p2
            }
        }

    # =====================================================================
    # OVERLAY THE TRANSPARENT GRID ON THE BG IMAGE
    # =====================================================================
    def overlay_grid_on_background(self):
        if not self._loshu_original:
            return

        base = self.bg_label.pixmap()
        if not base:
            return

        # Create new pixmap same size as background pixmap
        final = QPixmap(base.size())
        final.fill(Qt.transparent)

        painter = QPainter(final)
        painter.drawPixmap(0, 0, base)                    # draw background
        painter.drawPixmap(0, 0, self._loshu_original)    # draw transparent grid
        painter.end()

        self.bg_label.setPixmap(final)

    # =====================================================================
    # POPULATE KEYWORDS
    # =====================================================================
    def _populate_chips(self, layout, keywords):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not keywords:
            lbl = QLabel("—")
            lbl.setStyleSheet("color:white;")
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

    # =====================================================================
    # CLEAR
    # =====================================================================
    def clear_all(self):
        self.name_input.clear()
        self.grid_label_text = "Your Lo Shu Grid will appear here."

        self._populate_chips(self.ph1_keywords_layout, [])
        self._populate_chips(self.ph2_keywords_layout, [])
        self._loshu_original = None

        QTimer.singleShot(0, self.show_default_loshu_background)

    # =====================================================================
    # RESIZE HANDLER (updates background size)
    # =====================================================================
    def resizeEvent(self, event):
        self.show_default_loshu_background()
        if self._loshu_original:
            self.overlay_grid_on_background()
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.showMaximized()
    app.exec()
