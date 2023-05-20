import platform
import os
import os.path
import PIL.Image
import pandas as pd

from dotenv import load_dotenv
from datetime import datetime
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from CoralImage import *
from RecordInfoWindow import *
from InstructionsWindow import *
from generalTab import *
from recordTab import *
from viewOnlyTab import *
from CodeDeleteWindow import *
from connectToDatabase import *
from coral_count import *

# https://www.youtube.com/watch?v=NwvTh-gkdfs 

class Coral_Window(QWidget):

    placeMarkersCall = pyqtSignal(int, int)
    showLoadingImage = pyqtSignal()
    hideLoadingImage = pyqtSignal()

    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Capturing Coral Tentacles")
        
        self.username = username
        self.username_Label = QLabel("Welcome, " + self.username + "!")
                
        self.move(0,0)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.coordinate_list = []

        self.closeAllViewTabsButton = QPushButton("Close All View Only Tabs")
        self.closeAllViewTabsButton.setCursor(Qt.PointingHandCursor)
        self.closeAllViewTabsButton.clicked.connect(lambda: self.closeViewOnlyTabs("All"))

        # Create the tab widget with two tabs
        self.tabs = QTabWidget()
        self.general_tab = generalTabUI(self)
        self.record_tab = recordTabUI(self)
        self.tabs.addTab(self.general_tab, "Main")
        self.tabs.addTab(self.record_tab, "Record")

        self.tabs.setStyleSheet(
            # "QTabBar::tab { width: 75px; height: 20px; }"
            "font-family: 'Lucida Sans Typewriter';"
        )

        layout.addWidget(self.username_Label)
        layout.addWidget(self.closeAllViewTabsButton)
        layout.addWidget(self.tabs)

        self.photo.clicked.connect(self.updateMarkerCount)
        self.photo.openedImage.connect(lambda: self.photo.modelDisplay.setText("Inactive"))
        self.showLoadingImage.connect(self.photo.loading_view.show)
        self.hideLoadingImage.connect(self.photo.loading_view.hide)

        self.placeMarkersCall.connect(self.placeInitialMarkers)

        # Keyboard shortcuts
        self.instructions_shortcut = QShortcut(Qt.Key_I, self)
        self.count_shortcut = QShortcut(Qt.Key_C, self)
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.remove_shortcut = QShortcut(Qt.Key_R, self)
        self.undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)

        self.zoomin_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        self.zoomout_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)

        self.delete_shortcut = QShortcut(Qt.Key_Delete, self)
        self.tab_shortcut = QShortcut(Qt.Key_Tab, self)

        # Connect shortcuts
        self.instructions_shortcut.activated.connect(self.instruct)
        self.count_shortcut.activated.connect(self.modelStart)
        
        self.save_shortcut.activated.connect(self.recordInfo)
        self.remove_shortcut.activated.connect(self.photo.remove_marker)
        self.remove_shortcut.activated.connect(self.updateMarkerCount)
        self.undo_shortcut.activated.connect(self.photo.undo_last_marker)
        self.undo_shortcut.activated.connect(self.updateMarkerCount)

        self.zoomin_shortcut.activated.connect(self.photo.zoom_in)
        self.zoomout_shortcut.activated.connect(self.photo.zoom_out)
        
        self.delete_shortcut.activated.connect(self.codeBeforeDeleteRow)
        self.tab_shortcut.activated.connect(self.switchTabs)

        self.tableWidget.doubleClicked.connect(self.reopen)
        
    def switchTabs(self):
        if self.tabs.currentIndex() == (self.tabs.count() - 1):
            self.tabs.setCurrentIndex(0)
            self.updateMarkerCount()
        else:
            self.tabs.setCurrentIndex(self.tabs.currentIndex() + 1)
            if self.tabs.currentIndex() == 1:
                self.DBConnect()
    
    def instruct(self):
        self.w = InstructionsWindow()
        self.w.closeButton.clicked.connect(self.instructions_close)
        self.w.setGeometry(int(self.frameGeometry().width()/2) - 150, int(self.frameGeometry().height()/2) - 150, 300, 300)
        self.w.show()
        
    def instructions_close(self):
        self.w.close()
         
    def codeBeforeDeleteRow(self):
        if self.tableWidget.rowCount() > 0:
            currentRow = self.tableWidget.currentRow()
            item = self.tableWidget.selectedItems()
            if (len(item) < 1):
                QMessageBox.about(self, "Warning", "Please select an entry to delete.")
            else:             
                question = QMessageBox()
                response = question.question(self,'', "Are you sure you want to delete the row?", question.Yes | question.No)
                
                if response == question.Yes:
                    headercount = self.tableWidget.columnCount()
                    for x in range(headercount):
                        headertext = self.tableWidget.horizontalHeaderItem(x).text()
                        if headertext == "NAME OF PERSON":
                            nameOfPerson = self.tableWidget.item(currentRow, x).text()  # get cell at row, col
                        if headertext == "DATE UPLOADED":
                            dateUploaded = self.tableWidget.item(currentRow, x).text()
                    
                    filenameForQuery = item[0].text()
                    
                    self.codeDelete = CodeDeleteWindow()
                    self.codeDelete.setGeometry(int(self.frameGeometry().width()/2) - 150, int(self.frameGeometry().height()/2) - 150, 300, 300)
                    self.codeDelete.show()
                    self.codeDelete.submitButtonLogin.clicked.connect(lambda: self.deleteRow(currentRow, filenameForQuery, nameOfPerson, dateUploaded))

                    self.codeDelete.submit_shortcut.activated.connect(lambda: self.deleteRow(currentRow, filenameForQuery, nameOfPerson, dateUploaded))
                    
                else:
                    question.close()
    
                    
    def deleteRow(self, currentRow, filenameForQuery, nameOfPerson, dateUploaded):        
        try:
            mydb = connectToDatabase()
            mycursor = mydb.cursor()
            
            mycursor.execute("SELECT users_code FROM users WHERE users_name = '%s'" % nameOfPerson)
            myresult = mycursor.fetchall()

            str = ''.join(myresult[0])

            if (self.codeDelete.codeTextBox.text() == str):
                sql_delete = "DELETE FROM image_info WHERE filename = %s and date_uploaded = %s"
                sql_data = (filenameForQuery, dateUploaded)

                mycursor.execute(sql_delete, sql_data)
                self.tableWidget.removeRow(currentRow)
                self.codeDelete.close()
            elif (self.codeDelete.codeTextBox.text() == ""):
                QMessageBox.about(self, "Warning", "Please enter a code.")
                self.codeDelete.close()
                self.codeBeforeDeleteRow()
            else: 
                QMessageBox.about(self, "Warning", "Wrong code!")
                self.codeDelete.close()
        
            mydb.commit()
            mydb.close()
        except mydb.Error as e:
            print("Failed To Connect to Database")
        
                
    def codeBeforeDeleteAllRows(self):
        question = QMessageBox()
        response = question.question(self,'', "Are you sure you want to delete ALL the rows?", question.Yes | question.No)
                
        if response == question.Yes:
            self.codeDeleteAllWindow = CodeDeleteWindow()
            self.codeDeleteAllWindow.label.setText("Enter ADMIN code:")
            self.codeDeleteAllWindow.setGeometry(int(self.frameGeometry().width()/2) - 150, int(self.frameGeometry().height()/2) - 150, 300, 300)
            self.codeDeleteAllWindow.show()

            self.codeDeleteAllWindow.submitButtonLogin.clicked.connect(self.deleteAllRows) 
            self.codeDeleteAllWindow.submit_shortcut.activated.connect(self.deleteAllRows)   
        else:
            question.close()
                
    def deleteAllRows(self):
        try:
            mydb = connectToDatabase()
            mycursor = mydb.cursor()
            
            mycursor.execute("SELECT users_code FROM users WHERE users_name = '%s'" % os.getenv('ADMIN'))
            myresult = mycursor.fetchall()

            str = ''.join(myresult[0])

            if (self.codeDeleteAllWindow.codeTextBox.text() == str):
                mycursor.execute("DELETE FROM image_info")
            
                mydb.commit()
                while (self.tableWidget.rowCount() > 0):
                    self.tableWidget.removeRow(0)
                self.codeDeleteAllWindow.close()
            else:
                QMessageBox.about(self, "Warning", "Wrong code.\nONLY THE ADMIN CAN DELETE ALL THE ROWS!")
                self.codeDeleteAllWindow.close()
                
            
            mydb.close()
                
        except mydb.Error as e:
            print("Failed To Connect to Database")

        
    
    def DBConnect(self):
        try:
            mydb = connectToDatabase()
            
            mycursor = mydb.cursor()

            mycursor.execute("SELECT * FROM image_info")

            result = mycursor.fetchall()
        
            self.tableWidget.setRowCount(0)

            for row_number, row_data in enumerate(result):
                self.tableWidget.insertRow(row_number)

                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    # Only filename should be selectable
                    if column_number != 0:
                        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

                    self.tableWidget.setItem(row_number, column_number, item)

            mydb.close()
        except mydb.Error as e:
           print("Failed To Connect to Database")

    def searchRecord(self, search_text):
        rowsToDelete = []

        for row in range(self.tableWidget.rowCount()):
            item_name = self.tableWidget.item(row, 2).text().lower()
            item_file = self.tableWidget.item(row, 0).text().lower()
            item_date = self.tableWidget.item(row, 3).text().lower()
            item_notes = self.tableWidget.item(row, 5).text().lower()

            if (search_text.lower() not in item_name and search_text.lower() not in item_file 
                and search_text.lower() not in item_date and search_text.lower() not in item_notes):
                    rowsToDelete.append(row)

        # Counter: adjust for the fact that we're removing a row each time
        counter = 0
        for row in rowsToDelete:
            self.tableWidget.removeRow(row-counter)
            counter += 1
    
    def reopen(self):
        if not self.tableWidget.selectedItems():
            QMessageBox.about(self, "Warning", "Please select an entry to reopen.")
        else:
            try:
                mydb = connectToDatabase()
                
                mycursor = mydb.cursor()
                
                item = self.tableWidget.selectedItems()
                row = item[0].row()
                filenameForQuery = item[0].text()
                
                mycursor.execute("SELECT * FROM image_info WHERE filename='%s'" % filenameForQuery)
                
                myresult = mycursor.fetchone()[6]
                tentacleCount = self.tableWidget.item(row, 1).text()
                ownerName = self.tableWidget.item(row, 2).text()
                dateUploaded = self.tableWidget.item(row, 3).text()
                coordinates = self.tableWidget.item(row, 4).text()
                ownerNotes = self.tableWidget.item(row, 5).text()

                with open(filenameForQuery, "wb") as file:
                    file.write(myresult)
                    file.close()
                
                if (ownerName != self.username):
                    self.view_tab = viewOnlyTabUI(
                        self, filenameForQuery, tentacleCount, 
                        coordinates, ownerName, ownerNotes, dateUploaded
                    )
                    self.closeViewTabButton = QPushButton()
                    self.closeViewTabButton.setCursor(Qt.PointingHandCursor)
                    self.closeViewTabButton.setIcon(
                        self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
                    )
                    self.closeViewTabButton.setIconSize(QSize(10, 10))
                    self.closeViewTabButton.setStyleSheet(
                        "border: none;"
                        "color: white;"
                        "background-color: none;"
                        "padding: 0px;"
                    )
                    
                    viewTabText = "View - " + ownerName + ", " + filenameForQuery + " | " + dateUploaded

                    i = 0
                    while i < self.tabs.count():
                        if self.tabs.tabText(i) == viewTabText:
                            self.tabs.setCurrentIndex(i)

                            if (os.path.exists(filenameForQuery)):
                                os.remove(filenameForQuery)

                            return
                        else:
                            i += 1

                    self.tabs.addTab(self.view_tab, viewTabText)
                    self.tabs.tabBar().setTabButton(
                        self.tabs.count()-1, QTabBar.RightSide, self.closeViewTabButton
                    )
                    self.tabs.setTabToolTip(self.tabs.count()-1, viewTabText)
                    self.tabs.setCurrentIndex(self.tabs.count()-1)

                    self.closeViewTabButton.clicked.connect(lambda: self.closeViewOnlyTabs(viewTabText))

                    if (os.path.exists(filenameForQuery)):
                        os.remove(filenameForQuery)
                else:
                    self.photo.open_image(filename=filenameForQuery)
                    self.clearOldCoordinates()

                    placeLoadedCoordinates(coordinates.split("|"), self.photo, False)
                    self.updateMarkerCount()
                    self.tabs.setCurrentIndex(0)

                mydb.close()
            
            except mydb.Error as e:
                print("Failed To Connect to Database")
                    
    def export(self):
        try:
            mydb = connectToDatabase()
            
            mycursor = mydb.cursor(buffered=True) # Needed for saving all pictures to desktop

            mycursor.execute("Select filename, tentacle_count, name_of_person, date_uploaded, coordinates_of_markers, notes from image_info")

            result = mycursor.fetchall()
            
            all_filenames = []
            all_tentacle_count = []
            all_name_of_person = []
            all_date_uploaded = []
            all_coordinates_of_markers = []
            all_notes = []
            
            for filename, tentacle_count, name_of_person, date_uploaded, coordinates_of_markers, notes in result:
                all_filenames.append(filename)
                all_tentacle_count.append(tentacle_count)
                all_name_of_person.append(name_of_person)
                all_date_uploaded.append(date_uploaded)
                all_coordinates_of_markers.append(coordinates_of_markers)
                all_notes.append(notes)
            
            dictionary = {
                "FILENAME": all_filenames, "TENTACLE COUNT": all_tentacle_count, 
                "NAME OF PERSON": all_name_of_person, "DATE UPLOADED": all_date_uploaded, 
                "COORDINATES OF MARKERS": all_coordinates_of_markers, "NOTES": all_notes
            }

            df = pd.DataFrame(dictionary)
            windows_dirname = "C:\\temp\Capturing Coral Images"
            mac_dirname = os.path.expanduser("~/Desktop/Capturing Coral Images")

            if platform.system() == 'Windows':
                df.to_csv("C:\\temp\CoralCountEntries.csv", na_rep="None")
                if not os.path.exists(windows_dirname):
                    os.mkdir(windows_dirname)
            else:
                df.to_csv(os.path.expanduser("~/Desktop/CoralCountEntries.csv"))
                if not os.path.exists(mac_dirname):
                    os.mkdir(mac_dirname)
            
            # Save all pictures to the person's computer. [*set()] clears duplicates.
            for filename in [*set(all_filenames)]:
                mycursor.execute("SELECT * FROM image_info WHERE filename='%s'" % filename)
                myresult = mycursor.fetchone()[6]

                if platform.system() == 'Windows':
                    with open(os.path.join(windows_dirname, filename), "wb") as file:
                        file.write(myresult)
                        file.close()
                else:
                    with open(os.path.join(mac_dirname, filename), "wb") as file:
                        file.write(myresult)
                        file.close()                

            QMessageBox.about(self, "Notice", 
                """Check your desktop for the csv file and all image files!
                \n(Windows: See temp folder in C: drive)"""
            )
            mydb.close()
        except mydb.Error as e:
           print("Failed To Connect to Database")
            
    def recordInfo(self):   
        if self.tabs.currentIndex() == 0:
            if not self.photo.get_filename():
                QMessageBox.about(self, "Warning", "You did not upload an image!")
            else:
                self.g = RecordInfoWindow(self.username)
                self.g.submitButton.clicked.connect(self.gatheringInfo)
                self.g.submit_shortcut.activated.connect(self.gatheringInfo)

                self.g.setGeometry(int(self.frameGeometry().width()/2) - 150, int(self.frameGeometry().height()/2) - 150, 300, 300)
                self.g.show()
            
    def convertToBinaryData(self, filename):
    # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData
            
    def gatheringInfo(self):  
        if self.g.notes_Display.text() == "":
            QMessageBox.about(self, "Warning", "Please enter notes.")
            self.g.close()
            self.recordInfo()
        else:
            try:
                mydb = connectToDatabase()
                
                    
                mycursor = mydb.cursor()
                        
                for i, marker in enumerate(self.photo.markers):
                    self.coordinate_list.append(
                        str(marker.x()) + ', ' + str(marker.y()) 
                        + ' ; ' + str(self.photo.marker_colors[i])
                    )

                coordstring = ' | '.join(self.coordinate_list)

                with open(self.photo.get_path(), "rb") as file:
                    binaryData = file.read()       
                                            
                mycursor.execute(
                    "INSERT INTO image_info VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                    (
                        self.photo.get_filename(), self.photo.marker_count, 
                        self.username, datetime.today(), 
                        coordstring, self.g.get_notes(), binaryData
                    )
                )
                
                self.tableWidget.resizeRowsToContents()
            
                mydb.commit()
                
                self.DBConnect()
                self.g.close()
                mydb.close()
                
            except mydb.Error as e:
                print("Failed To Connect to Database")

    
    def modelStart(self):
        self._modelThread = Thread(target=self.countTentacles)

        if "YOLO Red" not in self.photo.marker_colors:
            if (self.photo.get_filename() == ""):
                QMessageBox.about(self, "Warning", "Please upload an image.")
            else:
                self.photo.modelDisplay.setText("Running...")
                self._modelThread.start()
                print("Finished")
        else:
            QMessageBox.about(self, "Error", "The model has already run.")

        return self

    def countTentacles(self):
        self.showLoadingImage.emit()

        # Run the model on the currently displayed photo (in Image)
        count_tentacles_actual(self.photo.path)
        img = PIL.Image.open(self.photo.path)
        
        # Add markers based on the labels generated by the model
        # Since you can't call another function within a thread, have to use signal slot
        self.placeMarkersCall.emit(img.width, img.height)

        # Delete the new resized.jpg created in the main folder
        if (os.path.exists('resized.jpg')):
            os.remove('resized.jpg')

        self.hideLoadingImage.emit()
        self.photo.modelDisplay.setText("Finished")
        return None

    def placeInitialMarkers(self, photo_width, photo_height):
        coordinates = get_coordinates()

        if not coordinates or len(coordinates) <= 5:
            QMessageBox.about(
                self, "Error", 
                """Few to no tentacles were found. Are you sure this is a clear coral image?"""
            )
            if not coordinates:
                return None

        for pair in coordinates:
            self.photo.add_marker(
                pair[0]*(photo_width/1.6), pair[1]*(photo_height/1.5), "YOLO Red"
            )
        
        self.updateMarkerCount()

    def updateMarkerCount(self):
        self.countDisplay.setText("{0}".format(self.photo.marker_count))

    def clearOldCoordinates(self):
        self.photo.marker_count = 0
        self.photo.markers.clear()
        self.photo.marker_colors.clear()
        self.coordinate_list.clear()
        self.photo.modelDisplay.setText("Inactive")
        self.updateMarkerCount()

    def confirmForClearCoordinates(self):
        question = QMessageBox()
        response = question.question(
            self,'', "Are you sure you want to delete all the markers?", 
            question.Yes | question.No)
    
        if response == question.Yes:
            while (len(self.photo.markers)) > 0:
                self.photo.scene.removeItem(self.photo.markers[0])
                self.photo.markers.pop(0)

            self.clearOldCoordinates()
        else:
            question.close()

    def closeViewOnlyTabs(self, text):
        if text != "All":
            i = 0
            while i < self.tabs.count():
                if self.tabs.tabText(i) == text:
                    self.tabs.removeTab(i)
                    return
                else:
                    i += 1
        else:
            while self.tabs.count() > 2:
                self.tabs.removeTab(2)
