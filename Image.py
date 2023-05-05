from PhotoLabel import PhotoLabel

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Image(QWidget):
    
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

        grid.addWidget(btn, 0, 0, Qt.AlignTop)

        grid.addWidget(self.photo, 1, 0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet(
            "background: transparent;"
        )
        grid.addWidget(self.view, 1, 0, 1, 0)

        self.marker_count = 0
        self.markers = []
        self.marker_colors = []
        self.setAcceptDrops(True)

        self.fileGridLayout = QGridLayout()
        self.filenameLabel = QLabel("Current image being displayed:")
        self.filenameDisplay = QLineEdit("{0}".format(self.get_filename()))
        self.fileGridLayout.addWidget(self.filenameLabel, 0, 0)
        self.fileGridLayout.addWidget(self.filenameDisplay, 0, 1)
        grid.addLayout(self.fileGridLayout, 2, 0)

        # self.modelGridLayout = QGridLayout()
        # self.modelLabel = QLabel("Model status:")
        # self.modelDisplay = QLineEdit("{0}".format("Not running"))
        # self.modelGridLayout.addWidget(self.modelLabel, 0, 0)
        # self.modelGridLayout.addWidget(self.modelDisplay, 0, 1)
        # grid.addLayout(self.modelGridLayout, 3, 0)

        self.selected_marker = None 

        self.color_dict = {
            "YOLO Red": QColor(245, 96, 42), "Red": Qt.red, "Orange": QColor(255, 137, 0), 
            "Yellow": Qt.yellow, "Green": Qt.green, "Blue": Qt.blue, 
            "Purple": QColor(219, 0, 255), "Pink": QColor(245, 66, 164), "Black": Qt.black, 
            "White": Qt.white
        }

        # Keyboard shortcuts
        self.browse_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.browse_shortcut.activated.connect(self.open_image)

        self.filenameDisplay.setStyleSheet(
            "border: none;"
        )

        # self.modelDisplay.setStyleSheet(
        #     "border: none;"
        # )
        
    def reopen_image(self, filename):
        # filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
        # if not filename:
        #     return
        # self.path = str(filename)
        # url = QUrl.fromLocalFile(filename)
        # self.file = QFileInfo(filename).fileName()
            
        self.photo.setStyleSheet(
            "background: transparent;"
        )
        self.pix = QPixmap(filename)
        self.smaller_pixmap = self.pix.scaled(self.view.width(), self.view.height())
        self.scene.clear()
        self.scene.addPixmap(self.smaller_pixmap)
        self.filenameDisplay.setText("{0}".format(self.get_filename()))
        
    def open_image(self, filename=None):
        if not filename:
            filename, _ = QFileDialog.getOpenFileName(self, 'Select Photo', QDir.currentPath(), 'Images (*.png *.jpg)')
            if not filename:
                return
            self.path = str(filename)
            url = QUrl.fromLocalFile(filename)
            self.file = QFileInfo(filename).fileName()
            
        self.photo.setStyleSheet(
            "background: transparent;"
        )
        self.pix = QPixmap(filename)
        self.smaller_pixmap = self.pix.scaled(self.view.width(), self.view.height())
        self.scene.clear()
        self.scene.addPixmap(self.smaller_pixmap)
        self.filenameDisplay.setText("{0}".format(self.get_filename()))
        
    def get_filename(self):
        return self.file
    
    def get_marker_count(self):
        return self.marker_count
         
    def get_markersList(self):
        return self.markers
         
    def add_marker(self, x_pos, y_pos, color_name):
        if self.path is not "":
            print(color_name)
            ellipse = QGraphicsEllipseItem(0, 0, 15, 15)
            ellipse.setBrush(QBrush(self.color_dict[color_name]))
            ellipse.setFlag(QGraphicsItem.ItemIsMovable)
            ellipse.setFlag(QGraphicsItem.ItemIsSelectable)
            
            ellipse.setPos(x_pos, y_pos)
            print(ellipse.scenePos())

            self.scene.addItem(ellipse)
            self.marker_count += 1
            self.markers.append(ellipse)
            self.marker_colors.append(color_name)

    def set_selected_marker(self, marker):
        self.selected_marker = marker

    def remove_marker(self):
        for i, marker in enumerate(self.markers):
            if marker.isSelected():
                self.scene.removeItem(marker)
                self.markers.pop(i)
                self.marker_colors.pop(i)
                self.marker_count -= 1

    def undo_last_marker(self):
        if len(self.markers) > 0:
            last_marker = self.markers[len(self.markers) - 1]
            self.scene.removeItem(last_marker)
            self.markers.pop(len(self.markers) - 1)
            self.marker_colors.pop(len(self.markers) - 1)
            self.marker_count -= 1

    def change_color(self, color):
        brush_color = self.color_dict[color]
        for i, marker in enumerate(self.markers):
            if marker.isSelected():
                marker.setBrush(QBrush(brush_color))
                self.marker_colors[i] = brush_color

        # Clear the drop-down menu and add the color options agai(n)

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1/1.2, 1/1.2)


    