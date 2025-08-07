# This work has been implemented by Alin-Bogdan Popa and Bogdan-Calin Ciobanu,
# under the supervision of prof. Pantelimon George Popescu, within the Quantum
# Team in the Computer Science and Engineering department,Faculty of Automatic 
# Control and Computers, National University of Science and Technology 
# POLITEHNICA Bucharest (C) 2024. In any type of usage of this code or released
# software, this notice shall be preserved without any changes.


import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QStatusBar, QMessageBox, QSpacerItem, QSizePolicy, QLineEdit
)
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator
from PyQt5.QtCore import Qt
from PyQt5.Qt import QSize
from PyQt5.QtWidgets import QRadioButton, QButtonGroup, QTextEdit
from PyQt5.QtWidgets import QFrame
import subprocess
import os

qkdgkt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'QKD-Infra-GetKey'))
sys.path.append(qkdgkt_path)
import qkdgkt
import json

from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets

class QKDApp(QWidget):
    def __init__(self):
        self.public_key_str = ""
        self.type = None
        super().__init__()
        self.initUI()

    def set_ellipsized_text(self, label, text):
        # font_metrics = QFontMetrics(label.font())
        # available_width = label.width()
        # # Measure the text and trim if necessary
        # elided_text = font_metrics.elidedText(text, Qt.ElideRight, available_width)
        # # Set the trimmed text to the label
        # label.setText(elided_text)
        label.setText(text)

    def initUI(self):
        # Main layout
        self.window_layout = QVBoxLayout()
        self.layout = QHBoxLayout()
        self.buttons_layout = QVBoxLayout()
        self.about_layout = QVBoxLayout()

        # initially, layout contains only 2 buttons: client and server
        # once clicked, the buttons are replaced with the respective forms
        # and the status bar is updated with the current step
        self.type_client_button = QPushButton("Client")
        self.type_client_button.clicked.connect(self.init_client)
        self.type_server_button = QPushButton("Server")
        self.type_server_button.clicked.connect(self.init_server)
        self.buttons_layout.addWidget(self.type_client_button)
        self.buttons_layout.addWidget(self.type_server_button)

        # Status bar
        self.status_bar = QStatusBar()

        # Config layouts
        self.window_layout.addLayout(self.layout)
        self.window_layout.addWidget(self.status_bar)
        self.layout.addLayout(self.buttons_layout)
        self.layout.addLayout(self.about_layout)

        # Set main layout
        self.setLayout(self.window_layout)

        # Window properties
        self.setWindowTitle('Quantum VPN')
        self.setGeometry(300, 100, 400, 100)
        self.show()
    
    def init_client(self):
        self.init_buttons("client")

    def init_server(self):
        self.peers = []
        self.init_buttons("server")

    def init_buttons(self, type):
        self.setGeometry(300, 100, 900, 200)
        self.type = type

        # remove the client and server buttons
        self.type_client_button.hide()
        self.type_server_button.hide()

        # Step: Generate authentication keys
        self.step_auth_layout = QHBoxLayout()
        self.step_auth_button = QPushButton("Generate WireGuard Key Pair")
        self.step_auth_button.clicked.connect(self.generate_wireguard_keys)
        self.step_auth_button.setEnabled(True)
        self.step_auth_status = QLabel("")
        self.step_auth_status.setFixedSize(20, 20)
        self.step_auth_layout.addWidget(self.step_auth_status)
        self.step_auth_layout.addWidget(self.step_auth_button)
        self.buttons_layout.addLayout(self.step_auth_layout)

        # Label to display the public key
        self.public_key_label = QLabel()
        self.public_key_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_button = QPushButton("")
        self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(self.public_key))
        self.copy_button.setIcon(QIcon("copyicon.png"))
        self.copy_button.setIconSize(QSize(20, 20))
        self.copy_button.setFixedSize(30, 30)
        self.copy_space = QLabel("")
        self.copy_space.setFixedSize(20, 20)
        self.public_key_layout = QHBoxLayout()
        self.public_key_layout.addWidget(self.copy_space)
        self.public_key_layout.addWidget(self.public_key_label)
        self.public_key_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.public_key_layout.addWidget(self.copy_button)
        self.copy_button.hide()
        self.buttons_layout.addLayout(self.public_key_layout)

        if self.type == "client":
            # # Step: Acquire QKD key
            # self.step_qkd_layout = QHBoxLayout()
            # self.step_qkd_button = QPushButton("Acquire QKD Key")
            # self.step_qkd_button.clicked.connect(self.acquire_qkd_key)
            # self.step_qkd_button.setEnabled(False)
            # self.step_qkd_status = QLabel("")
            # self.step_qkd_status.setFixedSize(20, 20)
            # self.step_qkd_layout.addWidget(self.step_qkd_status)
            # self.step_qkd_layout.addWidget(self.step_qkd_button)
            # self.buttons_layout.addLayout(self.step_qkd_layout)
            # Step: Acquire QKD key
            self.step_qkd_layout = QVBoxLayout()

            # Create radio buttons for selecting key acquisition mode
            self.radio_fresh_key = QRadioButton("Acquire Fresh Key")
            self.radio_paste_key = QRadioButton("Paste Base64 Key")
            self.radio_fresh_key.setChecked(True)  # Default selection

            # Add radio buttons to a button group to manage selection
            self.key_selection_group = QButtonGroup()
            self.key_selection_group.addButton(self.radio_fresh_key)
            self.key_selection_group.addButton(self.radio_paste_key)

            # Create a text field for pasting a Base64 key
            self.paste_key_field = QTextEdit()
            self.paste_key_field.setPlaceholderText("Paste your Base64 key here")
            self.paste_key_field.setDisabled(True)  # Initially disabled

            # Connect radio button changes to enable/disable the paste field
            self.radio_fresh_key.toggled.connect(self.toggle_key_field)

            # Add elements to the layout
            self.step_qkd_layout.addWidget(self.radio_fresh_key)
            self.step_qkd_layout.addWidget(self.radio_paste_key)
            self.step_qkd_layout.addWidget(self.paste_key_field)

            # Create the QKD key acquisition button and status indicator
            self.step_qkd_button = QPushButton("Acquire QKD Key")
            self.step_qkd_button.clicked.connect(self.acquire_qkd_key)
            self.step_qkd_status = QLabel("")
            self.step_qkd_status.setFixedSize(20, 20)

            # Add the button and status indicator to a horizontal layout
            self.qkd_button_layout = QHBoxLayout()
            self.qkd_button_layout.addWidget(self.step_qkd_status)
            self.qkd_button_layout.addWidget(self.step_qkd_button)

            # Add the button layout to the main layout
            self.step_qkd_layout.addLayout(self.qkd_button_layout)

            # Finally, add the layout to your main layout (assumed to be `buttons_layout` in your case)
            self.buttons_layout.addLayout(self.step_qkd_layout)


            # Label to display the QKD key id
            self.qkd_key_id_label = QLabel("")
            self.qkd_key_id_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.qkd_key_id_copy_button = QPushButton("")
            self.qkd_key_id_copy_button.clicked.connect(lambda: QApplication.clipboard().setText(self.qkd_key_id))
            self.qkd_key_id_copy_button.setIcon(QIcon("copyicon.png"))
            self.qkd_key_id_copy_button.setIconSize(QSize(20, 20))
            self.qkd_key_id_copy_button.setFixedSize(30, 30)
            self.qkd_key_id_copy_space = QLabel("")
            self.qkd_key_id_copy_space.setFixedSize(20, 20)
            self.qkd_key_id_layout = QHBoxLayout()
            self.qkd_key_id_layout.addWidget(self.qkd_key_id_copy_space)
            self.qkd_key_id_layout.addWidget(self.qkd_key_id_label)
            self.qkd_key_id_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.qkd_key_id_layout.addWidget(self.qkd_key_id_copy_button)
            self.qkd_key_id_copy_button.hide()
            self.buttons_layout.addLayout(self.qkd_key_id_layout)

            # WireGuard client config
            self.server_public_key_label = QLabel("Server Public Key:")
            self.server_public_key_field = QLineEdit()
            self.server_ip_label = QLabel("Server IP:")
            self.server_ip_field = QLineEdit()
            self.server_port_label = QLabel("Server Port:")
            self.server_port_field = QLineEdit()
            self.server_port_field.setValidator(QIntValidator())
            self.server_port_field.setMaxLength(5)
            self.peer_ip_label = QLabel("Peer IP:")
            self.peer_ip_field = QLineEdit()
            self.buttons_layout.addWidget(self.server_public_key_label)
            self.buttons_layout.addWidget(self.server_public_key_field)
            self.buttons_layout.addWidget(self.server_ip_label)
            self.buttons_layout.addWidget(self.server_ip_field)
            self.buttons_layout.addWidget(self.server_port_label)
            self.buttons_layout.addWidget(self.server_port_field)
            self.buttons_layout.addWidget(self.peer_ip_label)
            self.buttons_layout.addWidget(self.peer_ip_field)
            # hide the fields initially
            self.server_public_key_label.hide()
            self.server_public_key_field.hide()
            self.server_ip_label.hide()
            self.server_ip_field.hide()
            self.server_port_label.hide()
            self.server_port_field.hide()
            self.peer_ip_label.hide()
            self.peer_ip_field.hide()
        else:
            # Step: Add peers
            self.peer_ip_label = QLabel("Peer IP:")
            self.peer_ip_field = QLineEdit()
            self.peer_public_key_label = QLabel("Peer Public Key:")
            self.peer_public_key_field = QLineEdit()
            self.peer_qkd_key_id_label = QLabel("Peer QKD Key ID:")
            self.peer_qkd_key_id_field = QLineEdit()
            self.buttons_layout.addWidget(self.peer_ip_label)
            self.buttons_layout.addWidget(self.peer_ip_field)
            self.buttons_layout.addWidget(self.peer_public_key_label)
            self.buttons_layout.addWidget(self.peer_public_key_field)
            self.buttons_layout.addWidget(self.peer_qkd_key_id_label)
            self.buttons_layout.addWidget(self.peer_qkd_key_id_field)
            self.peer_ip_label.hide()
            self.peer_ip_field.hide()
            self.peer_public_key_label.hide()
            self.peer_public_key_field.hide()
            self.peer_qkd_key_id_label.hide()
            self.peer_qkd_key_id_field.hide()

            self.step_add_peer_status = QLabel("")
            self.step_add_peer_status.setFixedSize(20, 20)

            self.add_peer_button = QPushButton("Add Peer")
            self.add_peer_button.clicked.connect(self.add_peer)
            self.add_peer_button.setEnabled(False)

            self.lock_peers_button = QPushButton("Lock Peers")
            self.lock_peers_button.clicked.connect(self.lock_peers)
            self.lock_peers_button.setEnabled(False)

            self.step_add_peer_layout = QHBoxLayout()
            self.step_add_peer_layout.addWidget(self.step_add_peer_status)
            self.step_add_peer_layout.addWidget(self.add_peer_button)
            self.step_add_peer_layout.addWidget(self.lock_peers_button)
            self.buttons_layout.addLayout(self.step_add_peer_layout)

            self.peers_text = QLabel("")
            self.peers_text.setWordWrap(True)
            self.peers_space = QLabel("")
            self.peers_space.setFixedSize(20, 20)
            self.peers_layout = QHBoxLayout()
            self.peers_layout.addWidget(self.peers_space)
            self.peers_layout.addWidget(self.peers_text)
            self.update_peers_text()
            self.peers_text.hide()
            self.buttons_layout.addLayout(self.peers_layout)

            # server wireguard config
            # fields for internal ip and listen port
            self.server_ip_label = QLabel("Server Internal IP:")
            self.server_ip_field = QLineEdit()
            self.server_port_label = QLabel("Server Listen Port:")
            self.server_port_field = QLineEdit()
            self.server_port_field.setValidator(QIntValidator())
            self.server_port_field.setMaxLength(5)
            self.buttons_layout.addWidget(self.server_ip_label)
            self.buttons_layout.addWidget(self.server_ip_field)
            self.buttons_layout.addWidget(self.server_port_label)
            self.buttons_layout.addWidget(self.server_port_field)
            # hide the fields initially
            self.server_ip_label.hide()
            self.server_ip_field.hide()
            self.server_port_label.hide()
            self.server_port_field.hide()

        # Step: Generate WireGuard config
        self.step_wgconfig_layout = QHBoxLayout()
        self.step_wgconfig_button = QPushButton("Generate WireGuard Config")
        self.step_wgconfig_button.clicked.connect(self.generate_wireguard_config if self.type == "client" else self.generate_wireguard_config_server)
        self.step_wgconfig_button.setEnabled(False)
        self.step_wgconfig_status = QLabel("")
        self.step_wgconfig_status.setFixedSize(20, 20)
        self.step_wgconfig_layout.addWidget(self.step_wgconfig_status)
        self.step_wgconfig_layout.addWidget(self.step_wgconfig_button)
        self.buttons_layout.addLayout(self.step_wgconfig_layout)

        # Step: Open WireGuard
        self.step_wireguard_layout = QHBoxLayout()
        self.step_wireguard_button = QPushButton("Open WireGuard")
        self.step_wireguard_button.clicked.connect(self.open_wireguard)
        self.step_wireguard_button.setEnabled(False)
        self.step_wireguard_status = QLabel("")
        self.step_wireguard_status.setFixedSize(20, 20)
        self.step_wireguard_layout.addWidget(self.step_wireguard_status)
        self.step_wireguard_layout.addWidget(self.step_wireguard_button)
        self.buttons_layout.addLayout(self.step_wireguard_layout)

        if self.type == "client":
            # Step: Launch VideoCall
            self.step_linphone_layout = QHBoxLayout()
            self.step_linphone_button = QPushButton("Launch VideoCall")
            self.step_linphone_button.clicked.connect(self.launch_videocall)
            self.step_linphone_button.setEnabled(False)
            self.step_linphone_status = QLabel("")
            self.step_linphone_status.setFixedSize(20, 20)
            self.step_linphone_layout.addWidget(self.step_linphone_status)
            self.step_linphone_layout.addWidget(self.step_linphone_button)
            self.buttons_layout.addLayout(self.step_linphone_layout)
    
        self.buttons_layout.addStretch(1)

        # configure about section
        self.about_label = QLabel("<b>Quantum VPN:</b> Video conference over post-quantum VPN enhanced by QKD")
        self.about_label.setWordWrap(True)
        self.about_layout.addWidget(self.about_label)
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.about_layout.addWidget(self.line)
        # add two logos to about section
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("Logo.png").scaled(60, 60, Qt.KeepAspectRatio))
        self.logo2 = QLabel()
        # self.logo2.setPixmap(QPixmap("upb.png").scaled(100, 100, Qt.KeepAspectRatio))
        self.logo_layout = QHBoxLayout()
        self.about_copyright = QLabel('© 2024 National University of Science and Technology POLITEHNICA Bucharest')
        self.logo_layout.addWidget(self.logo)
        self.logo_layout.addWidget(self.about_copyright)
        # self.logo_layout.addWidget(self.logo2)
        self.logo_layout.addStretch(1)
        self.about_layout.addLayout(self.logo_layout)

        self.line2 = QFrame()
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.about_layout.addWidget(self.line2)

        self.about_label_website = QLabel('<a href="https://quantum.upb.ro/">Visit Website</a>')
        self.about_label_website.setOpenExternalLinks(True)
        self.about_label_github = QLabel('<a href="https://github.com/QuantumUPB/QKD-App-VPN">GitHub Repository</a>')
        self.about_label_github.setOpenExternalLinks(True)
        self.about_layout.addWidget(self.about_label_website)
        self.about_layout.addWidget(self.about_label_github)
        self.about_layout.addStretch(1)
        # fix about section width
        self.about_label.setFixedWidth(400)
        # set minimum size for the window
        self.setMinimumSize(900, 400)

    def update_peers_text(self):
        text = f"{len(self.peers)} Peers:\n"
        for peer in self.peers:
            text += f"{peer['peer_ip']}: {peer['peer_public_key'][:10]}...\n"
        self.peers_text.setText(text)
        self.peers_text.show()

        QtWidgets.QApplication.instance().processEvents()
        self.adjustSize()

    def add_peer(self):
        # check if the fields are filled
        if not self.peer_ip_field.text() or not self.peer_public_key_field.text() or not self.peer_qkd_key_id_field.text():
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage("Please fill in all fields", 5000)
            return
        
        peer_ip = self.peer_ip_field.text()
        peer_public_key = self.peer_public_key_field.text()
        peer_qkd_key_id = self.peer_qkd_key_id_field.text()

        # get key with id
        try:
            key_data = qkdgkt.qkd_get_key_custom_params('UPB-AP-UPBP', '141.85.241.65:22443', 'upb-ap.crt', 'qkd.key', 'qkd-ca.crt', 'pgpopescu', 'Response', peer_qkd_key_id)
            key_data = json.loads(key_data)
            key = key_data['keys'][0]['key']

            self.peers.append({
                "peer_ip": peer_ip,
                "peer_public_key": peer_public_key,
                "peer_qkd_key_id": peer_qkd_key_id,
                "peer_qkd_key": key
            })

            self.update_peers_text()

            self.peer_ip_field.clear()
            self.peer_public_key_field.clear()
            self.peer_qkd_key_id_field.clear()
        except Exception as e:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage(f"Error acquiring QKD Key: {str(e)}")
            return

    def lock_peers(self):
        # check there are at least 2 peers
        if len(self.peers) < 2:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage("Please add at least 2 peers", 5000)
            return
        
        self.lock_peers_button.setEnabled(False)
        self.add_peer_button.setEnabled(False)
        self.peer_ip_label.hide()
        self.peer_ip_field.hide()
        self.peer_public_key_label.hide()
        self.peer_public_key_field.hide()
        self.peer_qkd_key_id_label.hide()
        self.peer_qkd_key_id_field.hide()

        self.step_add_peer_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
        self.status_bar.showMessage("Peers locked successfully", 5000)
        self.step_wgconfig_button.setEnabled(True)
        # show fields
        self.server_ip_label.show()
        self.server_ip_field.show()
        self.server_port_label.show()
        self.server_port_field.show()

        QtWidgets.QApplication.instance().processEvents()  
        self.adjustSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.type == "client":
            self.set_ellipsized_text(self.public_key_label, self.public_key_str)
            # self.set_ellipsized_text(self.qkd_key_id_label, self.qkd_key_id)
    
    def generate_wireguard_keys(self):
        try:
            # Generate WireGuard private key
            private_key = subprocess.check_output(["wg", "genkey"]).strip()
            # Generate WireGuard public key
            public_key = subprocess.check_output(["wg", "pubkey"], input=private_key).strip()

            # Convert keys to UTF-8 string for display
            private_key_str = private_key.decode('utf-8')
            public_key_str = public_key.decode('utf-8')

            self.private_key = private_key_str
            self.public_key = public_key_str
            self.public_key_str = f"Public Key: {public_key_str}"

            # Display the public key
            # self.public_key_label.setText(self.public_key_str)
            self.set_ellipsized_text(self.public_key_label, self.public_key_str)

            self.step_auth_button.setText("WireGuard Key Pair Generated")
            self.step_auth_button.setEnabled(False)
            self.step_auth_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
            if self.type == "client":
                self.step_qkd_button.setEnabled(True)  # Enable the next step
            else:
                self.peer_ip_label.show()
                self.peer_ip_field.show()
                self.peer_public_key_label.show()
                self.peer_public_key_field.show()
                self.peer_qkd_key_id_label.show()
                self.peer_qkd_key_id_field.show()
                self.add_peer_button.setEnabled(True)
                self.peers_text.show()
                self.lock_peers_button.setEnabled(True)

            self.status_bar.showMessage("WireGuard key pair generated successfully", 5000)
        
            self.copy_button.show()
        except Exception as e:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage(f"Error generating WireGuard key pair: {str(e)}")

    # Function to toggle the key field based on the selected radio button
    def toggle_key_field(self):
        self.paste_key_field.setDisabled(self.radio_fresh_key.isChecked())

    # Function to handle acquiring the key (modified to account for pasted key)
    def acquire_qkd_key(self):
        if self.radio_fresh_key.isChecked():
            # self.step_qkd_status.setText("Acquiring fresh key...")
            try:
                # Placeholder for QKD key acquisition logic
                # Replace with actual call to qkdgkt
                key_data = qkdgkt.qkd_get_key_custom_params('UPB-AP-UPBC', '141.85.241.65:12443', 'upb-ap.crt', 'qkd.key', 'qkd-ca.crt', 'pgpopescu', 'Request')
                key_data = json.loads(key_data)
                key = key_data['keys'][0]['key']
                key_id = key_data['keys'][0]['key_ID']
                self.qkd_key = key
                self.qkd_key_id = key_id
                print(key_id, key)
                QtWidgets.QApplication.instance().processEvents()  
                self.adjustSize()

                self.qkd_key_id_label.setText(f"QKD Key ID: {key_id}")
                self.qkd_key_id_copy_button.show()
            except Exception as e:
                self.status_bar.setStyleSheet("color: red")
                self.status_bar.showMessage(f"Error acquiring QKD Key: {str(e)}")
                return
        elif self.radio_paste_key.isChecked():
            pasted_key = self.paste_key_field.toPlainText().strip()
            self.qkd_key = pasted_key
            # if pasted_key:
            #     # self.step_qkd_status.setText("Key pasted successfully!")
            # else:
            #     # self.step_qkd_status.setText("No key provided.")

        self.step_qkd_button.setText("QKD Key Acquired")
        self.step_qkd_button.setEnabled(False)
        self.step_qkd_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
        self.step_wgconfig_button.setEnabled(True)  # Enable the next step
        self.status_bar.showMessage("QKD Key acquired successfully", 5000)

        # disable paste field
        self.paste_key_field.setDisabled(True)
    
        # show fields
        self.server_public_key_label.show()
        self.server_public_key_field.show()
        self.server_ip_label.show()
        self.server_ip_field.show()
        self.server_port_label.show()
        self.server_port_field.show()
        self.peer_ip_label.show()
        self.peer_ip_field.show()

    def generate_wireguard_config(self):
        # check if the fields are filled
        if not self.server_public_key_field.text() or not self.server_ip_field.text() or not self.server_port_field.text():
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage("Please fill in all fields", 5000)
            return

        try:
            #  WireGuard config generation logic
            # multiline string
            config_data = f"""[Interface]
PrivateKey = {self.private_key}
Address = {self.peer_ip_field.text()}/24

[Peer]
PublicKey = {self.server_public_key_field.text()}
AllowedIPs = 0.0.0.0/0
Endpoint = {self.server_ip_field.text()}:{self.server_port_field.text()}
PresharedKey = {self.qkd_key}
"""
            # open browse to save text file
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save WireGuard Config", "wg_client.conf", "All Files (*);;Text Files (*.conf)", options=options)
            if file_name:
                with open(file_name, 'w') as f:
                    f.write(config_data)
            else:
                return

            self.step_wgconfig_button.setText("WireGuard Config Generated")
            self.step_wgconfig_button.setEnabled(False)
            self.step_wgconfig_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
            self.step_wireguard_button.setEnabled(True)  # Enable the next step
            self.status_bar.setStyleSheet("color: black")
            self.status_bar.showMessage("WireGuard config generated successfully", 5000)

            self.server_public_key_label.hide()
            self.server_public_key_field.hide()
            self.server_ip_label.hide()
            self.server_ip_field.hide()
            self.server_port_label.hide()
            self.server_port_field.hide()
            self.peer_ip_label.hide()
            self.peer_ip_field.hide()

            QtWidgets.QApplication.instance().processEvents()  
            self.adjustSize()
        
        except Exception as e:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage(f"Error generating WireGuard config: {str(e)}")

    def generate_wireguard_config_server(self):
        # check if the fields are filled
        if not self.server_ip_field.text() or not self.server_port_field.text():
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage("Please fill in all fields", 5000)
            return

        try:
            #  WireGuard config generation logic
            # multiline string
            config_data = f"""[Interface]
PrivateKey = {self.private_key}
ListenPort = {self.server_port_field.text()}
Address = {self.server_ip_field.text()}/24
"""
            for peer in self.peers:
                config_data += f"""
[Peer]
PublicKey = {peer['peer_public_key']}
PresharedKey = {peer['peer_qkd_key']}
AllowedIPs = {peer['peer_ip']}/32
"""

            # open browse to save text file
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save WireGuard Config", "wg_server.conf", "All Files (*);;Text Files (*.conf)", options=options)
            if file_name:
                with open(file_name, 'w') as f:
                    f.write(config_data)
            else:
                return

            self.step_wgconfig_button.setText("WireGuard Config Generated")
            self.step_wgconfig_button.setEnabled(False)
            self.step_wgconfig_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
            self.step_wireguard_button.setEnabled(True)  # Enable the next step
            self.status_bar.setStyleSheet("color: black")
            self.status_bar.showMessage("WireGuard config generated successfully", 5000)

            # hide fields
            self.server_ip_field.hide()
            self.server_port_field.hide()
            self.server_ip_label.hide()
            self.server_port_label.hide()

            QtWidgets.QApplication.instance().processEvents()  
            self.adjustSize()
        
        except Exception as e:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage(f"Error generating WireGuard config: {str(e)}")


    def open_wireguard(self):
        try:
            # Open WireGuard application (replace with actual command)
            subprocess.Popen(["wireguard.exe"])

            self.step_wireguard_button.setText("WireGuard is Open - Enable VPN")
            self.step_wireguard_button.setEnabled(False)
            self.step_wireguard_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
            if self.type == "client":
                self.step_linphone_button.setEnabled(True)  # Enable the next step
            self.status_bar.showMessage("WireGuard is open. Please enable the VPN.", 5000)
        except Exception as e:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage(f"Error opening WireGuard: {str(e)}")

    def launch_videocall(self):
        try:
            # Launch Linphone (replace with actual command)
            subprocess.Popen(['C:\\Program Files\\Linphone\\bin\\linphone.exe'])

            self.step_linphone_button.setText("Linphone is Open - Make VideoCall")
            self.step_linphone_button.setEnabled(False)
            self.step_linphone_status.setPixmap(QPixmap("checkmark.png").scaled(20, 20, Qt.KeepAspectRatio))
            self.status_bar.showMessage("Linphone is open. Please make a videocall.", 5000)
        except Exception as e:
            self.status_bar.setStyleSheet("color: red")
            self.status_bar.showMessage(f"Error launching Linphone: {str(e)}")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = QKDApp()
    sys.exit(app.exec_())

