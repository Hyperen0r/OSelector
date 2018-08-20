#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import xml.etree.ElementTree as ET

from enum import Enum
from util.utils import indent, create_dir
from util.Config import get_config, save_config
from data.Animation import Animation
from data.NamedContainer import NamedContainer
from widget.QuickyGui import *
from widget.MainWindow import MainWindow
from widget.AnimTreeWidget import AnimTreeWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMessageBox, QFileDialog, QInputDialog, QHBoxLayout, QVBoxLayout)


# TODO Remove comment from line containing an animation
# TODO Handle unique file
# TODO Handle merge plugin ?


class COLOR(Enum):
    NORMAL = Qt.black
    DUPLICATE = Qt.red


class OSelectorWindow(MainWindow):

    def __init__(self):
        super().__init__("OSelector Tool")

        self.init_settings()

    def init_ui(self):
        # ----- FIRST ROW : Scanning for animations files -----
        self.groupBoxScanning = create_group_box("STEP I - Scan")
        self.buttonScan = create_button(self, "Scan for animations", self.scan_folder)
        self.buttonLoad = create_button(self, "Load plugin", self.load_xml)
        label_anims_found = create_label("Animations found : ")
        self.lcdAnimsFound = create_lcd(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonScan)
        hbox.addWidget(self.buttonLoad)
        hbox.addStretch(1)
        hbox.addWidget(label_anims_found)
        hbox.addWidget(self.lcdAnimsFound)

        self.groupBoxScanning.setLayout(hbox)
        self.mainLayout.addWidget(self.groupBoxScanning)

        # ----- SECOND ROW : List animations files -----
        self.groupBoxAnim = create_group_box("STEP II - Select")
        self.treeAnimFiles = AnimTreeWidget()

        vbox = QVBoxLayout()
        vbox.addWidget(self.treeAnimFiles)

        hbox = QHBoxLayout()
        hbox.addWidget(create_button(self, "Check All", self.treeAnimFiles.check_all))
        hbox.addWidget(create_button(self, "Uncheck All", self.treeAnimFiles.action_uncheck_all))
        hbox.addWidget(create_button(self, "Clean Up", self.treeAnimFiles.cleanup))

        vbox.addItem(hbox)

        self.groupBoxAnim.setLayout(vbox)
        self.mainLayout.addWidget(self.groupBoxAnim)

        # ----- THIRD ROW : Generate plugin -----
        self.groupBoxGenerate = create_group_box("STEP III - Generate")
        self.buttonGenerate = create_button(self, "Generate Plugin", self.generate_plugin)
        label_anims_checked = create_label("Animations checked : ")
        self.lcdAnimsChecked = create_lcd(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonGenerate)
        hbox.addStretch(1)
        hbox.addWidget(label_anims_checked)
        hbox.addWidget(self.lcdAnimsChecked)

        self.groupBoxGenerate.setLayout(hbox)
        self.mainLayout.addWidget(self.groupBoxGenerate)

    def init_settings(self):
        if get_config().getboolean("CONFIG", "bFirstTime"):

            answer = question(self, 'Initialization', "Do you use MO ?")

            if answer == QMessageBox.Yes:
                QMessageBox.information(self, "Instructions for MO users",
                                        "Next dialog window will ask you where your Mod Organiser mods/ folder is, "
                                        "thus allowing to install the plugin directly. "
                                        "You will still need to activate it in Mod Organizer left pane. "
                                        "If you don't see the mod, refresh the left pane. ")
                get_config().set("CONFIG", "bUseModOrganizer", "True")
            else:
                QMessageBox.information(self, "Instructions for Non-MO users",
                                        "Next dialog window will ask you to specify a folder to store the plugin. "
                                        "In order to install it with a mod manager, compress the generated folder "
                                        "(Unless you specified skyrim/data folder ")
                get_config().set("CONFIG", "bUseModOrganizer", "False")

            folder = QFileDialog.getExistingDirectory(self, 'Mod folder location', '', QFileDialog.ShowDirsOnly)

            if folder:
                get_config().set("PATHS", "installFolder", str(folder))

            get_config().set("CONFIG", "bFirstTime", "False")
            save_config()

    def toggle_window(self, state):
        self.groupBoxGenerate.setDisabled(not state)
        self.groupBoxAnim.setDisabled(not state)
        self.groupBoxScanning.setDisabled(not state)

    def load_xml(self):
        self.toggle_window(False)

        xml_file, filter = QFileDialog.getOpenFileName(self, "Open file",
                                               get_config().get("PATHS", "installFolder") + "/" +
                                               get_config().get("PLUGIN", "name") + "/" +
                                               get_config().get("PATHS", "pluginFolder"),
                                               "MyOsa file (*.myo)")

        found = 0
        if xml_file:
            logging.info("xml_file given : " + xml_file)
            logging.info("Loading")

            found = self.treeAnimFiles.create_from_xml(xml_file)

        self.treeAnimFiles.itemClicked.connect(self.slot_lcd_display_anim_checked)
        self.slot_lcd_display_anim_checked()
        self.lcdAnimsFound.display(found)

        self.toggle_window(True)

    def scan_folder(self):

        self.toggle_window(False)

        scan_dir = QFileDialog.getExistingDirectory(self, 'Mod folder location',
                                                    get_config().get("PATHS", "installFolder"),
                                                    QFileDialog.ShowDirsOnly)

        packages = []
        previous_package = ""
        anim_package = None
        counter = 0
        max_item_string_length = get_config().getint("PLUGIN", "maxItemStringLength")

        if scan_dir:

            logging.info("=============== SCANNING ===============")
            logging.info("Scanning directory : " + scan_dir)

            for root, dirs, files in os.walk(scan_dir):
                for file in files:
                    if file.startswith("FNIS") and file.endswith("List.txt"):
                        anim_file = os.path.join(root, file)
                        module = file[5:-9]
                        package = anim_file.replace(scan_dir + '\\', '').split('\\', 1)[0][slice(0, max_item_string_length)]
                        if not package:
                            package = module

                        if package != previous_package:
                            if anim_package:
                                anim_package.items.sort(key=lambda x: x.name, reverse=False)
                            anim_package = NamedContainer(package)
                        anim_module = NamedContainer(module)

                        logging.info(indent("Package : " + str(package), 1))
                        logging.info(indent("Module  : " + str(module), 1))
                        logging.info(indent("Reading : " + anim_file, 1))

                        with open(anim_file, 'r') as f:
                            anim = None
                            for line in f:
                                anim_type, anim_options, anim_id, anim_file, anim_obj = Animation.parse_line(line)

                                logging.debug(indent("animType : " + anim_type.name + " || Line : " + line.strip(), 2))

                                if anim_type == Animation.TYPE.BASIC:
                                    anim = Animation(anim_package.name, anim_module.name, anim_type, anim_options, anim_id, anim_file, anim_obj)
                                    anim_module.add_item(anim)
                                    counter += 1
                                    logging.info(indent("Adding basic animation || Line : " + line.strip(), 2))

                                elif anim_type == Animation.TYPE.ANIM_OBJ:
                                    anim = Animation(anim_package.name, anim_module.name, anim_type, anim_options, anim_id, anim_file, anim_obj)
                                    anim_module.add_item(anim)
                                    counter += 1
                                    logging.info(indent("Adding AnimObj animation || Line : " + line.strip(), 2))

                                elif anim_type == Animation.TYPE.SEQUENCE:
                                    anim = Animation(anim_package.name, anim_module.name, anim_type, anim_options, anim_id, anim_file, anim_obj)
                                    anim_module.add_item(anim)
                                    counter += 1
                                    logging.info(indent("Adding sequence animation || Line : " + line.strip(), 2))

                                elif anim_type == Animation.TYPE.ADDITIVE:
                                    anim.add_stage(anim_id, anim_file, anim_obj)
                                    counter += 1
                                    logging.info(indent("Adding stage || Line : " + line.strip(), 3))

                        #anim_module.items.sort(key=lambda x: x.parse_name(), reverse=False)

                        if anim_module.items:
                            anim_package.add_item(anim_module)
                            if package != previous_package:
                                previous_package = package
                                packages.append(anim_package)

            packages.sort(key=lambda x: x.name, reverse=False)
            duplicate = self.treeAnimFiles.create_from_packages(packages)
            QMessageBox.information(self, "Results", str(duplicate) + " duplicates found (Not added)\n"
                                                                  "List (WARNING Level) available in logs (if activated)")
            self.treeAnimFiles.cleanup()
            self.treeAnimFiles.itemClicked.connect(self.slot_lcd_display_anim_checked)
            self.slot_lcd_display_anim_checked()
            self.lcdAnimsFound.display(counter)

        self.toggle_window(True)

    def slot_lcd_display_anim_checked(self):
        self.lcdAnimsChecked.display(self.treeAnimFiles.animation_count())

    def generate_plugin(self):
        logging.info("=============== GENERATING PLUGIN ===============")

        plugin_name, ok = QInputDialog.getText(self, "Plugin Name", "Enter the plugin name", text=get_config().get("PLUGIN", "name"))

        if ok:
            if plugin_name:

                path_plugin_folder = get_config().get("PATHS", "installFolder") + "/" + \
                                     plugin_name + "/" + \
                                     get_config().get("PATHS", "pluginFolder")

                """
                path_plugin_install = get_config().get("PATHS", "installFolder") + "/" + \
                                      plugin_name + "/" + \
                                      get_config().get("PATHS", "pluginInstall")
                create_dir(path_plugin_install)
                
                # File allowing the plugin to be recognized by OSA
                file = open(path_plugin_install + "/" + get_config().get("PLUGIN", "osplug") + ".osplug", "w")
                file.close()
                """

                create_dir(path_plugin_folder)

                logging.info("Plugin destination : " + path_plugin_folder)

                xml_root = self.treeAnimFiles.to_xml(plugin_name)

                with open(path_plugin_folder + plugin_name + ".myo", "w") as file:
                    data = ET.tostring(xml_root, "unicode")
                    file.write(data)

                QMessageBox.information(self, "Results",
                                        "Plugin Generation Done !\n"
                                        "----- Plugin path -----\n" +
                                        path_plugin_folder)
            else:
                QMessageBox.warning(self, "Abort", "Enter valid name")


if __name__ == '__main__':
    logging.basicConfig(filemode="w",
                        filename="logs.log",
                        level=logging.getLevelName(get_config().get("LOG", "level")),
                        format='%(asctime)s - [%(levelname)s] - %(name)s : %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    if not get_config().get("LOG", "enabled"):
        logger = logging.getLogger()
        logger.disabled = True

    logging.info(" =============== STARTING LOGGING ===============")

    app = QApplication(sys.argv)
    window = OSelectorWindow()
    sys.exit(app.exec_())
