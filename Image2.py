import sys

from PhotoLabel import PhotoLabel

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from tkinter import *

from PIL import Image, ImageTk

import cv2 as cv
import numpy as np

class Image2(QWidget):
    
    def __init__(self):
        super().__init__()
        self.photo = PhotoLabel()
        self.photo.setFixedWidth(800)
        self.photo.setFixedHeight(500)
        
        btn = QPushButton('Browse')
        btn.setFixedWidth(800)
        btn.setFixedHeight(50)
        
        btn.setStyleSheet(
            "border: 3px solid;"
            "border-top-color: #3f72af;"
            "border-left-color: #3f72af;"
            "border-right-color: #3f72af;"
            "border-bottom-color: #3f72af;"
            "color: #00adb5;"
        )
        
        self.pix = QPixmap()
        btn.clicked.connect(self.open_image)
        
        self.path = ""
        self.file = ""
        
        grid = QGridLayout(self)
        #basewidth = 100
        #img = Image.open(self.photo)
        grid.addWidget(btn, 0, 0, Qt.AlignTop)
        grid.addWidget(self.photo, 1, 0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet(
            "background: transparent;"
        )
        grid.addWidget(self.view, 1, 0, 1, 4)
        self.marker_count = 0
        self.markers = []
        self.list = []
        self.setAcceptDrops(True)

        self.selected_marker = None 

        # Keyboard shortcuts
        self.browse_shortcut = QShortcut(Qt.Key_B, self)
        self.browse_shortcut.activated.connect(self.open_image)

        # self.remove_marker_shortcut = QShortcut(Qt.Key_R, self)
        # self.remove_marker_shortcut.activated.connect(self.remove_marker)
        
    def open_image(self, filename=None):
        #global photo_path
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
            if not filename:
                return
            self.path = str(filename)
            url = QUrl.fromLocalFile(filename)
            self.file = QFileInfo(filename).fileName()
            #path = str(filename)
            #print("Hello: " + self.path)
        self.photo.setStyleSheet(
            "background: transparent;"
        )
        self.pix = QPixmap(filename)
        self.smaller_pixmap = self.pix.scaled(self.view.width(), self.view.height())
        self.scene.clear()
        self.scene.addPixmap(self.smaller_pixmap)
    
        
        #self.photo.setPixmap(self.pix.scaledToHeight(400, Qt.FastTransformation))
       
        #self.path = str(photo_path)
        
    def get_filename(self):
        return self.file
    
    def get_marker_count(self):
        return self.marker_count
         
    
    def get_markersList(self):
        return self.markers
         
    def add_marker(self, x_pos, y_pos, color):
        if self.path is not "":
            ellipse = QGraphicsEllipseItem(x_pos, y_pos, 15, 15)
            ellipse.setBrush(QBrush(color))
            ellipse.setFlag(QGraphicsItem.ItemIsMovable)
            ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            self.scene.addItem(ellipse)
            self.marker_count += 1
            self.markers.append(ellipse)

    def set_selected_marker(self, marker):
        # Set selected marker
        self.selected_marker = marker

    def remove_marker(self):
        for i, marker in enumerate(self.markers):
            if marker.isSelected():
                self.scene.removeItem(marker)
                self.markers.pop(i)
                self.marker_count -= 1

    def undo_last_marker(self):
        last_marker = self.markers[len(self.markers) - 1]
        self.scene.removeItem(last_marker)
        self.markers.pop(len(self.markers) - 1)
        self.marker_count -= 1
