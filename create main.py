import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QListWidget, QWidget
import data_handler  # You should implement this module
import time
import smtplib
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import paho.mqtt.client as mqtt
import datetime

# Set the SMTP server and login credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "tanya4849.be@22chitkara.edu.in"  
SMTP_PASSWORD = "987654321"  

# Set the sender and recipient addresses
sender = "sender@gmail.com"  # Replace with the hospital's email address

# Current patient's data
aid = ""
patients = []

spo2 = 0.0
temp = 0.0
hr = 0.0

# -------------------------------------------- List patients/ Entry Screen ------------------------------------------
class ListPatients(QListWidget):
    def __init__(self):
        super(ListPatients, self).__init__()
        loadUi("list_patients.ui", self)
        self.pushButton.clicked.connect(self.goToAddPatients)
        self.pushButton_2.clicked.connect(self.search)
        self.listWidget.itemDoubleClicked.connect(self.patientClicked)
        all = data_handler.get_all()

        if all:
            for patient in all:
                self.listWidget.addItem(f"{patient[0]} | {patient[1]}")

    def goToAddPatients(self):
        screen2 = AddPatient()
        widget.addWidget(screen2)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def search(self):
        self.listWidget.clear()
        global patients
        name = self.lineEdit.text()
        patients = data_handler.search(name)
        if not patients:
            self.label_2.setText("No patient(s) found")
            self.label_2.repaint()
        else:
            self.label_2.setText("Results")
            self.label_2.repaint()
            for patient in patients:
                self.listWidget.addItem(f"{patient[0]} | {patient[1]}")

    def patientClicked(self, item):
        aid = patients[self.currentRow()][1]
        print(aid)
        time.sleep(1)
        screen3 = PatientDetails()
        widget.addWidget(screen3)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# ---------------------------------------- Add Patient screen class ---------------------------------------------------------
class AddPatient(QDialog):
    def __init__(self):
        super(AddPatient, self).__init()
        loadUi("add_patient.ui", self)
        self.pushButton.clicked.connect(self.goToList)
        self.pushButton_2.clicked.connect(self.goBack)

    def goToList(self):
        name = self.I_Name.text()
        a_id = self.I_Aadhar.text()
        dev_no = self.I_Device.text()
        age = self.I_Age.text()
        sex = self.I_Sex.text()
        mail = self.I_Mail.text()
        status = data_handler.add_patient(name=name, aid=a_id, mail=mail, did=dev_no, age=age, sex=sex)

        if status == 0:
            time.sleep(1)
            self.label_1.setText("No entries should be empty")
            self.label_1.show()
            self.label_1.repaint()
        elif status == 2:
            time.sleep(1)
            self.label_1.setText("Patient already exists")
            self.label_1.show()
            self.label_1.repaint()
        elif status == 3:
            self.label_1.setText("Patient added successfully")
            self.label_1.show()
            self.label_1.repaint()
            time.sleep(3)
            self.goBack()

    def goBack(self):
        mainwindow = ListPatients()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# ------------------------------------------------- Patient Details class ----------------------------------------------------
class PatientDetails(QDialog):
    def __init__(self):
        global aid
        super(PatientDetails, self).__init()
        loadUi("patient_details.ui", self)
        patient = data_handler.patient_det(str(aid))
        name = patient[0]
        age = patient[4]
        self.label.setText(name)
        self.label_3.setText(age)
        self.label_4.setText(self.diagnose())
        self.pushButton_4.clicked.connect(self.sendEmail)
        self.pushButton.clicked.connect(self.goBack)
        self.pushButton_3.clicked.connect(self.removePatient)
        self.pushButton_2.clicked.connect(self.viewPlot)

    def removePatient(self):
        data_handler.remove_pat(aid)
        time.sleep(0.5)
        self.goBack()

    def goBack(self):
        mainwindow = ListPatients()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def sendEmail(self):
        patient = data_handler.patient_det(str(aid))
        subject = 'Health Update from Karti\'s eMPS App'
        body = self.textEdit.text()
        recipient = patient[3]
        msg = f"Subject: {subject}\n\n{body}"
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(sender, recipient, msg)
        server.quit()

    def viewPlot(self):
        # Add code to display a plot here using the patient's data
        pass

    def diagnose(self):
        # Add code to diagnose the patient's condition based on their data
        pass

# ----------------------------------------------- MQTT receiver and Database updater -------------------------
running = True
message = ''
prev_message = ''

# Set the MQTT broker address and topic
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_TOPIC = "ePMS"

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootbar",
    database="mydatabase"
)

def onConnect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def mqttReceiver():
    client.connect(MQTT_BROKER, 1883, 60)
    if running:
        client.loop_forever()

def onMessage(client, userdata, msg):
    # Store the received message in a global variable
    global message
    message = msg.payload

def database_updater():
    while running:
        if message != prev_message:
            global temp, hr, spo2, aid
            prev_message = message
            mycursor = db.cursor()
            did = data_handler.patient_det(aid)[3]
            d_id = int(message.split()[1])
            l_temp = float(message.split()[2])
            l_hr = float(message.split()[3])
            l_spo2 = float(message.split()[4])      

            if (did == d_id):
                temp = l_temp
                hr = l_hr
                spo2 = l_spo2
        
            now = datetime.datetime.utcnow()
            query = "INSERT INTO dataArd(dt, heart, temp, spo) VALUES (%s, %s, %s)"
            mycursor.execute(query, (now.strftime('%Y-%m-%d %H:%M:%S'), l_hr, l_temp, l_spo2))

            mycursor.close()
            time.sleep(3)
        

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)

mqtt_thread = threading.Thread(target=mqtt_receiver, daemon=True)
data_updater_thread = threading.Thread(target=database_updater, daemon=True)


# ----------------------------------------------- Main Body --------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('ukui')
    widget = QtWidgets.QStackedWidget()
    mainwindow = list_patients()
    widget.addWidget(mainwindow)

    mqtt_thread.start()
    data_updater_thread.start()
    widget.show()


    try:
        running = False
        mqtt_thread.join()
        data_updater_thread.join()
        db.close()
        sys.exit(app.exec_())
    except:
        print("Exiting")
