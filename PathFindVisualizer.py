from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QGridLayout,
    QPlainTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QRadioButton,
    QLineEdit,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from collections import deque
from PyQt6 import QtTest

import heapq
from collections import namedtuple
from typing import List
import re

Point = namedtuple("Point", "x y")


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_params = {
            "black": "background-color: rgb(0, 0, 0);",
            "white": "background-color: rgb(255, 255, 255);",
            "red": "background-color: rgb(255, 0, 0);",
            "green": "background-color: rgb(0, 255, 0);",
            "blue": "background-color: rgb(0, 0, 255);",
            "cyan": "background-color: rgb(0, 255, 255);",
            "yellow": "background-color: rgb(255, 255, 0);",
            "purple": "background-color: rgb(255, 0, 255);",
        }
        for key in self.cell_params:
            self.cell_params[key] += " font-size: 24pt; font-family: Times New Roman;"

        self.setWindowTitle("PathVisualizer")
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.cells = {}
        self.rows = 5
        self.cols = 5
        self.def_val = 1
        self.blocked_cell = "bc"
        self.max_val = float("inf")
        self.grid_widget = None
        self.moves = [Point(0, -1), Point(0, 1), Point(-1, 0), Point(1, 0)]
        self.time_delay_ms = 100

        self.create_grid(self.rows, self.cols, str(self.def_val))

        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        self.menu_widget.setLayout(menu_layout)
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.create_grid_button = QPushButton("Create grid")
        self.create_grid_button.clicked.connect(slot=self.create_grid_from_inputs)

        rows_label = QLabel("rows")
        cols_label = QLabel("cols")
        def_val_label = QLabel("default value")
        grid_info_label = QLabel(
            "\n1. Rows, cols: int > 0: \n"
            "2. default value: int/float >=0 \n or bc-blocked cell \n"
        )
        cell_info_label = QLabel(
            "\n\nCell values can be: \n"
            "1. a non-negative float \n"
            "2. bc - blocked cell"
        )
        start_info_label = QLabel("\nstart pos: bottom-left\n" "end pos: top-right\n")
        self.n_rows = QLineEdit(str(self.rows))
        self.n_cols = QLineEdit(str(self.cols))
        self.def_val = QLineEdit(str(self.def_val))

        menu_layout.addWidget(self.create_grid_button)
        menu_layout.addWidget(grid_info_label)
        menu_layout.addWidget(rows_label)
        menu_layout.addWidget(self.n_rows)
        menu_layout.addWidget(cols_label)
        menu_layout.addWidget(self.n_cols)
        menu_layout.addWidget(def_val_label)
        menu_layout.addWidget(self.def_val)

        self.bfs_radio_button = QRadioButton("breadth first search", self)
        self.dfs_radio_button = QRadioButton("depth first search", self)
        self.dijkstra_radio_button = QRadioButton("dijkstra search", self)
        self.a_star_radio_button = QRadioButton("A star search", self)

        self.bfs_radio_button.setChecked(True)
        self.start_search = QPushButton("search path")
        self.start_search.clicked.connect(self.search_path)
        menu_layout.addWidget(self.start_search)
        menu_layout.addWidget(self.bfs_radio_button)
        menu_layout.addWidget(self.dfs_radio_button)
        menu_layout.addWidget(self.dijkstra_radio_button)
        menu_layout.addWidget(self.a_star_radio_button)
        menu_layout.addWidget(cell_info_label)
        menu_layout.addWidget(start_info_label)
        self.main_layout.addWidget(self.menu_widget)
        self.main_layout.addWidget(self.grid_widget)
        self.show()

    @staticmethod
    def is_number(s: str):
        pattern = r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
        return re.match(pattern, s) is not None

    @staticmethod
    def is_positive_integer(s: str) -> bool:
        return s.isdigit()

    def create_grid_from_inputs(self):
        rows_s = self.n_rows.text()
        cols_s = self.n_cols.text()
        def_val_s = self.def_val.text()
        def_val_s = def_val_s.lower()
        if self.is_positive_integer(rows_s) and self.is_positive_integer(cols_s):
            rows = int(rows_s)
            cols = int(rows_s)
            if self.is_number(def_val_s) or def_val_s == self.blocked_cell:
                self.rows = rows
                self.cols = cols
                self.create_grid(self.rows, self.cols, def_val_s)
            else:
                self.show_message(
                    "Invalid default value",
                    "default value should be non-negative float/int " "or bc",
                )
        else:
            self.show_message(
                "Incorrect number of rows/cols",
                "number of rows/cols should be " "a strictly positive integer",
            )

    def create_grid(self, n_rows: int = 10, n_cols: int = 10, def_val: str = 1):
        replace_widget = False
        if len(self.cells):
            replace_widget = True
        grid_widget = QWidget()
        grid_widget.setMaximumSize(300, 300)
        grid_layout = QGridLayout()
        grid_widget.setLayout(grid_layout)
        grid_layout.setSpacing(0)
        self.cells = {}
        for i in range(n_rows):
            for j in range(n_cols):
                cell = QPlainTextEdit(def_val)
                cell.setStyleSheet(self.cell_params["white"])
                self.cells[(i, j)] = cell
                grid_layout.addWidget(cell, i, j)
        width = 700
        height = 700
        grid_widget.setFixedSize(width, height)
        if replace_widget:
            self.main_layout.replaceWidget(self.grid_widget, grid_widget)
        else:
            self.main_layout.addWidget(grid_widget)
        self.grid_widget = grid_widget

    def check_coord_correct(self, row: int, col: int) -> bool:
        if (0 > row or row >= self.rows) or col < 0 or col >= self.cols:
            return False
        return True

    def check_grid_correct(self, cell_vals: List[List[float]]) -> bool:
        for row in range(self.rows):
            for col in range(self.cols):
                val = self.cells[(row, col)].toPlainText()
                if val == self.blocked_cell:
                    cell_vals[row][col] = self.max_val
                elif self.is_number(val):
                    f_val = float(val)
                    if f_val >= 0:
                        cell_vals[row][col] = float(val)
                    else:
                        self.show_message("Error", "cell value should be non-negative")
                        return False
                else:
                    self.show_message(
                        "Error", "cell value should be a non-negative float"
                    )
                    return False
        return True

    def search_path(self):
        max_n = float("inf")
        cell_vals = [[0.0] * self.cols for _ in range(self.rows)]
        correct_grid = self.check_grid_correct(cell_vals)
        if not correct_grid:
            return
        for row in range(self.rows):
            for col in range(self.cols):
                self.cells[(row, col)].setPlainText("unk")
                self.cells[(row, col)].setStyleSheet(self.cell_params["cyan"])

        min_d = [[max_n] * self.cols for _ in range(self.rows)]
        no_prev = Point(-1, -1)
        start = Point(self.rows - 1, 0)
        dest = Point(0, self.cols - 1)
        self.cells[(start.x, start.y)].setPlainText(str(0))
        cell_vals[start.x][start.y] = 0.0
        cell_vals[dest.x][dest.y] = 0.0
        prev_cell = [[no_prev] * self.cols for _ in range(self.rows)]
        min_d[start.x][start.y] = cell_vals[start.x][start.y]
        self.cells[start].setStyleSheet(self.cell_params["yellow"])
        self.cells[dest].setStyleSheet(self.cell_params["purple"])

        if self.bfs_radio_button.isChecked():
            n_steps = self.breadth_first_search(
                min_d, prev_cell, cell_vals, start, dest
            )
        elif self.dfs_radio_button.isChecked():
            n_steps = self.depth_first_search(min_d, prev_cell, cell_vals, start, dest)
        elif self.dijkstra_radio_button.isChecked():
            n_steps = self.dijkstra_search(min_d, prev_cell, cell_vals, start, dest)
        else:
            n_steps = self.a_star_search(min_d, prev_cell, cell_vals, start, dest)

        # create path from dest to start
        curr = prev_cell[dest.x][dest.y]
        while curr != no_prev:
            QtTest.QTest.qWait(self.time_delay_ms)
            if prev_cell[curr.x][curr.y] != no_prev:
                self.cells[curr].setStyleSheet(self.cell_params["green"])
            curr = prev_cell[curr.x][curr.y]

        msg = "Min distance: {} \n Total steps: {}".format(
            min_d[dest[0]][dest[1]], n_steps
        )
        self.show_message("Search results:", msg)

    def show_message(self, title: str, msg: str) -> None:
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(msg)
        dlg.exec()

    def breadth_first_search(
        self,
        min_d: List[List[float]],
        prev_cell: List[List[Point]],
        cell_vals: List[List[float]],
        start: Point,
        dest: Point,
    ) -> int:
        points = deque([start])
        n_steps = 0
        while len(points):
            point = points.pop()
            for move in self.moves:
                new_p = Point(point.x + move.x, point.y + move.y)
                if (
                    self.check_coord_correct(*new_p)
                    and cell_vals[new_p.x][new_p.y] != self.max_val
                ):
                    new_d = min_d[point.x][point.y] + cell_vals[new_p.x][new_p.y]
                    if new_d < min_d[new_p.x][new_p.y]:
                        prev_cell[new_p.x][new_p.y] = point
                        points.appendleft(new_p)
                        min_d[new_p.x][new_p.y] = new_d
                        QtTest.QTest.qWait(self.time_delay_ms)
                        self.cells[new_p].setPlainText(str(new_d))
                        if new_p != dest:
                            self.cells[new_p].setStyleSheet(self.cell_params["red"])
                            QtTest.QTest.qWait(self.time_delay_ms)
                            self.cells[new_p].setStyleSheet(self.cell_params["blue"])
                        n_steps += 1
        return n_steps

    def depth_first_search(
        self,
        min_d: List[List[float]],
        prev_cell: List[List[Point]],
        cell_vals: List[List[float]],
        start: Point,
        dest: Point,
    ) -> int:
        def dfs_util(point) -> int:
            total_steps = 0
            for move in self.moves:
                new_p = Point(point.x + move.x, point.y + move.y)
                if (
                    self.check_coord_correct(*new_p)
                    and cell_vals[new_p.x][new_p.y] != self.max_val
                ):
                    new_d = min_d[point.x][point.y] + cell_vals[new_p.x][new_p.y]
                    if new_d < min_d[new_p.x][new_p.y]:
                        prev_cell[new_p.x][new_p.y] = point
                        min_d[new_p.x][new_p.y] = new_d
                        QtTest.QTest.qWait(self.time_delay_ms)
                        self.cells[new_p].setPlainText(str(new_d))
                        if new_p != dest:
                            self.cells[new_p].setStyleSheet(self.cell_params["red"])
                            QtTest.QTest.qWait(self.time_delay_ms)
                            self.cells[new_p].setStyleSheet(self.cell_params["blue"])
                            total_steps += dfs_util(new_p)
                            total_steps += 1
            return total_steps

        return dfs_util(start)

    def dijkstra_search(
        self,
        min_d: List[List[float]],
        prev_cell: List[List[Point]],
        cell_vals: List[List[float]],
        start: Point,
        dest: Point,
    ) -> int:
        points = [(min_d[start.x][start.y], start)]
        n_steps = 0
        while len(points):
            dist, point = heapq.heappop(points)
            for move in self.moves:
                new_p = Point(point.x + move.x, point.y + move.y)
                if (
                    self.check_coord_correct(*new_p)
                    and cell_vals[new_p.x][new_p.y] != self.max_val
                ):
                    new_d = dist + cell_vals[new_p.x][new_p.y]
                    if new_d < min_d[new_p.x][new_p.y]:
                        n_steps += 1
                        prev_cell[new_p.x][new_p.y] = point
                        heapq.heappush(points, (new_d, new_p))
                        min_d[new_p.x][new_p.y] = new_d
                        QtTest.QTest.qWait(self.time_delay_ms)
                        self.cells[new_p].setPlainText(str(new_d))
                        if new_p != dest:
                            self.cells[new_p].setStyleSheet(self.cell_params["red"])
                            QtTest.QTest.qWait(self.time_delay_ms)
                            self.cells[new_p].setStyleSheet(self.cell_params["blue"])
                        else:
                            return n_steps
        return n_steps

    def a_star_search(
        self,
        min_d: List[List[float]],
        prev_cell: List[List[Point]],
        cell_vals: List[List[float]],
        start: Point,
        dest: Point,
    ) -> int:
        def heuristic_f(p1: Point, p2: Point) -> float:
            return abs(p1.x - p2.x) + abs(p1.y - p2.y)

        # total path + heuristic distance, current point
        points = [(heuristic_f(start, dest) + cell_vals[start.x][start.y], start)]
        n_steps = 0
        while len(points):
            _, point = heapq.heappop(points)
            for move in self.moves:
                new_p = Point(point.x + move.x, point.y + move.y)
                if (
                    self.check_coord_correct(*new_p)
                    and cell_vals[new_p.x][new_p.y] != self.max_val
                ):
                    new_d = min_d[point.x][point.y] + cell_vals[new_p.x][new_p.y]
                    if new_d < min_d[new_p.x][new_p.y]:
                        n_steps += 1
                        prev_cell[new_p.x][new_p.y] = point
                        heapq.heappush(
                            points, (heuristic_f(dest, new_p) + new_d, new_p)
                        )
                        min_d[new_p.x][new_p.y] = new_d
                        QtTest.QTest.qWait(self.time_delay_ms)
                        self.cells[new_p].setPlainText(str(new_d))
                        if new_p != dest:
                            self.cells[new_p].setStyleSheet(self.cell_params["red"])
                            QtTest.QTest.qWait(self.time_delay_ms)
                            self.cells[new_p].setStyleSheet(self.cell_params["blue"])
                        else:
                            return n_steps
        return n_steps
