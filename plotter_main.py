#!/usr/bin/env python3

import sys
import pandas as pd
import numpy as np

from PySide2 import QtCore, QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


def read_data(fname):
    """The function that reads the file given in the -f arg.
    It removes all rows with strings and returns two 1d numpy arrays
    """
    data_arr = np.genfromtxt(fname, dtype='float64')

    return data_arr


class CustomTableModel(QtCore.QAbstractTableModel):
    """Class for creating the table model where the raw data from the csv is shown. 
    Maximum 100x100 array used. The user can choose the center index for the slice."""
    def __init__(self, data=None, tableindex=None):
        QtCore.QAbstractTableModel.__init__(self)

        self.tabledata = data
        self.tableindex = tableindex
        if self.tabledata.shape[0] < 101:
            pass
        else:
            self.lower_row = self.tableindex[1] - 50
            self.upper_row = self.tableindex[1] + 50
            self.lower_col = self.tableindex[0] - 50
            self.upper_col = self.tableindex[0] + 50
            self.tabledata = self.tabledata[self.lower_row:self.upper_row, self.lower_col:self.upper_col]
        self.row_count, self.column_count = np.shape(self.tabledata)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QtCore.QModelIndex()):
        return self.column_count

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            col_list = list(range(self.lower_col, self.upper_col))
            return col_list[section]
        if orientation == QtCore.Qt.Vertical:
            row_list = list(range(self.lower_row, self.upper_row))
            return row_list[section]
        else:
            return "{}".format(section)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return str("{:.2f}".format(self.tabledata[index.row(), index.column()]))
        elif role == QtCore.Qt.BackgroundRole:
            return QtGui.QColor(QtCore.Qt.white)
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignRight

        return None


class Widget(QtWidgets.QWidget):
    """Class for laying out the table, plot and plot options widgets."""
    def __init__(self):
        """The method describing the layout of the table, plotting
        and plot options windows.
        """
        QtWidgets.QWidget.__init__(self)
        try:
            self.tableindex
        except AttributeError:
            self.tableindex = [51, 51]
        try:
            self.data
        except AttributeError:
            self.open_csv()

        # Creating a QTableView
        self.model = CustomTableModel(self.data, self.tableindex)
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.model)

        # QTableView Headers
        resize = QtWidgets.QHeaderView.ResizeToContents
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(resize)
        self.vertical_header.setSectionResizeMode(resize)
        self.horizontal_header.setStretchLastSection(False)

        # Creating layout for plot options
        self.options = QtWidgets.QVBoxLayout()
        self.options.setContentsMargins(0, 2, 0, 2)  # (int left, int top, int right, int bottom)
        self.options.setSpacing(2)
        labelsize = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                          QtWidgets.QSizePolicy.Fixed)

        self.options.addStretch(stretch=50)

        self.label0 = QtWidgets.QLabel('x axis label: ')
        self.label0.setAlignment(QtCore.Qt.AlignBottom)
        self.label0.setSizePolicy(labelsize)
        self.options.addWidget(self.label0)
        self.x_axis_label = QtWidgets.QLineEdit('x axis label')
        self.options.addWidget(self.x_axis_label)
        self.options.addSpacing(5)

        self.label1 = QtWidgets.QLabel('y axis label: ')
        self.label1.setAlignment(QtCore.Qt.AlignBottom)
        self.label1.setSizePolicy(labelsize)
        self.options.addWidget(self.label1)
        self.y_axis_label = QtWidgets.QLineEdit('y axis label')
        self.options.addWidget(self.y_axis_label)
        self.options.addSpacing(5)

        self.label2 = QtWidgets.QLabel('axis label fontsize: ')
        self.label2.setAlignment(QtCore.Qt.AlignBottom)
        self.label2.setSizePolicy(labelsize)
        self.options.addWidget(self.label2)
        self.axis_label_fontsize = QtWidgets.QLineEdit('axis label fontsize')
        self.options.addWidget(self.axis_label_fontsize)
        self.options.addSpacing(5)

        self.label3 = QtWidgets.QLabel('tickmarks fontsize: ')
        self.label3.setAlignment(QtCore.Qt.AlignBottom)
        self.label3.setSizePolicy(labelsize)
        self.options.addWidget(self.label3)
        self.tickmarks_fontsize = QtWidgets.QLineEdit('tickmarks fontsize')
        self.options.addWidget(self.tickmarks_fontsize)
        self.options.addSpacing(5)

        self.label4 = QtWidgets.QLabel('shift y values: ')
        self.label4.setAlignment(QtCore.Qt.AlignBottom)
        self.label4.setSizePolicy(labelsize)
        self.options.addWidget(self.label4)
        self.shift_y_values = QtWidgets.QLineEdit('shift y values')
        self.options.addWidget(self.shift_y_values)
        self.options.addSpacing(5)

        self.label5 = QtWidgets.QLabel('multiply y values: ')
        self.label5.setAlignment(QtCore.Qt.AlignBottom)
        self.label5.setSizePolicy(labelsize)
        self.options.addWidget(self.label5)
        self.multiply_y_values = QtWidgets.QLineEdit('multiply y values')
        self.options.addWidget(self.multiply_y_values)
        self.options.addSpacing(5)

        self.button = QtWidgets.QPushButton('Replot', self)
        self.options.addWidget(self.button)
        self.button.clicked.connect(self.replot)
        self.options.addSpacing(10)

        self.label6 = QtWidgets.QLabel('Center column: ')
        self.label6.setAlignment(QtCore.Qt.AlignBottom)
        self.label6.setSizePolicy(labelsize)
        self.options.addWidget(self.label6)
        self.centercol = QtWidgets.QLineEdit('Center column')
        self.options.addWidget(self.centercol)
        self.options.addSpacing(5)

        self.label7 = QtWidgets.QLabel('Center row: ')
        self.label7.setAlignment(QtCore.Qt.AlignBottom)
        self.label7.setSizePolicy(labelsize)
        self.options.addWidget(self.label7)
        self.centerrow = QtWidgets.QLineEdit('Center row')
        self.options.addWidget(self.centerrow)
        self.options.addSpacing(5)

        self.button = QtWidgets.QPushButton('Recenter table', self)
        self.options.addWidget(self.button)
        self.button.clicked.connect(self.table_recenter)
        self.options.addSpacing(10)

        self.file_button = QtWidgets.QPushButton('CSV Import', self)
        self.options.addWidget(self.file_button)
        self.file_button.clicked.connect(self.new_csv)

        self.plot(self.data)

        # Left and main layout
        size = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        size.setHorizontalStretch(4)
        self.table_view.setSizePolicy(size)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.table_view)

        # Middle Layout
        size.setHorizontalStretch(4)
        self.main_layout.addLayout(self.plot_layout)

        # Right Layout
        size.setHorizontalStretch(1)
        self.main_layout.addLayout(self.options)

        # Set the layout to the QWidget
        self.setLayout(self.main_layout)

    def plot(self, data):
        """Creating matplotlib layout"""
        levels = MaxNLocator(nbins=15).tick_values(data[1:, 1:].min(), data[1:, 1:].max())
        self.fig = Figure(figsize=(7, 7), dpi=100, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.contourf(data[1:, 0], data[0, 1:], data[1:, 1:], levels=levels, cmap='inferno')
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
        self.canvas.draw()

    def replot(self):
        """The method that takes user inputs for plot options and calls for a replot"""
        x_axis_label = self.x_axis_label.text()
        y_axis_label = self.y_axis_label.text()
        axis_label_fontsize = self.axis_label_fontsize.text()
        tickmarks_fontsize = self.tickmarks_fontsize.text()
        shift_y_values = self.shift_y_values.text()
        multiply_y_values = self.multiply_y_values.text()
        y_shift = float(shift_y_values)
        y_factor = float(multiply_y_values)
        for i in range(self.num_files):
            data = self.data[i]
            data[:, 1] /= data[:, 1].max()
            self.plot.set_data(data[:, 0], y_factor * (data[:, 1] + y_shift))
        self.ax.set_xlabel(x_axis_label, fontsize=axis_label_fontsize)
        self.ax.set_ylabel(y_axis_label, fontsize=axis_label_fontsize)
        self.ax.tick_params(axis='both', which='major', labelsize=tickmarks_fontsize)
        self.canvas.draw()

    def table_recenter(self):
        """Method that centers the table on a new index"""
        col = self.centercol.text()
        row = self.centerrow.text()
        self.tableindex = [int(col), int(row)]
        self.model = CustomTableModel(self.data, self.tableindex)
        self.table_view.setModel(self.model)

        return None

    def open_csv(self):
        """Method opening first csv and saving data and headers"""
        filename, *_ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('Open txt'), self.tr("~/Desktop/"),
                                                             self.tr('Files (*.txt)'))
        self.data = read_data(filename)
        self.shape = np.shape(self.data)

        return None

    def new_csv(self):
        """Method opening new csv and saving data"""
        filename, *_ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('Open txt'), self.tr("~/Desktop/"),
                                                             self.tr('Files (*.txt)'))
        self.data = read_data(filename)
        self.shape = np.shape(self.data)

        self.model = CustomTableModel(self.data, None)
        self.table_view.setModel(self.model)

        self.plot.set_data(self.data[0, :], self.data[:, 0], self.data[1:, 1:])
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()
        return None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, widget):
        """Describes the main windows of the application including:
        window title, top menu bar,  exit button, buttom status bar,  and window dimensions.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Linear Plotter')
        self.setCentralWidget(widget)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')

        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        self.status = self.statusBar()
        self.status.showMessage('Data loaded and plotted')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = Widget()
    window = MainWindow(widget)
    window.show()

    sys.exit(app.exec_())
