"""A version of the GeneralTab with no functionality.
Used when opening someone else's image; the user should only
be able to view the image, not edit it."""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from CoralImage import *
from basic_styling import *

class ViewOnlyTab(QWidget):

    def __init__(self, load_image, load_count, load_coordinates, 
                 owner_name, owner_notes, upload_date):

        super().__init__()
        self.generalLayout = QGridLayout()

        self.loadImageName = load_image
        self.tentacleCount = load_count
        self.ownerName = owner_name
        self.uploadDate = upload_date
        self.coordString = load_coordinates
        self.coordList = load_coordinates.split("|")

        self.view_photo = CoralImage(isViewOnly=True)
        self.view_photo.browse_btn.setEnabled(False)

        self.view_photo.marker_count = 0
        self.view_photo.markers.clear()

        self.view_photo.open_image(filename=self.loadImageName)
        self.view_photo.imageOwnerDisplay.setText("{0}".format(self.ownerName))
        self.view_photo.zoom_in()

        placeLoadedCoordinates(self.coordList, self.view_photo, True)

        self.generalLayout.addWidget(self.view_photo, 1, 0)

        self.view_photo.view.setFixedWidth(800)
        self.view_photo.view.setFixedHeight(500)
        
        self.view_photo.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view_photo.view.setRenderHint(QPainter.Antialiasing)
        self.view_photo.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view_photo.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view_photo.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view_photo.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.view_dateLabel = QLabel("Upload Date & Time:")
        self.view_dateDisplay = QLineEdit(self.uploadDate)
        self.view_dateDisplay.setReadOnly(True)
        self.view_dateGridLayout = QGridLayout()
        self.view_dateGridLayout.addWidget(self.view_dateLabel, 0, 0)
        self.view_dateGridLayout.addWidget(self.view_dateDisplay, 0, 1)

        self.view_countLabel = QLabel("Tentacle Count:")
        self.view_countDisplay = QLineEdit("{0}".format(self.tentacleCount))
        self.view_countDisplay.setReadOnly(True)
        self.view_countGridLayout = QGridLayout()
        self.view_countGridLayout.addWidget(self.view_countLabel, 0, 0)
        self.view_countGridLayout.addWidget(self.view_countDisplay, 0, 1)

        self.notesLabel = QLabel("Notes:")
        self.notesDisplay = QLineEdit(owner_notes)
        self.notesDisplay.setReadOnly(True)
        self.notesGridLayout = QGridLayout()
        self.notesGridLayout.addWidget(self.notesLabel, 0, 0)
        self.notesGridLayout.addWidget(self.notesDisplay, 0, 1)

        self.zoomInButton = QPushButton('Zoom In')
        self.zoomInButton.setCursor(Qt.PointingHandCursor)
        self.zoomOutButton = QPushButton('Zoom Out')
        self.zoomOutButton.setCursor(Qt.PointingHandCursor)
        self.zoomInButton.clicked.connect(self.view_photo.zoom_in)
        self.zoomOutButton.clicked.connect(self.view_photo.zoom_out)

        self.smallGridLayout = QGridLayout()
        self.smallGridLayout.addWidget(self.zoomInButton, 0, 0)
        self.smallGridLayout.addWidget(self.zoomOutButton, 0, 1)

        self.zoomin_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoomout_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoomin_shortcut.activated.connect(self.view_photo.zoom_in)
        self.zoomout_shortcut.activated.connect(self.view_photo.zoom_out)

        self.rightGridLayout = QGridLayout()
        self.rightGridLayout.addLayout(self.view_photo.fileGridLayout, 1, 0)
        self.rightGridLayout.addLayout(self.view_photo.ownerGridLayout, 2, 0)
        self.rightGridLayout.addLayout(self.view_dateGridLayout, 3, 0)
        self.rightGridLayout.addLayout(self.view_countGridLayout, 4, 0)
        self.rightGridLayout.addLayout(self.notesGridLayout, 5, 0)
        self.rightGridLayout.addLayout(self.smallGridLayout, 6, 0)

        self.generalLayout.addLayout(self.rightGridLayout, 1, 1)

        self.view_countDisplay.setStyleSheet(
            "border: none;"
        )
        self.notesDisplay.setStyleSheet(
            "border: none;"
        )
        self.view_dateDisplay.setStyleSheet(
            "border: none;"
        )

        self.setStyleSheet(get_basic_styling())

        self.setLayout(self.generalLayout)


def placeLoadedCoordinates(coordList, coralImage, isViewOnly):
    if coordList[0] == '':
        return
    else:
        for point in coordList:
            color = point.split(";")[1].strip()
            coord = point.split(";")[0].strip()
            
            point_x = float(coord.split(",")[0].strip())
            point_y = float(coord.split(",")[1].strip())
            if isViewOnly:
                point_x /= 1.28

            coralImage.add_marker(point_x, point_y, color)