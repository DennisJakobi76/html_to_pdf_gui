import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt
from weasyprint import HTML, CSS


class DropArea(QFrame):
    """Drag & Drop Fläche für Dateien oder Ordner"""

    def __init__(self, parent=None, filetypes=None, folder=False):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(2)
        self.setAcceptDrops(True)
        self.setMinimumHeight(60)
        self.label = QLabel("Datei/Ordner hierher ziehen", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.filetypes = filetypes
        self.folder = folder
        self.path = ""

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if self.folder:
                if not os.path.isdir(path):
                    self.label.setText("Bitte einen Ordner ablegen")
                    return
            elif self.filetypes:
                if not any(path.lower().endswith(ft) for ft in self.filetypes):
                    self.label.setText("Ungültiger Dateityp")
                    return
            self.path = path
            self.label.setText(os.path.basename(
                path) if not self.folder else path)


class HtmlToPdfTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTML → PDF Tool (WeasyPrint)")

        self.html_drop = DropArea(filetypes=[".html", ".htm"])
        self.html_drop.label.setText("HTML-Datei hier ablegen")

        self.css_drop = DropArea(filetypes=[".css"])
        self.css_drop.label.setText("CSS-Datei hier ablegen (optional)")

        self.assets_drop = DropArea(folder=True)
        self.assets_drop.label.setText("Assets-Ordner hier ablegen (optional)")

        self.html_btn = QPushButton("HTML auswählen")
        self.html_btn.clicked.connect(self.choose_html)

        self.css_btn = QPushButton("CSS auswählen")
        self.css_btn.clicked.connect(self.choose_css)

        self.assets_btn = QPushButton("Assets-Ordner auswählen")
        self.assets_btn.clicked.connect(self.choose_assets)

        self.convert_btn = QPushButton("📄 PDF erstellen")
        self.convert_btn.setStyleSheet(
            "background:#4CAF50;color:white;font-weight:bold;padding:8px;")
        self.convert_btn.clicked.connect(self.create_pdf)

        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setStyleSheet(
            "background:#f44336;color:white;font-weight:bold;padding:8px;")
        self.reset_btn.clicked.connect(self.reset_form)

        self.status_label = QLabel("Bereit")
        self.status_label.setStyleSheet("color: gray;")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("HTML-Datei:"))
        layout.addWidget(self.html_drop)
        layout.addWidget(self.html_btn)

        layout.addWidget(QLabel("CSS-Datei (optional):"))
        layout.addWidget(self.css_drop)
        layout.addWidget(self.css_btn)

        layout.addWidget(QLabel("Assets-Ordner (optional):"))
        layout.addWidget(self.assets_drop)
        layout.addWidget(self.assets_btn)

        layout.addWidget(self.convert_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.status_label)

    def choose_html(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "HTML-Datei auswählen", "", "HTML Dateien (*.html *.htm)")
        if path:
            self.html_drop.path = path
            self.html_drop.label.setText(os.path.basename(path))

    def choose_css(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "CSS-Datei auswählen", "", "CSS Dateien (*.css)")
        if path:
            self.css_drop.path = path
            self.css_drop.label.setText(os.path.basename(path))

    def choose_assets(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Assets-Ordner auswählen")
        if folder:
            self.assets_drop.path = folder
            self.assets_drop.label.setText(folder)

    def create_pdf(self):
        html_file = self.html_drop.path
        css_file = self.css_drop.path

        if not html_file:
            self.status_label.setText(
                "⚠️ Bitte HTML-Datei auswählen oder ablegen")
            return

        output, _ = QFileDialog.getSaveFileName(
            self, "PDF speichern unter", "output.pdf", "PDF Dateien (*.pdf)"
        )
        if not output:
            return

        try:
            base_url = os.path.dirname(html_file)

            stylesheets = []
            if css_file:
                stylesheets.append(CSS(filename=css_file))

            HTML(filename=html_file, base_url=base_url).write_pdf(
                target=output,
                stylesheets=stylesheets
            )

            self.status_label.setText(f"✅ PDF erstellt: {output}")
        except Exception as e:
            self.status_label.setText(f"❌ Fehler: {e}")

    def reset_form(self):
        self.html_drop.path = ""
        self.html_drop.label.setText("HTML-Datei hier ablegen")

        self.css_drop.path = ""
        self.css_drop.label.setText("CSS-Datei hier ablegen (optional)")

        self.assets_drop.path = ""
        self.assets_drop.label.setText("Assets-Ordner hier ablegen (optional)")

        self.status_label.setText("Bereit")
        self.status_label.setStyleSheet("color: gray;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HtmlToPdfTool()
    win.resize(500, 600)
    win.show()
    sys.exit(app.exec())
