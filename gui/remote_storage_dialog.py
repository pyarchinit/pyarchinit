"""
Remote Storage Configuration Dialog
====================================

Dialog for configuring remote storage backends (Google Drive, Dropbox, S3, etc.)

Author: PyArchInit Team
License: GPL v2
"""

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox,
    QFormLayout, QMessageBox, QTextEdit
)
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsSettings


class RemoteStorageDialog(QDialog):
    """
    Dialog for configuring remote storage backends.

    Allows users to configure credentials for:
    - Google Drive
    - Dropbox
    - Amazon S3 / Cloudflare R2
    - WebDAV
    - HTTP/HTTPS
    - SFTP
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remote Storage Configuration")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.settings = QgsSettings()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            "<b>Remote Storage Configuration</b><br>"
            "Configure credentials for remote storage backends.<br>"
            "You can use remote paths in the Thumbnail and Resize path fields:<br>"
            "<code>gdrive://folder/path</code>, <code>dropbox://folder/path</code>, "
            "<code>s3://bucket/path</code>, etc."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Tab widget for different backends
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Add tabs for each backend
        self.setup_api_storage_tab()  # API Storage first (for File Manager servers)
        self.setup_cloudinary_tab()
        self.setup_gdrive_tab()
        self.setup_dropbox_tab()
        self.setup_s3_tab()
        self.setup_webdav_tab()
        self.setup_http_tab()

        # Buttons
        button_layout = QHBoxLayout()

        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)

        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def setup_cloudinary_tab(self):
        """Set up Cloudinary configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>Cloudinary Setup:</b><br>"
            "1. Sign up at <a href='https://cloudinary.com/'>cloudinary.com</a><br>"
            "2. Go to Dashboard to find your Cloud Name, API Key, and API Secret<br>"
            "3. Enter your credentials below<br><br>"
            "<b>AI Features:</b><br>"
            "Enable auto-tagging to automatically tag images with Google Vision AI.<br>"
            "Use path format: <code>cloudinary://folder/subfolder</code>"
        )
        instructions.setOpenExternalLinks(True)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form_group = QGroupBox("Credentials")
        form_layout = QFormLayout(form_group)

        self.cloudinary_cloud_name = QLineEdit()
        self.cloudinary_cloud_name.setPlaceholderText("Your Cloudinary cloud name")
        form_layout.addRow("Cloud Name:", self.cloudinary_cloud_name)

        self.cloudinary_api_key = QLineEdit()
        self.cloudinary_api_key.setPlaceholderText("API Key from Dashboard")
        form_layout.addRow("API Key:", self.cloudinary_api_key)

        self.cloudinary_api_secret = QLineEdit()
        self.cloudinary_api_secret.setEchoMode(QLineEdit.Password)
        self.cloudinary_api_secret.setPlaceholderText("API Secret from Dashboard")
        form_layout.addRow("API Secret:", self.cloudinary_api_secret)

        self.cloudinary_folder = QLineEdit()
        self.cloudinary_folder.setPlaceholderText("Base folder for uploads (e.g., pyarchinit)")
        form_layout.addRow("Base Folder:", self.cloudinary_folder)

        layout.addWidget(form_group)

        # AI Features group
        ai_group = QGroupBox("AI Features")
        ai_layout = QFormLayout(ai_group)

        self.cloudinary_auto_tagging = QComboBox()
        self.cloudinary_auto_tagging.addItems(["Disabled", "Enabled"])
        self.cloudinary_auto_tagging.setToolTip(
            "When enabled, images are automatically tagged using Google Vision AI.\n"
            "This helps with search and organization of archaeological media."
        )
        ai_layout.addRow("Auto-Tagging:", self.cloudinary_auto_tagging)

        layout.addWidget(ai_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Cloudinary")

    def setup_gdrive_tab(self):
        """Set up Google Drive configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>Google Drive Setup:</b><br>"
            "1. Go to <a href='https://console.cloud.google.com/'>Google Cloud Console</a><br>"
            "2. Create a project and enable Google Drive API<br>"
            "3. Create OAuth 2.0 credentials (Desktop app)<br>"
            "4. Download credentials and extract client_id and client_secret<br>"
            "5. Use <a href='https://developers.google.com/oauthplayground/'>OAuth Playground</a> "
            "to get a refresh token"
        )
        instructions.setOpenExternalLinks(True)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form_group = QGroupBox("Credentials")
        form_layout = QFormLayout(form_group)

        self.gdrive_client_id = QLineEdit()
        self.gdrive_client_id.setPlaceholderText("Client ID from Google Cloud Console")
        form_layout.addRow("Client ID:", self.gdrive_client_id)

        self.gdrive_client_secret = QLineEdit()
        self.gdrive_client_secret.setEchoMode(QLineEdit.Password)
        self.gdrive_client_secret.setPlaceholderText("Client Secret")
        form_layout.addRow("Client Secret:", self.gdrive_client_secret)

        self.gdrive_refresh_token = QLineEdit()
        self.gdrive_refresh_token.setEchoMode(QLineEdit.Password)
        self.gdrive_refresh_token.setPlaceholderText("Refresh Token from OAuth Playground")
        form_layout.addRow("Refresh Token:", self.gdrive_refresh_token)

        layout.addWidget(form_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Google Drive")

    def setup_dropbox_tab(self):
        """Set up Dropbox configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>Dropbox Setup:</b><br>"
            "1. Go to <a href='https://www.dropbox.com/developers/apps'>Dropbox App Console</a><br>"
            "2. Create an app with Full Dropbox access<br>"
            "3. Generate an access token (or use OAuth flow for refresh tokens)"
        )
        instructions.setOpenExternalLinks(True)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form_group = QGroupBox("Credentials")
        form_layout = QFormLayout(form_group)

        self.dropbox_access_token = QLineEdit()
        self.dropbox_access_token.setEchoMode(QLineEdit.Password)
        self.dropbox_access_token.setPlaceholderText("Access Token from Dropbox")
        form_layout.addRow("Access Token:", self.dropbox_access_token)

        self.dropbox_app_key = QLineEdit()
        self.dropbox_app_key.setPlaceholderText("App Key (optional, for refresh tokens)")
        form_layout.addRow("App Key:", self.dropbox_app_key)

        self.dropbox_app_secret = QLineEdit()
        self.dropbox_app_secret.setEchoMode(QLineEdit.Password)
        self.dropbox_app_secret.setPlaceholderText("App Secret (optional)")
        form_layout.addRow("App Secret:", self.dropbox_app_secret)

        layout.addWidget(form_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Dropbox")

    def setup_s3_tab(self):
        """Set up S3/R2 configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>Amazon S3 / Cloudflare R2 Setup:</b><br>"
            "For S3: Get credentials from AWS IAM<br>"
            "For R2: Get credentials from Cloudflare dashboard"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form_group = QGroupBox("Credentials")
        form_layout = QFormLayout(form_group)

        self.s3_access_key = QLineEdit()
        self.s3_access_key.setPlaceholderText("Access Key ID")
        form_layout.addRow("Access Key:", self.s3_access_key)

        self.s3_secret_key = QLineEdit()
        self.s3_secret_key.setEchoMode(QLineEdit.Password)
        self.s3_secret_key.setPlaceholderText("Secret Access Key")
        form_layout.addRow("Secret Key:", self.s3_secret_key)

        self.s3_region = QLineEdit()
        self.s3_region.setPlaceholderText("e.g., us-east-1, eu-west-1")
        self.s3_region.setText("us-east-1")
        form_layout.addRow("Region:", self.s3_region)

        self.s3_endpoint = QLineEdit()
        self.s3_endpoint.setPlaceholderText("Custom endpoint URL (for R2, MinIO, etc.)")
        form_layout.addRow("Endpoint URL:", self.s3_endpoint)

        self.s3_account_id = QLineEdit()
        self.s3_account_id.setPlaceholderText("Cloudflare Account ID (for R2 only)")
        form_layout.addRow("Account ID:", self.s3_account_id)

        layout.addWidget(form_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "S3 / R2")

    def setup_webdav_tab(self):
        """Set up WebDAV configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>WebDAV Setup:</b><br>"
            "Compatible with Nextcloud, ownCloud, and other WebDAV servers.<br>"
            "Use path format: <code>webdav://server.com/remote.php/dav/files/user/folder</code>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form_group = QGroupBox("Credentials")
        form_layout = QFormLayout(form_group)

        self.webdav_username = QLineEdit()
        self.webdav_username.setPlaceholderText("WebDAV username")
        form_layout.addRow("Username:", self.webdav_username)

        self.webdav_password = QLineEdit()
        self.webdav_password.setEchoMode(QLineEdit.Password)
        self.webdav_password.setPlaceholderText("WebDAV password")
        form_layout.addRow("Password:", self.webdav_password)

        layout.addWidget(form_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "WebDAV")

    def setup_http_tab(self):
        """Set up HTTP/HTTPS configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>HTTP/HTTPS Setup:</b><br>"
            "For accessing files via HTTP/HTTPS URLs.<br>"
            "Use with PyArchInit Storage Proxy server or any HTTP file server.<br><br>"
            "<b>Storage Proxy URL example:</b><br>"
            "<code>https://your-server.railway.app/files/</code>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form
        form_group = QGroupBox("Credentials (Optional)")
        form_layout = QFormLayout(form_group)

        self.http_api_key = QLineEdit()
        self.http_api_key.setEchoMode(QLineEdit.Password)
        self.http_api_key.setPlaceholderText("API Key for PyArchInit Storage Proxy")
        form_layout.addRow("API Key:", self.http_api_key)

        self.http_username = QLineEdit()
        self.http_username.setPlaceholderText("HTTP Basic Auth username (alternative)")
        form_layout.addRow("Username:", self.http_username)

        self.http_password = QLineEdit()
        self.http_password.setEchoMode(QLineEdit.Password)
        self.http_password.setPlaceholderText("HTTP Basic Auth password")
        form_layout.addRow("Password:", self.http_password)

        self.http_bearer_token = QLineEdit()
        self.http_bearer_token.setEchoMode(QLineEdit.Password)
        self.http_bearer_token.setPlaceholderText("Bearer token (alternative)")
        form_layout.addRow("Bearer Token:", self.http_bearer_token)

        layout.addWidget(form_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "HTTP/HTTPS")

    def setup_api_storage_tab(self):
        """Set up API Storage (File Manager) configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "<b>API Storage (File Manager)</b><br>"
            "Configure connection to File Manager servers with JWT authentication.<br>"
            "Compatible with servers that use REST API with login/token authentication.<br><br>"
            "<b>Path format:</b> <code>unibo://project_code/folder/path</code><br>"
            "<b>Example:</b> <code>unibo://Al-Khutm/KTM2025/photolog/original</code>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Server Connection group
        server_group = QGroupBox("Server Connection")
        server_layout = QFormLayout(server_group)

        self.api_server_url = QLineEdit()
        self.api_server_url.setPlaceholderText("https://server-address:port")
        self.api_server_url.setToolTip("Server URL (e.g., https://137.204.128.220)")
        server_layout.addRow("Server URL:", self.api_server_url)

        self.api_username = QLineEdit()
        self.api_username.setPlaceholderText("Username for authentication")
        self.api_username.setToolTip("Username for JWT authentication")
        server_layout.addRow("Username:", self.api_username)

        self.api_password = QLineEdit()
        self.api_password.setEchoMode(QLineEdit.Password)
        self.api_password.setPlaceholderText("Password for authentication")
        self.api_password.setToolTip("Password for JWT authentication")
        server_layout.addRow("Password:", self.api_password)

        layout.addWidget(server_group)

        # Default Path group (optional)
        path_group = QGroupBox("Default Path (Optional)")
        path_layout = QFormLayout(path_group)

        self.api_project_code = QLineEdit()
        self.api_project_code.setPlaceholderText("Project code or name")
        self.api_project_code.setToolTip("Default project code to use (e.g., Al-Khutm)")
        path_layout.addRow("Project Code:", self.api_project_code)

        self.api_base_folder = QLineEdit()
        self.api_base_folder.setPlaceholderText("folder/subfolder/path")
        self.api_base_folder.setToolTip("Default folder path within the project")
        path_layout.addRow("Base Folder:", self.api_base_folder)

        layout.addWidget(path_group)

        # SSL Options group
        ssl_group = QGroupBox("SSL Options")
        ssl_layout = QFormLayout(ssl_group)

        self.api_verify_ssl = QComboBox()
        self.api_verify_ssl.addItems(["No (Self-signed certificates)", "Yes (Verify certificates)"])
        self.api_verify_ssl.setToolTip("Disable SSL verification for self-signed certificates")
        ssl_layout.addRow("Verify SSL:", self.api_verify_ssl)

        layout.addWidget(ssl_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "API Storage")

    def load_settings(self):
        """Load settings from QGIS settings"""
        # API Storage
        self.api_server_url.setText(
            self.settings.value("pyarchinit/storage/unibo/server_url", ""))
        self.api_username.setText(
            self.settings.value("pyarchinit/storage/unibo/username", ""))
        self.api_password.setText(
            self.settings.value("pyarchinit/storage/unibo/password", ""))
        self.api_project_code.setText(
            self.settings.value("pyarchinit/storage/unibo/project_code", ""))
        self.api_base_folder.setText(
            self.settings.value("pyarchinit/storage/unibo/base_folder", ""))
        verify_ssl = self.settings.value("pyarchinit/storage/unibo/verify_ssl", "false")
        self.api_verify_ssl.setCurrentIndex(1 if verify_ssl.lower() in ('true', '1', 'yes') else 0)

        # Cloudinary
        self.cloudinary_cloud_name.setText(
            self.settings.value("pyarchinit/storage/cloudinary/cloud_name", ""))
        self.cloudinary_api_key.setText(
            self.settings.value("pyarchinit/storage/cloudinary/api_key", ""))
        self.cloudinary_api_secret.setText(
            self.settings.value("pyarchinit/storage/cloudinary/api_secret", ""))
        self.cloudinary_folder.setText(
            self.settings.value("pyarchinit/storage/cloudinary/folder", ""))
        auto_tag = self.settings.value("pyarchinit/storage/cloudinary/auto_tagging", "false")
        self.cloudinary_auto_tagging.setCurrentIndex(1 if auto_tag.lower() in ('true', '1', 'yes') else 0)

        # Google Drive
        self.gdrive_client_id.setText(
            self.settings.value("pyarchinit/storage/gdrive/client_id", ""))
        self.gdrive_client_secret.setText(
            self.settings.value("pyarchinit/storage/gdrive/client_secret", ""))
        self.gdrive_refresh_token.setText(
            self.settings.value("pyarchinit/storage/gdrive/refresh_token", ""))

        # Dropbox
        self.dropbox_access_token.setText(
            self.settings.value("pyarchinit/storage/dropbox/access_token", ""))
        self.dropbox_app_key.setText(
            self.settings.value("pyarchinit/storage/dropbox/app_key", ""))
        self.dropbox_app_secret.setText(
            self.settings.value("pyarchinit/storage/dropbox/app_secret", ""))

        # S3/R2
        self.s3_access_key.setText(
            self.settings.value("pyarchinit/storage/s3/access_key", ""))
        self.s3_secret_key.setText(
            self.settings.value("pyarchinit/storage/s3/secret_key", ""))
        self.s3_region.setText(
            self.settings.value("pyarchinit/storage/s3/region", "us-east-1"))
        self.s3_endpoint.setText(
            self.settings.value("pyarchinit/storage/s3/endpoint", ""))
        self.s3_account_id.setText(
            self.settings.value("pyarchinit/storage/s3/account_id", ""))

        # WebDAV
        self.webdav_username.setText(
            self.settings.value("pyarchinit/storage/webdav/username", ""))
        self.webdav_password.setText(
            self.settings.value("pyarchinit/storage/webdav/password", ""))

        # HTTP
        self.http_api_key.setText(
            self.settings.value("pyarchinit/storage/http/api_key", ""))
        self.http_username.setText(
            self.settings.value("pyarchinit/storage/http/username", ""))
        self.http_password.setText(
            self.settings.value("pyarchinit/storage/http/password", ""))
        self.http_bearer_token.setText(
            self.settings.value("pyarchinit/storage/http/bearer_token", ""))

    def save_settings(self):
        """Save settings to QGIS settings"""
        # API Storage
        self.settings.setValue("pyarchinit/storage/unibo/server_url",
                               self.api_server_url.text())
        self.settings.setValue("pyarchinit/storage/unibo/username",
                               self.api_username.text())
        self.settings.setValue("pyarchinit/storage/unibo/password",
                               self.api_password.text())
        self.settings.setValue("pyarchinit/storage/unibo/project_code",
                               self.api_project_code.text())
        self.settings.setValue("pyarchinit/storage/unibo/base_folder",
                               self.api_base_folder.text())
        self.settings.setValue("pyarchinit/storage/unibo/verify_ssl",
                               "true" if self.api_verify_ssl.currentIndex() == 1 else "false")

        # Cloudinary
        self.settings.setValue("pyarchinit/storage/cloudinary/cloud_name",
                               self.cloudinary_cloud_name.text())
        self.settings.setValue("pyarchinit/storage/cloudinary/api_key",
                               self.cloudinary_api_key.text())
        self.settings.setValue("pyarchinit/storage/cloudinary/api_secret",
                               self.cloudinary_api_secret.text())
        self.settings.setValue("pyarchinit/storage/cloudinary/folder",
                               self.cloudinary_folder.text())
        self.settings.setValue("pyarchinit/storage/cloudinary/auto_tagging",
                               "true" if self.cloudinary_auto_tagging.currentIndex() == 1 else "false")

        # Google Drive
        self.settings.setValue("pyarchinit/storage/gdrive/client_id",
                               self.gdrive_client_id.text())
        self.settings.setValue("pyarchinit/storage/gdrive/client_secret",
                               self.gdrive_client_secret.text())
        self.settings.setValue("pyarchinit/storage/gdrive/refresh_token",
                               self.gdrive_refresh_token.text())

        # Dropbox
        self.settings.setValue("pyarchinit/storage/dropbox/access_token",
                               self.dropbox_access_token.text())
        self.settings.setValue("pyarchinit/storage/dropbox/app_key",
                               self.dropbox_app_key.text())
        self.settings.setValue("pyarchinit/storage/dropbox/app_secret",
                               self.dropbox_app_secret.text())

        # S3/R2
        self.settings.setValue("pyarchinit/storage/s3/access_key",
                               self.s3_access_key.text())
        self.settings.setValue("pyarchinit/storage/s3/secret_key",
                               self.s3_secret_key.text())
        self.settings.setValue("pyarchinit/storage/s3/region",
                               self.s3_region.text())
        self.settings.setValue("pyarchinit/storage/s3/endpoint",
                               self.s3_endpoint.text())
        self.settings.setValue("pyarchinit/storage/s3/account_id",
                               self.s3_account_id.text())

        # WebDAV
        self.settings.setValue("pyarchinit/storage/webdav/username",
                               self.webdav_username.text())
        self.settings.setValue("pyarchinit/storage/webdav/password",
                               self.webdav_password.text())

        # HTTP
        self.settings.setValue("pyarchinit/storage/http/api_key",
                               self.http_api_key.text())
        self.settings.setValue("pyarchinit/storage/http/username",
                               self.http_username.text())
        self.settings.setValue("pyarchinit/storage/http/password",
                               self.http_password.text())
        self.settings.setValue("pyarchinit/storage/http/bearer_token",
                               self.http_bearer_token.text())

        QMessageBox.information(self, "Settings Saved",
                                "Remote storage settings have been saved.")
        self.accept()

    def test_connection(self):
        """Test connection to the currently selected backend"""
        current_tab = self.tab_widget.currentIndex()
        tab_name = self.tab_widget.tabText(current_tab)

        # Special handling for API Storage tab (index 0)
        if current_tab == 0:  # API Storage
            self._test_api_storage_connection()
            return

        try:
            from modules.storage import StorageManager, CredentialsManager
            from modules.storage.base_backend import StorageType

            # Save current settings temporarily
            self.save_settings_temp()

            creds_manager = CredentialsManager()
            storage = StorageManager(credentials_manager=creds_manager)

            # Test based on current tab (shifted by 1 due to API Storage at index 0)
            if current_tab == 1:  # Cloudinary
                storage_type = StorageType.CLOUDINARY
                test_path = "cloudinary://test"
            elif current_tab == 2:  # Google Drive
                storage_type = StorageType.GOOGLE_DRIVE
                test_path = "gdrive://test"
            elif current_tab == 3:  # Dropbox
                storage_type = StorageType.DROPBOX
                test_path = "dropbox://test"
            elif current_tab == 4:  # S3
                storage_type = StorageType.S3
                bucket = "test-bucket"
                test_path = f"s3://{bucket}"
            elif current_tab == 5:  # WebDAV
                storage_type = StorageType.WEBDAV
                test_path = "webdav://test"
            else:  # HTTP (index 6)
                storage_type = StorageType.HTTP
                test_path = "https://example.com"

            # Check if credentials are available
            if not creds_manager.has_credentials(storage_type):
                missing = creds_manager.get_missing_credentials(storage_type)
                QMessageBox.warning(
                    self, "Missing Credentials",
                    f"Missing required credentials for {tab_name}:\n" +
                    "\n".join(f"- {m}" for m in missing)
                )
                return

            QMessageBox.information(
                self, "Credentials Found",
                f"Credentials for {tab_name} are configured.\n"
                "Full connection test requires a valid path."
            )

        except ImportError as e:
            QMessageBox.warning(
                self, "Module Not Found",
                f"Storage module not available: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error",
                f"Error testing {tab_name} connection:\n{str(e)}"
            )

    def _test_api_storage_connection(self):
        """Test connection to API Storage (File Manager) server"""
        server_url = self.api_server_url.text().strip()
        username = self.api_username.text().strip()
        password = self.api_password.text()

        # Validate required fields
        if not server_url:
            QMessageBox.warning(self, "Missing Field", "Server URL is required.")
            return
        if not username:
            QMessageBox.warning(self, "Missing Field", "Username is required.")
            return
        if not password:
            QMessageBox.warning(self, "Missing Field", "Password is required.")
            return

        try:
            from modules.storage.unibo_filemanager_backend import UniboFileManagerBackend

            # Build the base path from project code and folder
            project_code = self.api_project_code.text().strip()
            base_folder = self.api_base_folder.text().strip()

            if project_code and base_folder:
                base_path = f"{project_code}/{base_folder}"
            elif project_code:
                base_path = project_code
            else:
                base_path = ""

            # Create credentials dict
            credentials = {
                'username': username,
                'password': password,
                'server_url': server_url
            }

            # Create backend and test connection
            backend = UniboFileManagerBackend(base_path=base_path, credentials=credentials)

            if backend.connect():
                # Build success message
                msg = "Connection successful!\n\n"
                if backend._project_id:
                    msg += f"Project ID: {backend._project_id}\n"
                if backend._folder_id:
                    msg += f"Folder ID: {backend._folder_id}\n"

                # Try to list files
                try:
                    files = backend.list()
                    msg += f"\nFound {len(files)} items in the folder."
                except Exception:
                    pass

                backend.disconnect()
                QMessageBox.information(self, "Connection Test", msg)
            else:
                QMessageBox.warning(
                    self, "Connection Failed",
                    "Could not connect to the server.\n"
                    "Please check your credentials and server URL."
                )

        except ImportError as e:
            QMessageBox.warning(
                self, "Module Not Found",
                f"API Storage module not available: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error",
                f"Error testing connection:\n{str(e)}"
            )

    def save_settings_temp(self):
        """Temporarily save settings for testing"""
        # This saves settings immediately so the credentials manager can read them
        self.save_settings.__wrapped__(self) if hasattr(self.save_settings, '__wrapped__') else None

        # Actually save the current values
        settings = QgsSettings()

        # API Storage
        settings.setValue("pyarchinit/storage/unibo/server_url",
                          self.api_server_url.text())
        settings.setValue("pyarchinit/storage/unibo/username",
                          self.api_username.text())
        settings.setValue("pyarchinit/storage/unibo/password",
                          self.api_password.text())
        settings.setValue("pyarchinit/storage/unibo/project_code",
                          self.api_project_code.text())
        settings.setValue("pyarchinit/storage/unibo/base_folder",
                          self.api_base_folder.text())
        settings.setValue("pyarchinit/storage/unibo/verify_ssl",
                          "true" if self.api_verify_ssl.currentIndex() == 1 else "false")

        # Cloudinary
        settings.setValue("pyarchinit/storage/cloudinary/cloud_name",
                          self.cloudinary_cloud_name.text())
        settings.setValue("pyarchinit/storage/cloudinary/api_key",
                          self.cloudinary_api_key.text())
        settings.setValue("pyarchinit/storage/cloudinary/api_secret",
                          self.cloudinary_api_secret.text())
        settings.setValue("pyarchinit/storage/cloudinary/folder",
                          self.cloudinary_folder.text())
        settings.setValue("pyarchinit/storage/cloudinary/auto_tagging",
                          "true" if self.cloudinary_auto_tagging.currentIndex() == 1 else "false")

        # Google Drive
        settings.setValue("pyarchinit/storage/gdrive/client_id",
                          self.gdrive_client_id.text())
        settings.setValue("pyarchinit/storage/gdrive/client_secret",
                          self.gdrive_client_secret.text())
        settings.setValue("pyarchinit/storage/gdrive/refresh_token",
                          self.gdrive_refresh_token.text())

        # Dropbox
        settings.setValue("pyarchinit/storage/dropbox/access_token",
                          self.dropbox_access_token.text())

        # S3
        settings.setValue("pyarchinit/storage/s3/access_key",
                          self.s3_access_key.text())
        settings.setValue("pyarchinit/storage/s3/secret_key",
                          self.s3_secret_key.text())
        settings.setValue("pyarchinit/storage/s3/region",
                          self.s3_region.text())

        # WebDAV
        settings.setValue("pyarchinit/storage/webdav/username",
                          self.webdav_username.text())
        settings.setValue("pyarchinit/storage/webdav/password",
                          self.webdav_password.text())

        # HTTP
        settings.setValue("pyarchinit/storage/http/api_key",
                          self.http_api_key.text())
        settings.setValue("pyarchinit/storage/http/username",
                          self.http_username.text())
        settings.setValue("pyarchinit/storage/http/password",
                          self.http_password.text())
        settings.setValue("pyarchinit/storage/http/bearer_token",
                          self.http_bearer_token.text())
