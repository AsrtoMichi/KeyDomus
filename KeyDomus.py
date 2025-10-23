from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QListWidget, QListWidgetItem, QTabWidget, QSizePolicy, QFrame
)
from PyQt6.QtCore import QStringListModel

import sys
import json


class Translator:
    def __init__(self, path="translations.json", default_lang="en"):
        self.path = path
        self.lang = default_lang
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"Errore nel caricamento delle traduzioni: {e}")
            self.translations = {}

    def set_language(self, lang_code):
        if lang_code in self.translations:
            self.lang = lang_code
        else:
            print(f"Lingua '{lang_code}' non trovata. Uso '{self.lang}'.")

    def t(self, key_path):
        """
        Recupera una traduzione da una chiave annidata, es: "buttons.new"
        """
        keys = key_path.split(".")
        value = self.translations.get(self.lang, {})
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return f"[{key_path}]"
        return value


i18n = Translator()
i18n.set_language("en")

t = i18n.t


class BuildingsForm(QWidget):
    def __init__(self):
        super().__init__()
        self.mode = "idle"
        self.selected_item = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 🔘 Pulsanti (sopra)
        self.button_row = QHBoxLayout()
        self.new_button = QPushButton(t("buttons.new"))
        self.new_button.clicked.connect(self.on_new)
        self.edit_button = QPushButton(t("buttons.edit"))
        self.edit_button.clicked.connect(self.on_edit)
        self.save_button = QPushButton(t("buttons.save"))
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button = QPushButton(t("buttons.cancel"))
        self.cancel_button.clicked.connect(self.on_cancel)
        self.delete_button = QPushButton(t("buttons.delete"))
        self.delete_button.clicked.connect(self.on_delete)

        for btn in [self.new_button, self.edit_button, self.save_button, self.cancel_button, self.delete_button]:
            btn.setFixedHeight(30)
            self.button_row.addWidget(btn)

        layout.addLayout(self.button_row)

        # 🧾 Form campi (sotto)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("buildings.name_building"))
        layout.addWidget(self.name_input)
       
        self.parent_input = QComboBox()
        self.parent_input.setPlaceholderText(t("buildings.parent_building"))
        layout.addWidget(self.parent_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText(t("buildings.address"))
        layout.addWidget(self.address_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(t("commons.note"))
        layout.addWidget(self.notes_input)


        self.update_form_state()
        self.update_buttons()

    def update_form_state(self):
        editable = self.mode in ["new", "edit"]
        self.name_input.setEnabled(editable)
        self.parent_input.setEnabled(editable)
        self.address_input.setEnabled(editable)
        self.notes_input.setEnabled(editable)

    def update_buttons(self):
        self.new_button.setVisible(self.mode == "idle")
        self.edit_button.setVisible(self.mode == "idle" and self.selected_item is not None)
        self.save_button.setVisible(self.mode in ["new", "edit"])
        self.cancel_button.setVisible(self.mode in ["new", "edit"])
        self.delete_button.setVisible(self.mode == "idle" and self.selected_item is not None)

    def load_item(self, item: QListWidgetItem):
        self.selected_item = item
        self.name_input.setText(item.text())
        self.address_input.setText("Indirizzo esempio")
        self.notes_input.setText("Note esempio")
        self.mode = "idle"
        self.update_form_state()
        self.update_buttons()

    def on_new(self):
        self.mode = "new"
        self.selected_item = None
        self.name_input.clear()
        self.address_input.clear()
        self.notes_input.clear()
        self.update_form_state()
        self.update_buttons()

    def on_edit(self):
        if self.selected_item:
            self.mode = "edit"
            self.update_form_state()
            self.update_buttons()

    def on_save(self):
        name = self.name_input.text()
        if self.mode == "edit" and self.selected_item:
            self.selected_item.setText(name)
        elif self.mode == "new":
            self.parent().building_list.addItem(name)
        self.mode = "idle"
        self.update_form_state()
        self.update_buttons()

    def on_cancel(self):
        if self.selected_item:
            self.load_item(self.selected_item)
        else:
            self.name_input.clear()
            self.address_input.clear()
            self.notes_input.clear()
        self.mode = "idle"
        self.update_form_state()
        self.update_buttons()

    def on_delete(self):
        if self.selected_item:
            row = self.parent().building_list.row(self.selected_item)
            self.parent().building_list.takeItem(row)
            self.selected_item = None
            self.name_input.clear()
            self.address_input.clear()
            self.notes_input.clear()
            self.mode = "idle"
            self.update_form_state()
            self.update_buttons()

class BuildingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()

        # Lista + filtri
        left_panel = QVBoxLayout()
        
        left_panel.addWidget(QLabel(t("commons.filters")))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("buildings.find_building"))
        left_panel.addWidget(self.search_input)
        
        self.parent_filter = QComboBox()
        self.parent_filter.addItem(t("commons.all"))
        left_panel.addWidget(self.parent_filter)
        
        self.address_filter = QLineEdit()
        self.address_filter.setPlaceholderText(t("buildings.find_address"))
        left_panel.addWidget(self.address_filter)
        
        left_panel.addWidget(QLabel(t("buildings.list_building")))
        self.building_list = QListWidget()
        self.building_list.itemClicked.connect(self.on_item_selected)

        for name in ["Edificio A", "Edificio B", "Edificio C"]:
            self.building_list.addItem(name)
        
        left_panel.addWidget(self.building_list)

        # Form edificio
        self.form = BuildingsForm()
        self.form.setParent(self)

        top_layout.addLayout(left_panel)
        top_layout.addWidget(self.form)
        layout.addLayout(top_layout)

        # Tabella relazioni
        layout.addWidget(QLabel(t("buildings.relations")))
        self.relations_table = QTableWidget()
        self.relations_table.setColumnCount(1)
        self.relations_table.setHorizontalHeaderLabels([t("buildings.realtions_headers")])
        layout.addWidget(self.relations_table)

    def on_item_selected(self, item: QListWidgetItem):
        self.form.load_item(item)

class DoorForm(QWidget):
    def __init__(self):
        super().__init__()
        self.mode = "idle"
        self.selected_item = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 🔘 Pulsanti (sopra)
        self.button_row = QHBoxLayout()
        self.new_button = QPushButton(t("buttons.new"))
        self.new_button.clicked.connect(self.on_new)
        self.edit_button = QPushButton(t("buttons.edit"))
        self.edit_button.clicked.connect(self.on_edit)
        self.save_button = QPushButton(t("buttons.save"))
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button = QPushButton(t("buttons.cancel"))
        self.cancel_button.clicked.connect(self.on_cancel)
        self.delete_button = QPushButton(t("buttons.delete"))
        self.delete_button.clicked.connect(self.on_delete)

        for btn in [self.new_button, self.edit_button, self.save_button, self.cancel_button, self.delete_button]:
            btn.setFixedHeight(30)
            self.button_row.addWidget(btn)

        layout.addLayout(self.button_row)

        # 🧾 Form campi (sotto)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("doors.name_door"))
        layout.addWidget(self.name_input)
        
        
        self.building_input = QComboBox()
        self.building_input.setPlaceholderText(t("doors.parent_building"))
        layout.addWidget(self.building_input)
        
        pos_layout = QVBoxLayout()
        layout.addLayout(pos_layout)
        
        flor_map = QHBoxLayout()
        pos_layout.addLayout(flor_map)

        self.floor = QLineEdit()
        self.floor.setPlaceholderText(t("doors.floor"))
        flor_map.addWidget(self.floor)
        
        
        self.map_button = QPushButton("Map")
        flor_map.addWidget(self.map_button)

        
        nroom_room = QHBoxLayout()
        pos_layout.addLayout(nroom_room)
        
        self.nroom = QLineEdit()
        self.nroom.setPlaceholderText(t("doors.nroom"))
        nroom_room.addWidget(self.nroom)
        
        self.room = QLineEdit()
        self.room.setPlaceholderText(t("doors.room"))
        nroom_room.addWidget(self.room)
        

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        self.sistem_input = QComboBox()
        self.sistem_input.setPlaceholderText(t("doors.sistem"))
        layout.addWidget(self.sistem_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(t("commons.note"))
        layout.addWidget(self.notes_input)


        self.update_form_state()
        self.update_buttons()

    def update_form_state(self):
        editable = self.mode in ["new", "edit"]
        self.name_input.setEnabled(editable)
        self.building_input.setEnabled(editable)
        self.floor.setEnabled(editable)
        self.map_button.setEnabled(editable)
        self.nroom.setEnabled(editable)
        self.room.setEnabled(editable)
        self.notes_input.setEnabled(editable)

    def update_buttons(self):
        self.new_button.setVisible(self.mode == "idle")
        self.edit_button.setVisible(self.mode == "idle" and self.selected_item is not None)
        self.save_button.setVisible(self.mode in ["new", "edit"])
        self.cancel_button.setVisible(self.mode in ["new", "edit"])
        self.delete_button.setVisible(self.mode == "idle" and self.selected_item is not None)

    def load_item(self, item: QListWidgetItem):
        self.selected_item = item
        self.mode = "idle"
        self.update_form_state()
        self.update_buttons()

    def on_new(self):
        self.mode = "new"
        self.selected_item = None
        self.name_input.clear()
        self.building_input.clear()
        self.floor.clear()
        self.nroom.clear()
        self.room.clear()
        self.notes_input.clear()
        self.update_form_state()
        self.update_buttons()

    def on_edit(self):
        if self.selected_item:
            self.mode = "edit"
            #load data
            self.update_form_state()
            self.update_buttons()

    def on_save(self):
        name = self.name_input.text()
        if self.mode == "edit" and self.selected_item:
            self.selected_item.setText(name)
        elif self.mode == "new":
            self.parent().door_list.addItem(name)
        self.mode = "idle"
        self.update_form_state()
        self.update_buttons()

    def on_cancel(self):
        if self.selected_item:
            self.load_item(self.selected_item)
        else:
            self.name_input.clear()
            #self.address_input.clear()
            self.notes_input.clear()
        self.mode = "idle"
        self.update_form_state()
        self.update_buttons()

    def on_delete(self):
        if self.selected_item:
            row = self.parent().door_list.row(self.selected_item)
            self.parent().door_list.takeItem(row)
            self.selected_item = None
            self.name_input.clear()
            self.address_input.clear()
            self.notes_input.clear()
            self.mode = "idle"
            self.update_form_state()
            self.update_buttons()

class DoorsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()

        # Lista + filtri
        left_panel = QVBoxLayout()
        
        left_panel.addWidget(QLabel(t("commons.filters")))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("doors.find_door"))
        left_panel.addWidget(self.search_input)
        
        self.building_filter = QComboBox()
        self.building_filter.setPlaceholderText(t("doors.find_building"))
        left_panel.addWidget(self.building_filter)
        
        self.sistem_filter = QComboBox()
        self.sistem_filter.setPlaceholderText(t("doors.find_keysistem"))
        left_panel.addWidget(self.sistem_filter)
                
        self.door_list = QListWidget()
        self.door_list.itemClicked.connect(self.on_item_selected)
        left_panel.addWidget(self.door_list)

        for name in ["Edificio A", "Edificio B", "Edificio C"]:
            self.door_list.addItem(name)


        left_panel.addWidget(QLabel(t("doors.list_door")))
        

        # Form edificio
        self.form = DoorForm()
        self.form.setParent(self)

        top_layout.addLayout(left_panel)
        top_layout.addWidget(self.form)
        layout.addLayout(top_layout)

        # Tabella relazioni
        layout.addWidget(QLabel(t("doors.relations")))
        self.relations_table = QTableWidget()
        self.relations_table.setColumnCount(3)
        self.relations_table.setHorizontalHeaderLabels(list(t("doors.relations_folders")))
        layout.addWidget(self.relations_table)

    def on_item_selected(self, item: QListWidgetItem):
        self.form.load_item(item)

class SistemsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()

class KeysTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()
        
class EmployeesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()
        
class ActionsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()

class DeadlinesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()

class JournalTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()





class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KeyDomus")
        layout = QVBoxLayout()
        self.setLayout(layout)

        tabs = QTabWidget()
        tabs.addTab(BuildingsTab(), t("buildings.title"))
        tabs.addTab(DoorsTab(), t("doors.title") )
        tabs.addTab(SistemsTab(), t("sistems.title"))
        tabs.addTab(KeysTab(), t("keys.title"))
        tabs.addTab(EmployeesTab(), t("employees.title"))
        tabs.addTab(ActionsTab(), t("actions.title"))
        tabs.addTab(DeadlinesTab(), t("deadlines.title"))
        tabs.addTab(JournalTab(), t("journal.title"))
        

        layout.addWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
