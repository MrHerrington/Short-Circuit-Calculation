from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtCore import Qt

app = QApplication([])
text_edit = QTextEdit()

def on_key_filter(event):
    if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
        text = text_edit.toPlainText()
        if text.endswith('\n'):
            print(f"Finished input: {text}")

text_edit.eventFilter = on_key_filter
text_edit.show()
app.exec_()