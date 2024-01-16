import sys
import os
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qt_material import apply_stylesheet

from main_app import MainApp
from unified_wizard import ConfigurationWizard
from windows import LoadMessageBox, SetupWindow

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


def main(theme='qt_material', material_theme=None, icon_theme='qtawesome'):

    def cleanup():
        """
        Cleanup function. Closes and deletes all windows and widgets.
        """

        try:

            load_msg_box.close()
            load_msg_box.deleteLater()
        except NameError:
            pass

        try:

            window.close()
            window.deleteLater()
        except NameError:
            pass

        try:

            setup_window.close()
            setup_window.deleteLater()
        except NameError:
            pass

        try:

            wizard.close()
            wizard.deleteLater()
        except NameError:
            pass
        return

    app = QApplication(sys.argv)

    settings = QSettings('PathologyUI', 'ImageViewer')

    if theme == 'qt_material':
        if material_theme is None:
            material_theme = settings.value('theme', 'dark_blue.xml')
        else:
            settings.setValue('theme', material_theme)
        apply_stylesheet(app, theme=material_theme, extra={})
    else:
        app.setStyle(QStyleFactory.create(theme))

    QIcon.setThemeName(icon_theme)

    while True:

        load_msg_box = LoadMessageBox()
        result = load_msg_box.exec()
        config_filename = load_msg_box.config_combo.currentText()

        load_msg_box.save_last_config(config_filename)

        if result == load_msg_box.DialogCode.Accepted:

            setup_window = SetupWindow(settings)
            result = setup_window.exec()

            if result == setup_window.DialogCode.Accepted:

                window = MainApp(app, settings)
                if not window.should_quit:
                    window.show()
                    break
                else:
                    cleanup()
                    sys.exit()
            else:
                continue


        elif result == load_msg_box.DialogCode.Rejected:
            cleanup()
            sys.exit()


        else:
            if hasattr(sys, '_MEIPASS'):

                resource_dir = sys._MEIPASS
            elif 'main.py' in os.listdir(os.path.dirname(os.path.abspath("__main__"))):

                resource_dir = os.path.dirname(os.path.abspath("__main__"))
            else:
                resource_dir = os.path.join(os.path.dirname(os.path.abspath("__main__")), 'PathologyUI')
            wizard = ConfigurationWizard(os.path.join(resource_dir, config_filename))
            result = wizard.exec()
            if result == 1:
                continue

            else:
                cleanup()
                sys.exit()

    exit_code = app.exec()
    cleanup()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
