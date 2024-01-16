import os
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from typing import Optional, List
import sys
import json
from qt_material import get_theme

from utils import ConnectionManager, open_yml_file, setup_logging, find_relative_image_path

if hasattr(sys, '_MEIPASS'):

    resource_dir = sys._MEIPASS
elif 'main.py' in os.listdir(os.path.dirname(os.path.abspath("__main__"))):

    resource_dir = os.path.dirname(os.path.abspath("__main__"))
else:
    resource_dir = os.path.join(os.path.dirname(os.path.abspath("__main__")), 'PathologyUI')

outer_setting = QSettings('PathologyUI', 'ImageViewer')
config_file = outer_setting.value("last_config_file", os.path.join(resource_dir, "config.yml"))
config_data = open_yml_file(os.path.join(resource_dir, config_file))
logger, console_msg = setup_logging(config_data['log_dir'])

if hasattr(sys, '_MEIPASS'):

    resource_dir = sys._MEIPASS
elif 'main.py' in os.listdir(os.path.dirname(os.path.realpath(__file__))):
    resource_dir = os.path.dirname(os.path.realpath(__file__))
elif 'main.py' in os.listdir(os.path.dirname(os.path.abspath("__main__"))):

    resource_dir = os.path.dirname(os.path.abspath("__main__"))
elif 'main.py' in os.path.join(os.path.dirname(os.path.abspath("__main__")), 'PathologyUI'):
    resource_dir = os.path.join(os.path.dirname(os.path.abspath("__main__")), 'PathologyUI')
elif 'main.py' in os.path.join(os.path.dirname(os.path.abspath("__main__")), 'PathologyUI', 'PathologyUI'):
    resource_dir = os.path.join(os.path.dirname(os.path.abspath("__main__")), 'PathologyUI', 'PathologyUI')
else:
    raise (FileNotFoundError(f"Resource directory not found from {os.path.dirname(os.path.abspath('__main__'))}"))


class AboutMessageBox(QDialog):

    def __init__(self, parent: Optional[QWidget] = None):

        super().__init__(parent)

        self.connection_manager = ConnectionManager()

        self.setWindowTitle("About...")

        top_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        path = os.path.join(resource_dir, 'assets/logo.png')
        grey_logo = QPixmap(path).scaled(320, 320, Qt.AspectRatioMode.KeepAspectRatio)
        icon_label = QLabel()
        icon_label.setPixmap(grey_logo)
        left_layout.addStretch(1)
        left_layout.addWidget(icon_label)

        right_layout = QVBoxLayout()
        right_layout.addStretch(1)

        text_layout = QVBoxLayout()

        main_text = QLabel("PathologyUI")
        main_text.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_text.setAlignment(Qt.AlignmentFlag.AlignBottom)
        text_layout.addWidget(main_text)

        right_layout.addLayout(text_layout)
        right_layout.addStretch(1)

        hbox = QHBoxLayout()

        right_layout.addLayout(hbox)

        top_layout.addLayout(right_layout)
        top_layout.addLayout(left_layout)

        self.setLayout(top_layout)




class LoadMessageBox(QDialog):

    def __init__(self, parent: Optional[QWidget] = None):

        super().__init__(parent)

        self.connection_manager = ConnectionManager()

        self.setWindowTitle("PathologyUI")

        top_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        path = os.path.join(resource_dir, 'assets/logo.png')
        logo = QPixmap(path).scaled(320, 320, Qt.AspectRatioMode.KeepAspectRatio)

        if logo.isNull():
            logger.warning(f"Failed to load logo at path: {path}")

        icon_label = QLabel()
        icon_label.setPixmap(logo)
        left_layout.addWidget(icon_label)

        web_text = QLabel("<a href=''>place_holder</a>")
        web_text.setTextFormat(Qt.TextFormat.RichText)
        web_text.setAlignment(Qt.AlignmentFlag.AlignRight)
        web_text.setOpenExternalLinks(True)
        left_layout.addWidget(web_text)

        right_layout = QVBoxLayout()

        spacer = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        right_layout.addStretch()
        main_text = QLabel("PathologyUI Prototype")
        main_text.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_text.setAlignment(Qt.AlignmentFlag.AlignBottom)
        right_layout.addWidget(main_text)

        right_layout.addStretch()

        self.settings = QSettings('PathologyUI', 'ImageViewer')

        self.config_combo = QComboBox(self)
        for file in os.listdir(resource_dir):
            if file.endswith('.yml'):
                self.config_combo.addItem(file)

        last_config_file = self.settings.value("last_config_file", os.path.join(resource_dir, "config.yml"))
        self.config_combo.setCurrentText(os.path.basename(last_config_file))

        config_layout = QVBoxLayout()
        config_box_layout = QHBoxLayout()
        config_label = QLabel("Config file:")
        config_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        config_label.setStyleSheet("font-size: 14px;")
        config_box_layout.addWidget(config_label)
        config_box_layout.addWidget(self.config_combo)
        try:
            combo_text_colour = get_theme(self.settings.value('theme', 'light_red.xml'))['secondaryTextColor']
        except KeyError:
            combo_text_colour = get_theme(self.settings.value('theme', 'light_red.xml'))['secondaryLightColor']
        self.config_combo.setStyleSheet(f"QComboBox:disabled::item {{ color: {combo_text_colour}; }}")
        self.config_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        config_layout.addLayout(config_box_layout)
        right_layout.addLayout(config_layout)

        config_label2_text = ("<p style='white-space: pre-wrap; width: 100px;'>"
                              "Only change this if you have created or been provided with "
                              "specific config file/s.</p>")
        self.config_help_btn = QPushButton('?')
        self.config_help_btn.setFixedSize(25, 25)
        self.config_help_btn.setToolTip(config_label2_text)
        self.config_help_btn.setToolTipDuration(0)

        self.connection_manager.connect(self.config_help_btn.clicked,
                                        lambda: self.show_help_box(config_label2_text))
        self.config_help_btn.setStyleSheet(f"color: {combo_text_colour}; border: 1px solid {combo_text_colour};")
        self.config_help_btn.setWhatsThis(config_label2_text)
        config_box_layout.addWidget(self.config_help_btn)

        self.connection_manager.connect(self.config_combo.currentTextChanged, self.save_last_config)

        right_layout.addItem(spacer)

        sub_text2 = QLabel("To name the task/purpose of the images and to change the labelling subcategories, "
                           "please use 'Set Up' first.")
        sub_text2.setWordWrap(True)
        sub_text2.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sub_text2.setStyleSheet("font-size: 14px;")
        sub_text2.setAlignment(Qt.AlignmentFlag.AlignTop)

        right_layout.addStretch()

        hbox = QHBoxLayout()

        config_wizard_button = QPushButton("Set Up")
        self.connection_manager.connect(config_wizard_button.clicked, self.on_wizard_button_clicked)
        hbox.addWidget(config_wizard_button)

        ok_button = QPushButton("Annotate")
        self.connection_manager.connect(ok_button.clicked, self.accept)
        hbox.addWidget(ok_button)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        hbox.addItem(spacer)

        cancel_button = QPushButton("Cancel")
        self.connection_manager.connect(cancel_button.clicked, self.reject)
        hbox.addWidget(cancel_button)

        right_layout.addLayout(hbox)

        top_layout.addLayout(right_layout)
        top_layout.addLayout(left_layout)

        self.setLayout(top_layout)

        ok_button.setDefault(True)

    def on_wizard_button_clicked(self):
        """
        Open the configuration wizard when the Configuration Wizard button is clicked.
        """
        self.custom_return_code = 42
        self.accept()

    def exec(self) -> int:

        result = super().exec()
        try:
            return self.custom_return_code
        except AttributeError:
            if result == self.DialogCode.Accepted:
                return 1
            else:
                return 0

    def save_last_config(self, conf_name: str):
        self.settings.setValue("last_config_file", os.path.join(resource_dir, conf_name))

    def closeEvent(self, event: QCloseEvent):

        self.connection_manager.disconnect_all()
        event.accept()

    def show_help_box(self, message):
        QMessageBox.information(self, "Help", message)


class SetupWindow(QDialog):

    def __init__(self, settings: QSettings):

        super().__init__()

        self.settings = settings
        self.connection_manager = ConnectionManager()
        self.folder_label = QLabel()
        self.reference_folder_label = QLabel()
        self.json_label = QLabel()
        self.folder_label.setText(self.settings.value("image_path", ""))
        self.reference_folder_label.setText(self.settings.value("reference_path", ""))
        self.json_label.setText(self.settings.value("json_path", ""))
        self.folder_button = QPushButton("...")
        self.reference_folder_button = QPushButton("...")
        self.json_button = QPushButton("...")
        self.folder_button.setFixedSize(25, 25)
        self.reference_folder_button.setFixedSize(25, 25)
        self.json_button.setFixedSize(25, 25)
        self.new_json = False
        self.config = open_yml_file(self.settings.value("last_config_file", os.path.join(resource_dir, "config.yml")))

        self.setWindowTitle("PathologyUI Setup")

        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        expanding_spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        fixed_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()

        logo_layout = QHBoxLayout()

        info_layout = QVBoxLayout()
        general_info_label = QLabel("Begin Annotating...")
        general_info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        general_info_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        general_info_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_layout.addWidget(general_info_label)
        general_add_info_label = QLabel("Select to start a new save file (json) or load an existing one to continue "
                                        "previous progress...")
        general_add_info_label.setStyleSheet("font-size: 12px; font-style: italic;")
        general_add_info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        general_add_info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        info_layout.addWidget(general_add_info_label)
        logo_layout.addLayout(info_layout)

        logo_layout.addItem(spacer)

        path = os.path.join(resource_dir, 'assets/logo.png')
        logo = QPixmap(path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        icon_label = QLabel()
        icon_label.setPixmap(logo)
        logo_layout.addWidget(icon_label)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(logo_layout)

        layout.addItem(spacer)

        layout.addSpacerItem(expanding_spacer)

        self.new_json_tickbox = QCheckBox("Check to start from scratch (i.e. start a new JSON file)")
        self.new_json_tickbox.setStyleSheet("font-weight: bold;")
        self.new_json_tickbox.setObjectName("new_json")
        layout.addWidget(self.new_json_tickbox)

        layout.addSpacerItem(expanding_spacer)

        json_frame = QFrame()
        json_layout = QVBoxLayout()

        #
        load_json_title = QLabel("Load Progress:")
        load_json_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(load_json_title)

        json_info_label = QLabel("To load progress, please select an existing .json file:")
        json_info_label.setStyleSheet("font-weight: bold;")
        json_layout.addWidget(json_info_label)

        json_layout.addSpacerItem(fixed_spacer)

        json_selection_layout = QHBoxLayout()
        json_selection_layout.addWidget(QLabel("Selected JSON:"))
        json_selection_layout.addSpacerItem(expanding_spacer)
        json_selection_layout.addWidget(self.json_label)
        json_selection_layout.addWidget(self.json_button)

        try:
            help_colour = get_theme(self.settings.value('theme', 'light_red.xml'))['secondaryTextColor']
        except KeyError:
            help_colour = get_theme(self.settings.value('theme', 'light_red.xml'))['secondaryLightColor']

        json_explanation_text = ("<p style='white-space: pre-wrap; width: 100px;'>"
                                 "Progress is stored in a .json file. Please choose the file you wish to load.</p>")
        self.json_explanation_btn = QPushButton('?')
        self.json_explanation_btn.setFixedSize(25, 25)
        self.json_explanation_btn.setToolTip(json_explanation_text)
        self.json_explanation_btn.setToolTipDuration(0)

        self.connection_manager.connect(self.json_explanation_btn.clicked,
                                        lambda: self.show_help_box(json_explanation_text))

        self.json_button.setWhatsThis(json_explanation_text)
        self.json_explanation_btn.setStyleSheet(f"color: {help_colour}; border: 1px solid {help_colour};")
        json_selection_layout.addWidget(self.json_explanation_btn)

        json_layout.addLayout(json_selection_layout)

        json_frame.setLayout(json_layout)
        layout.addWidget(json_frame)

        layout.addItem(spacer)

        layout.addSpacerItem(expanding_spacer)

        #
        new_json_title = QLabel("Start from Scratch:")
        new_json_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(new_json_title)

        new_json_frame = QFrame()
        new_json_layout = QVBoxLayout()

        dcm_layout = QVBoxLayout()

        dcm_layout.addSpacerItem(fixed_spacer)

        im_selection_frame = QFrame()
        try:
            frame_color = get_theme(self.settings.value('theme', 'light_red.xml'))['secondaryLightColor']
        except KeyError:
            frame_color = get_theme(self.settings.value('theme', 'light_red.xml'))['secondaryColor']

        im_selection_frame.setObjectName("im_selection_frame")
        im_selection_frame.setStyleSheet(f"#im_selection_frame {{ border: 1px solid {frame_color}; }}")

        im_selection_layout = QVBoxLayout()
        dcm_selection_layout = QHBoxLayout()
        im_selection_label = QLabel("Images for Quality Assessment:")
        im_selection_label.setStyleSheet("font-weight: bold;")
        dcm_selection_layout.addWidget(im_selection_label)
        dcm_selection_layout.addSpacerItem(expanding_spacer)
        dcm_selection_layout.addWidget(self.folder_label)
        dcm_selection_layout.addWidget(self.folder_button)
        im_folder_explanation_text = ("<p style='white-space: pre-wrap; width: 100px;'>"
                                      "This folder should contain the images to be labelled.\n\n"
                                      "N.B. The images can be in subfolders.</p>")
        self.im_folder_explanation_btn = QPushButton('?')
        self.im_folder_explanation_btn.setFixedSize(25, 25)
        self.im_folder_explanation_btn.setToolTip(im_folder_explanation_text)
        self.im_folder_explanation_btn.setToolTipDuration(0)

        self.connection_manager.connect(self.im_folder_explanation_btn.clicked,
                                        lambda: self.show_help_box(im_folder_explanation_text))
        self.im_folder_explanation_btn.setStyleSheet(f"color: {help_colour}; border: 1px solid {help_colour};")
        self.folder_button.setWhatsThis(im_folder_explanation_text)
        dcm_selection_layout.addWidget(self.im_folder_explanation_btn)

        im_selection_layout.addLayout(dcm_selection_layout)

        delimiter_layout = QHBoxLayout()
        delimiter_label = QLabel("Image Filename Delimiter:")
        delimiter_label.setStyleSheet("font-weight: bold;")
        delimiter_layout.addWidget(delimiter_label)

        fixed_15_spacer = QSpacerItem(15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        delimiter_layout.addSpacerItem(fixed_15_spacer)
        self.delimiter_line_edit = QLineEdit()
        self.delimiter_line_edit.setFixedWidth(50)
        self.delimiter_line_edit.setText(self.settings.value("reference_delimiter", "__"))
        self.delimiter_line_edit.setObjectName("delimiter_line_edit")
        self.delimiter_line_edit.setStyleSheet(f"#delimiter_line_edit {{ color: white ; }}")
        delimiter_layout.addWidget(self.delimiter_line_edit)
        delimiter_layout.addSpacerItem(expanding_spacer)

        delimiter_explanation_text = ("<p style='white-space: pre-wrap; width: 100px;'>"
                                      "The delimiter distinguishes the image filename from the reference "
                                      "image filename.\n\nFor example, delimiter "
                                      "= '__' -> image filenames: image1__1.png', 'image1__2.png, etc and reference "
                                      "filename: 'image1.png'.\n\nIf no delimiter, leave blank. "
                                      "\n\nIf there is a mixture of "
                                      "with and without, enter the delimiter.</p>")
        self.delimiter_explanation_btn = QPushButton('?')
        self.delimiter_explanation_btn.setFixedSize(25, 25)
        self.delimiter_explanation_btn.setToolTip(delimiter_explanation_text)
        self.delimiter_explanation_btn.setToolTipDuration(0)

        self.connection_manager.connect(self.delimiter_explanation_btn.clicked,
                                        lambda: self.show_help_box(delimiter_explanation_text))
        self.delimiter_explanation_btn.setStyleSheet(f"color: {help_colour}; border: 1px solid {help_colour};")
        self.delimiter_line_edit.setWhatsThis(delimiter_explanation_text)
        delimiter_layout.addWidget(self.delimiter_explanation_btn)

        im_selection_layout.addLayout(delimiter_layout)
        im_selection_frame.setLayout(im_selection_layout)
        dcm_layout.addWidget(im_selection_frame)

        dcm_layout.addSpacerItem(fixed_spacer)

        ref_selection_frame = QFrame()
        ref_selection_frame.setObjectName("ref_selection_frame")
        ref_selection_frame.setStyleSheet(f"#ref_selection_frame {{ border: 1px solid {frame_color}; }}")

        ref_selection_layout = QVBoxLayout()
        reference_selection_layout = QHBoxLayout()
        ref_selection_label = QLabel("Reference Images:")
        ref_selection_label.setStyleSheet("font-weight: bold;")
        reference_selection_layout.addWidget(ref_selection_label)
        reference_selection_layout.addSpacerItem(expanding_spacer)
        reference_selection_layout.addWidget(self.reference_folder_label)
        reference_selection_layout.addWidget(self.reference_folder_button)

        ref_folder_explanation_text = ("<p style='white-space: pre-wrap; width: 100px;'>"
                                       "This folder should contain the reference images for comparison.</p>")
        self.ref_folder_explanation_btn = QPushButton('?')
        self.ref_folder_explanation_btn.setFixedSize(25, 25)
        self.ref_folder_explanation_btn.setToolTip(ref_folder_explanation_text)
        self.ref_folder_explanation_btn.setToolTipDuration(0)

        self.connection_manager.connect(self.ref_folder_explanation_btn.clicked,
                                        lambda: self.show_help_box(ref_folder_explanation_text))
        self.ref_folder_explanation_btn.setStyleSheet(f"color: {help_colour}; border: 1px solid {help_colour};")
        self.reference_folder_button.setWhatsThis(ref_folder_explanation_text)
        self.reference_folder_button.show()
        reference_selection_layout.addWidget(self.ref_folder_explanation_btn)

        ref_selection_layout.addLayout(reference_selection_layout)

        ref_selection_frame.setLayout(ref_selection_layout)
        dcm_layout.addWidget(ref_selection_frame)

        dcm_layout.addSpacerItem(fixed_spacer)

        new_json_layout.addLayout(dcm_layout)
        new_json_frame.setLayout(new_json_layout)
        layout.addWidget(new_json_frame)

        layout.addItem(spacer)

        layout.addSpacerItem(expanding_spacer)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        cancel_button = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Back")

        self.connection_manager.connect(self.button_box.accepted, self.on_accepted)
        self.connection_manager.connect(self.button_box.rejected, self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        if settings.value('json_path', "") == "":

            self.new_json_tickbox.setChecked(True)







        else:

            self.new_json_tickbox.setChecked(False)

        self.connection_manager.connect(self.json_button.clicked, self.select_json)
        self.connection_manager.connect(self.folder_button.clicked, self.select_image_folder)
        self.connection_manager.connect(self.reference_folder_button.clicked, self.select_reference_folder)
        self.connection_manager.connect(self.new_json_tickbox.stateChanged, self.on_json_checkbox_changed)
        self.connection_manager.connect(self.delimiter_line_edit.textChanged, self.on_delimiter_changed)

        self.load_saved_files(settings)

        QTimer.singleShot(0, self.on_json_checkbox_changed)

    def on_delimiter_changed(self):
        self.settings.setValue("reference_delimiter", self.delimiter_line_edit.text())

    def on_accepted(self):

        if not os.path.isdir(self.folder_label.text()) and self.new_json_tickbox.isChecked():
            print("No image folder selected", self.folder_label.text())
            print("No image folder selected", self.new_json_tickbox.isChecked())
            print(not os.path.isdir(self.folder_label.text()) and not self.new_json_tickbox.isChecked())
            self.generate_no_image_msg()
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return
        elif not os.path.isdir(self.reference_folder_label.text()) and self.new_json_tickbox.isChecked():
            self.generate_no_reference_image_msg()
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return
        elif self.new_json_tickbox.isChecked():
            super().accept()
        elif not self.check_json_compatibility(self.json_label.text()):

            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return
        else:
            super().accept()

    def accept(self):
        """
        Overwrite the default accept method to prevent the dialog from closing with an incompatible json.
        """
        pass

    def on_json_checkbox_changed(self):
        """
        When the new json checkbox is ticked, disable the json file dialog button and clear the json label.
        """
        if self.new_json_tickbox.isChecked():
            self.json_button.setEnabled(False)
            self.json_label.setText("")
            self.folder_label.setText(self.settings.value("image_path", ""))
            self.reference_folder_label.setText(self.settings.value("reference_path", ""))
            self.settings.setValue("new_json", True)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.folder_button.setEnabled(True)
            self.reference_folder_button.setEnabled(True)
            self.delimiter_line_edit.setEnabled(True)
            self.delimiter_line_edit.setText(self.settings.value("reference_delimiter", "__"))

            if not self.check_json_compatibility(self.json_label.text()):
                self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            else:
                self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

        else:
            self.json_label.setText(self.settings.value("json_path", ""))
            self.folder_label.setText("")
            self.reference_folder_label.setText("")
            self.settings.setValue("new_json", False)
            self.json_button.setEnabled(True)
            self.folder_button.setEnabled(False)
            self.reference_folder_button.setEnabled(False)
            self.delimiter_line_edit.setEnabled(False)

    def load_saved_files(self, settings: QSettings):
        """
        Load previously selected files from QSettings.

        :param settings: QSettings object
        :type settings: QSettings
        """

        json_path = settings.value("json_path", "")
        folder_path = settings.value("image_path", "")
        reference_folder_path = settings.value("reference_path", "")

        if json_path:
            self.json_label.setText(json_path)
        if folder_path:
            self.folder_label.setText(folder_path)
        if reference_folder_path:
            self.reference_folder_label.setText(reference_folder_path)

    @staticmethod
    def save_file_paths(settings: QSettings, json_path: str, folder_path: str, reference_folder_path: str):
        """
        Update QSettings

        :param settings: QSettings object to update
        :type settings: QSettings
        :param json_path: Path to JSON file
        :type json_path: str
        :param folder_path: Path to image folder
        :type folder_path: str
        """

        settings.setValue("json_path", json_path)
        settings.setValue("image_path", folder_path)
        settings.setValue("reference_path", reference_folder_path)

    def select_json(self):
        """
        Open file dialog to select JSON file.
        """

        json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")

        if json_path:
            self.json_label.setText(json_path)
            self.save_file_paths(self.settings, json_path, self.folder_label.text(), self.reference_folder_label.text())
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    def select_image_folder(self):
        """
        Open file dialog to select image folder. Only accept if directory contains an image file.
        """
        image_dir = None
        while image_dir is None:

            folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder", self.folder_label.text())

            if folder_path:
                img_files = find_relative_image_path(folder_path)
                if len(img_files) == 0:
                    error_msg_box = QMessageBox()
                    error_msg_box.setIcon(QMessageBox.Icon.Warning)
                    error_msg_box.setWindowTitle("Error")
                    error_msg_box.setText("The directory does not appear to contain any image files!")
                    error_msg_box.setInformativeText("Please try again.")
                    error_msg_box.exec()
                else:
                    self.folder_label.setText(folder_path)
                    self.save_file_paths(self.settings, self.json_label.text(), folder_path,
                                         self.reference_folder_label.text())
                    image_dir = folder_path
                    self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                    if not self.new_json_tickbox.isChecked():
                        self.check_json_compatibility(self.json_label.text())
            else:
                break

    def select_reference_folder(self):
        """
        Open file dialog to select image folder. Only accept if directory contains an image file.
        """
        image_dir = None
        while image_dir is None:

            folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder",
                                                           self.reference_folder_label.text())

            if folder_path:
                if os.path.isfile(folder_path):
                    folder_path = os.path.dirname(folder_path)
                img_files = [f for f in os.listdir(folder_path) if f.endswith((
                    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.dcm', '.dicom',
                ))]
                if len(img_files) == 0:
                    error_msg_box = QMessageBox()
                    error_msg_box.setIcon(QMessageBox.Icon.Warning)
                    error_msg_box.setWindowTitle("Error")
                    error_msg_box.setText("The directory does not appear to contain any image files!")
                    error_msg_box.setInformativeText("Please try again.")
                    error_msg_box.exec()
                else:
                    self.reference_folder_label.setText(folder_path)
                    self.save_file_paths(self.settings, self.json_label.text(), self.folder_label.text(), folder_path)
                    image_dir = folder_path
                    self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                    if not self.new_json_tickbox.isChecked():
                        self.check_json_compatibility(self.json_label.text())
            else:
                break

    def generate_json_tristate_incompatibility_msg(self):
        """
        Generate a message box to inform the user that the selected json file is incompatible with the config file
        due to the tristate checkbox setting.
        """
        QMessageBox.critical(self,
                             "Error",
                             f"JSON - CONFIG FILE CONFLICT!\n\n"
                             f"The selected json file has tri-state checkbox values (i.e. uncertain) which is incompatible "
                             f"with the config file selected.\n\n"
                             f"Please select a new json file or start again and select a new config file.",
                             QMessageBox.StandardButton.Ok,
                             defaultButton=QMessageBox.StandardButton.Ok)

    def generate_json_cbox_incompatibility_msg(self):
        """
        Generate a message box to inform the user that the selected json file is incompatible with the config file
        due to different checkbox names.
        """
        QMessageBox.critical(self,
                             "Error",
                             f"JSON - CONFIG FILE CONFLICT!\n\n"
                             f"The selected json file has checkbox name/s which are not in the config file.\n\n"
                             f"Please select a new json file or start again and select a new config file. ",
                             QMessageBox.StandardButton.Ok,
                             defaultButton=QMessageBox.StandardButton.Ok)

    def generate_json_rb_incompatibility_msg(self):
        """
        Generate a message box to inform the user that the selected json file is incompatible with the config file
        due to different checkbox names.
        """
        QMessageBox.critical(self,
                             "Error",
                             f"JSON - CONFIG FILE CONFLICT!\n\n"
                             f"The selected json file has radiobutton group/s which are not in the config file.\n\n"
                             f"Please select a new json file or start again and select a new config file. ",
                             QMessageBox.StandardButton.Ok,
                             defaultButton=QMessageBox.StandardButton.Ok)

    def generate_json_image_incompatibility_msg(self):
        """
        Generate a message box to inform the user that the selected json file is incompatible with the image folder
        as it contains image filenames which are not present in the folder.
        """
        QMessageBox.critical(self,
                             "Error",
                             f"JSON - IMAGE FOLDER CONFLICT!\n\n"
                             f"The selected json file has image files which are not present in the selected image "
                             f"directory.\n\n"
                             f"Please select a new json file or image directory. Alternatively, start again and select "
                             f"a new config file. ",
                             QMessageBox.StandardButton.Ok,
                             defaultButton=QMessageBox.StandardButton.Ok)

    def generate_no_image_msg(self):
        """
        Generate a message box to inform the user that no dcm folder is selected.
        """
        QMessageBox.critical(self,
                             "Error",
                             f"NO IMAGE DIRECTORY SELECTED!\n\n"
                             f"Please select an image directory or start again and select a new config file. ",
                             QMessageBox.StandardButton.Ok,
                             defaultButton=QMessageBox.StandardButton.Ok)

    def generate_no_reference_image_msg(self):
        """
        Generate a message box to inform the user that no dcm folder is selected.
        """
        QMessageBox.critical(self,
                             "Error",
                             f"NO REFERENCE IMAGE DIRECTORY SELECTED!\n\n"
                             f"Please select a reference image directory or start again and select a new config file. ",
                             QMessageBox.StandardButton.Ok,
                             defaultButton=QMessageBox.StandardButton.Ok)

    def check_config_json_compatibility(self, cboxes: List[str], cbox_values: List[int], rbs: [str]) -> bool:
        """
        Check if the selected json file is compatible with the config file.

        :param cboxes: list of checkbox names
        :type cboxes: list
        :param cbox_values: list of checkbox values
        :type cbox_values: list
        :param rbs: list of radiobutton group names
        :type rbs: list
        :return: True if compatible, False otherwise
        :rtype: bool
        """

        tristate = self.config.get('tristate_checkboxes', False)
        if not tristate:
            if 1 in cbox_values:
                self.generate_json_tristate_incompatibility_msg()
                return False

        for cbox in cboxes:
            if cbox not in self.config['checkboxes']:
                self.generate_json_cbox_incompatibility_msg()
                return False

        config_rb_names = [group['title'] for group in self.config['radiobuttons_page1']] + \
                          [group['title'] for group in self.config['radiobuttons_page2']]
        for rb in rbs:
            if rb not in config_rb_names:
                self.generate_json_rb_incompatibility_msg()
                return False

        return True

    def check_json_image_compatibility(self, filenames: List[str]) -> bool:
        """
        Check if the selected json file is compatible with the image folder.

        :param filenames: list of image filenames in the json file
        :type filenames: list
        :return: True if compatible, False otherwise
        :rtype: bool
        """
        if os.path.isdir(self.folder_label.text()):
            imgs = sorted([f for f in os.listdir(self.folder_label.text()) if f.endswith((
                '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.dcm', '.dicom',
            ))])

            for file in filenames:
                if file not in imgs:
                    self.generate_json_image_incompatibility_msg()
                    return False
            return True
        elif self.new_json_tickbox.isChecked():
            self.generate_no_image_msg()
            return False
        else:
            return True

    def check_json_compatibility(self, json_path: str) -> bool:
        """
        Check if the selected json file is compatible with the image files in the image directory and the selected
        config yml file. This prevents the program from crashing if incompatible files are selected.

        :param json_path: path to the json file
        :type json_path: str
        :return: True if compatible, False otherwise
        :rtype: bool
        """
        if os.path.isfile(json_path):
            filenames, cboxes, cbox_values, rbs = self.load_json_filenames_findings(json_path)
            dcm_compatible = self.check_json_image_compatibility(filenames)
            if dcm_compatible:
                config_compatible = self.check_config_json_compatibility(cboxes, cbox_values, rbs)
                if config_compatible:
                    self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                    return True
        elif self.new_json_tickbox.isChecked():
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            return True
        else:
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return False

    def closeEvent(self, event: QCloseEvent):
        """
        Handles a close event and disconnects connections between signals and slots.

        :param event: close event
        :type event: QCloseEvent
        """
        self.connection_manager.disconnect_all()
        event.accept()

    def load_json_filenames_findings(self, json_path: str):
        """
        Load the filenames and findings from a json file.

        :param json_path: path to the json file
        :type json_path: str
        """

        with open(json_path, 'r') as file:
            data = json.load(file)

        filenames = [entry['filename'] for entry in data['files']]
        self.folder_label.setText(self.settings.value(data['image_directory'], self.folder_label.text()))
        self.reference_folder_label.setText(
            self.settings.value(data['reference_image_directory'], self.reference_folder_label.text())
        )
        cboxes = [cbox for entry in data['files'] if 'checkboxes' in entry for cbox in entry['checkboxes'].keys()]
        cbox_values = [value for entry in data['files'] if 'checkboxes' in entry for value in
                       entry['checkboxes'].values()]
        radiobs = [rb for entry in data['files'] if 'radiobuttons' in entry for rb in entry['radiobuttons'].keys()]

        unique_cboxes = sorted(list(set(cboxes)))
        unique_cbox_values = sorted(list(set(cbox_values)))
        unique_radiobs = sorted(list(set(radiobs)))

        return filenames, unique_cboxes, unique_cbox_values, unique_radiobs

    def show_help_box(self, message):
        QMessageBox.information(self, "Help", message)


class FileSelectionDialog(QDialog):
    """
    Dialog for selecting a file from a list of files.

    :param file_list: list of files
    :type file_list: List[str]
    :param parent: parent widget
    :type parent: Optional[QWidget]
    """

    def __init__(self, file_list: List[str], parent: Optional[QWidget] = None):
        """
        Initialize the dialog.

        :param file_list: list of files
        :type file_list: List[str]
        :param parent: parent widget
        :type parent: Optional[QWidget]
        """
        super().__init__(parent)
        self.setWindowTitle("Select Image")

        self.file_list = file_list
        self.filtered_list = file_list

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.search_bar = QLineEdit()
        self.connection_manager = ConnectionManager()
        self.connection_manager.connect(self.search_bar.textChanged, self.filter_list)
        self.layout.addWidget(self.search_bar)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.file_list)
        self.connection_manager.connect(self.list_widget.itemClicked, self.select_file)
        self.connection_manager.connect(self.list_widget.itemDoubleClicked, self.select_and_accept_file)
        self.layout.addWidget(self.list_widget)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.connection_manager.connect(self.buttonBox.accepted, self.accept_file)
        self.connection_manager.connect(self.buttonBox.rejected, self.reject)
        self.layout.addWidget(self.buttonBox)

        self.selected_file = None
        self.adjust_size()

    def adjust_size(self):
        """
        Adjust the size of the dialog to fit the list of files.
        """
        max_width = 0
        fm = QFontMetrics(self.font())
        for file in self.file_list:
            width = fm.horizontalAdvance(file)
            if width > max_width:
                max_width = width

        max_width += 50
        height = 500
        self.resize(max_width, height)

    def filter_list(self, query):
        """
        Filter the list of files based on a query.

        :param query: query to filter the list of files
        :type query: str
        """
        self.filtered_list = [file for file in self.file_list if query.lower() in file.lower()]
        self.list_widget.clear()
        self.list_widget.addItems(self.filtered_list)

    def select_file(self, item):
        """
        Select a file from the list of files.

        :param item: item to select
        :type item: QListWidgetItem
        """
        self.selected_file = item.text()
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    def select_and_accept_file(self, item):
        """
        Select a file from the list of files and accept the dialog.

        :param item: item to select
        :type item: QListWidgetItem
        """
        self.selected_file = item.text()
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        self.accept_file()

    def accept_file(self):
        """
        Accept the dialog if a file is selected, otherwise reject it.
        """
        if self.selected_file is not None:
            self.accept()
        else:
            self.reject()
