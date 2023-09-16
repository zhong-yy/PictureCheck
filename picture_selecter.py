import os
import typing
import pandas as pd
import numpy as np
import shutil
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFileDialog,
    QLabel,
    QPushButton,
    QMessageBox,
    QGraphicsScene,
    QMenu,
    QGraphicsPixmapItem,
    QAction,
    QGraphicsView,
)
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF
from pathlib import Path
from functools import partial
import sys


class MyGUI(QMainWindow):
    def __init__(
        self,
        ui_path: str | Path,
    ) -> None:
        super(MyGUI, self).__init__()
        # self.win = uic.loadUi(ui_path)
        uic.loadUi(str(ui_path), self)
        self.setWindowTitle("Picture Selecter")

        # self.btn_start.clicked.connect(self.start_working)
        self.btn_pass.clicked.connect(self.reject_figure)
        self.btn_OK.clicked.connect(self.select_figure)
        self.btn_next.clicked.connect(self.next_figure)
        self.btn_previous.clicked.connect(self.previouse_figure)

        self.actionInput_folder.triggered.connect(self.set_input_folder)
        self.actionOutput_folder.triggered.connect(self.set_output_folder)

        self.input_line.returnPressed.connect(self.input_line_enter)
        self.output_line.returnPressed.connect(self.output_line_enter)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self._input_folder = Path("")
        self._output_folder = Path("")
        self.only_selected_figures = self.only_selected_check_box.isChecked()
        self.only_selected_check_box.toggled.connect(self.only_selected_figures_toggle)

        self.current_id = None
        self.n_selected = 0
        self.figures = []
        self.setWindowState(Qt.WindowMaximized)
        self.graphicsView.wheelEvent = self.zoom
        self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.show()
        self.resizeEvent(None)

    @property
    def input_folder(self):
        return self._input_folder

    @input_folder.setter
    def input_folder(self, folder_path):
        if (folder_path / "figure_list.csv").is_file():
            df = pd.read_csv(folder_path / "figure_list.csv")
            if len(df) > 0:
                self.figures = df.to_dict("records")

                figures_to_check = df[~df["checked"]]
                if len(figures_to_check) > 0:
                    self.current_id = figures_to_check.index[0]
                else:
                    self.current_id = len(self.figures)
                self._input_folder = folder_path
                self.n_selected = sum([x["decision"] for x in self.figures])
                self.start_working()
        else:
            fig_names = [x.name for x in folder_path.glob(f"*.jpg")] + [
                x.name for x in folder_path.glob(f"*.png")
            ]
            fig_names.sort()
            if len(fig_names) == 0:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"No picures in {folder_path}",
                    QMessageBox.Ok,
                )
            else:
                status = np.zeros(len(fig_names), dtype=bool)
                selected = np.zeros(len(fig_names), dtype=bool)
                df = pd.DataFrame(
                    data={
                        "figure_name": fig_names,
                        "checked": status,
                        "decision": selected,
                    }
                )
                df.to_csv(folder_path / "figure_list.csv", index=False)
                self.figures = df.to_dict("records")
                self.current_id = 0
                self.n_selected = 0
                self._input_folder = folder_path
                self.start_working()

    @property
    def output_folder(self):
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        self._output_folder = value

    def load_figure(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                self.scene.removeItem(item)
        if self.current_id < len(self.figures):
            picture = self.input_folder / self.figures[self.current_id]["figure_name"]

            self.img = QImage(str(picture))

            # img = QPixmap(str(picture))

            # scale_img = img.scaled(
            #     self.graphicsView.size(),
            #     Qt.KeepAspectRatio,
            #     Qt.SmoothTransformation,
            # )
            pic = QGraphicsPixmapItem()
            # pic.setPixmap(scale_img)
            pic.setPixmap(QPixmap.fromImage(self.img))
            self.scene.addItem(pic)
            # self.scene.addPixmap(scale_img)
            self.graphicsView.setScene(self.scene)
            self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.update_status_bar()

        else:
            QMessageBox().information(
                None,
                "No more figures",
                f"""You have gone through all figures.""",
                QMessageBox.Ok,
            )
            self.statusBar().showMessage("")
            df = pd.DataFrame(data=self.figures)
            df.to_csv(self.input_folder / "figure_list.csv", index=False)

    def update_status_bar(self):
        status_msg = (
            f"""Figure {self.current_id}: {self.figures[self.current_id]["figure_name"]}.      """
            f"""Has it been checked before? {self.figures[self.current_id]["checked"]}.      """
        )
        if self.figures[self.current_id]["checked"]:
            status_msg += (
                f"""Decision status: {self.figures[self.current_id]["decision"]}"""
            )
        status_msg += f"      {self.n_selected} selected"
        self.statusBar().showMessage(status_msg)

    def only_selected_figures_toggle(self):
        self.only_selected_figures = self.only_selected_check_box.isChecked()

    def start_working(self):
        if self.current_id < len(self.figures):
            self.load_figure()
        else:
            restart_btn = QMessageBox.question(
                self,
                "No more figures",
                "Do you want to check the figures again?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if restart_btn == QMessageBox.Yes:
                self.current_id = 0
                self.load_figure()

    def check_input_folder(self):
        if self.current_id is None:
            QMessageBox().information(
                None,
                "No input folder selected",
                f"""You need to select a folder containing pictures.""",
                QMessageBox.Ok,
            )
            return False
        else:
            return True

    def check_output_folder(self):
        if self.output_folder.name == "":
            self.output_folder = self.input_folder / "selected_figures"
            self.output_folder.mkdir(parents=True, exist_ok=True)
            self.output_line.setText(str(self.output_folder))

    def reject_figure(self):
        if not self.check_input_folder():
            return
        if self.current_id < len(self.figures):
            self.figures[self.current_id]["checked"] = True
            if self.figures[self.current_id]["decision"] == True:
                self.n_selected = self.n_selected - 1
                self.figures[self.current_id]["decision"] = False
            self.check_output_folder()
            if (
                self.output_folder / self.figures[self.current_id]["figure_name"]
            ).is_file():
                (
                    self.output_folder / self.figures[self.current_id]["figure_name"]
                ).unlink()
            if not self.only_selected_figures:
                self.current_id = self.current_id + 1
                self.load_figure()
            else:
                n_selected = sum([x["decision"] for x in self.figures])
                if n_selected == 0:
                    QMessageBox().warning(
                        None,
                        "No figures",
                        f"""Cannot load the next selected figure, because no figures have been selected.""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                else:
                    while True:
                        self.current_id = self.current_id + 1
                        if self.current_id >= len(self.figures):
                            self.current_id = self.current_id - len(self.figures)
                        if self.figures[self.current_id]["decision"] == True:
                            self.load_figure()
                            break
                    # self.current_id = self.current_id + 1
                    # self.load_figure()

    def select_figure(self):
        if not self.check_input_folder():
            return
        if self.current_id < len(self.figures):
            self.figures[self.current_id]["checked"] = True
            if self.figures[self.current_id]["decision"] == False:
                self.n_selected = self.n_selected + 1
                self.figures[self.current_id]["decision"] = True
            self.check_output_folder()
            shutil.copy2(
                self.input_folder / self.figures[self.current_id]["figure_name"],
                self.output_folder / self.figures[self.current_id]["figure_name"],
            )
            if not self.only_selected_figures:
                self.current_id = self.current_id + 1
                self.load_figure()
            else:
                n_selected = sum([x["decision"] for x in self.figures])
                if n_selected == 0:
                    QMessageBox().warning(
                        None,
                        "No figures",
                        f"""Cannot load the next selected figure, because no figures have been selected.""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                elif (
                    n_selected == 1
                    and self.figures[self.current_id]["decision"] == True
                ):
                    QMessageBox().information(
                        None,
                        "No figures",
                        f"""Cannot load the next selected figure, because this is the only selected figure.""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                else:
                    while True:
                        self.current_id = self.current_id + 1
                        if self.current_id >= len(self.figures):
                            self.current_id = self.current_id - len(self.figures)
                        if self.figures[self.current_id]["decision"] == True:
                            self.load_figure()
                            break

    def next_figure(self):
        if not self.check_input_folder():
            return
        if self.current_id < len(self.figures):
            if not self.only_selected_figures:
                self.current_id = self.current_id + 1
                if self.current_id >= len(self.figures):
                    self.current_id = self.current_id - len(self.figures)
                self.load_figure()
            else:
                # n_selected = sum([x["decision"] for x in self.figures])
                if self.n_selected == 0:
                    QMessageBox().warning(
                        None,
                        "No figures",
                        f"""No figures have been selected""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                elif (
                    self.n_selected == 1
                    and self.figures[self.current_id]["decision"] == True
                ):
                    QMessageBox().information(
                        None,
                        "No figures",
                        f"""Cannot load the next selected figure, because this is the only selected figure.""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                else:
                    while True:
                        self.current_id = self.current_id + 1
                        if self.current_id >= len(self.figures):
                            self.current_id = self.current_id - len(self.figures)
                        if self.figures[self.current_id]["decision"] == True:
                            self.load_figure()
                            break

    def previouse_figure(self):
        if not self.check_input_folder():
            return
        if self.current_id < len(self.figures):
            if not self.only_selected_figures:
                self.current_id = self.current_id - 1
                if self.current_id < 0:
                    self.current_id = self.current_id + len(self.figures)
                self.load_figure()
            else:
                # n_selected = sum([x["decision"] for x in self.figures])
                if self.n_selected == 0:
                    QMessageBox().information(
                        None,
                        "No figures",
                        f"""No figures have been selected""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                elif (
                    self.n_selected == 1
                    and self.figures[self.current_id]["decision"] == True
                ):
                    QMessageBox().information(
                        None,
                        "No figures",
                        f"""Cannot load the next selected figure, because this is the only selected figure.""",
                        QMessageBox.Ok,
                    )
                    self.update_status_bar()
                else:
                    while True:
                        self.current_id = self.current_id - 1
                        if self.current_id < 0:
                            self.current_id = self.current_id + len(self.figures)
                        if self.figures[self.current_id]["decision"] == True:
                            self.load_figure()
                            break

    def select_folder(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(dialog.FileMode.DirectoryOnly)
        folder_path = dialog.getExistingDirectory()
        return folder_path

    def set_input_folder(self):
        folder_path = self.select_folder()
        if folder_path:
            self.input_folder = Path(folder_path)
            self.input_line.setText(str(self.input_folder))
            self.output_folder = Path()
            self.output_line.setText("")

    def set_output_folder(self):
        folder_path = self.select_folder()
        if folder_path:
            self.output_folder = Path(folder_path)
            self.output_line.setText(str(self.output_folder))

    def input_line_enter(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirmation Dialog")
        dlg.setText("Do you want to change the input folder?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg_answer_button = dlg.exec()

        if dlg_answer_button == QMessageBox.Yes:
            if Path(self.input_line.text()).is_dir():
                self.input_folder = Path(self.input_line.text())
            else:
                QMessageBox().information(
                    None,
                    "Folder not exists",
                    f"""Folder "{self.input_line.text()}" does not exists.""",
                    QMessageBox.Ok,
                )
        else:
            self.input_line.setText(str(self.input_folder))

    def output_line_enter(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirmation Dialog")
        dlg.setText("Do you want to change the output folder?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg_answer_button = dlg.exec()

        if dlg_answer_button == QMessageBox.Yes:
            if Path(self.output_line.text()).is_dir():
                self.output_folder = Path(self.output_line.text())
            else:
                create_btn = QMessageBox().question(
                    None,
                    "Folder not exists",
                    f"""Folder "{self.output_line.text()}" does not exists. Do you want to create it?""",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if create_btn == QMessageBox.Yes:
                    self.output_folder = Path(self.output_line.text())
                    self.output_folder.mkdir(parents=True, exist_ok=True)
                else:
                    self.output_line.setText(str(self.output_folder))
        else:
            self.output_line.setText(str(self.output_folder))

    def resizeEvent(self, event):
        if self.scene:
            self.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        # rect = QRectF(self.pixmap_item.pixmap().rect())
        # self.graphicsView.setSceneRect(rect)
        # self.graphicsView.fitInView(rect, Qt.KeepAspectRatio)
        if event:
            super().resizeEvent(event)

    def closeEvent(self, event):
        exit_query = QMessageBox.question(
            self,
            "Close window",
            "Do you wan to exit",
            QMessageBox.Yes | QMessageBox.No,
        )
        if exit_query == QMessageBox.Yes:
            if len(self.figures) > 0:
                df = pd.DataFrame(data=self.figures)
                df.to_csv(self.input_folder / "figure_list.csv", index=False)
            event.accept()
        else:
            event.ignore()

    def zoom(self, event):
        # Zoom in/out
        zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.graphicsView.scale(zoom_factor, zoom_factor)


if __name__ == "__main__":
    pwd = Path(__file__).parent
    app = QApplication(sys.argv)
    mygui = MyGUI(pwd / "UI" / "mainwindow.ui")
    mygui.show()
    app.exec_()
