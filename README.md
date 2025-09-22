# DNS-Switcher
App to switch your local DNS to Cloudflar, Google etc..


***

## Fastest DNS Changer

### Overview

**Fastest DNS Changer** is a cross-platform, desktop-based application that allows you to quickly switch your system’s DNS servers between popular providers. It provides a user-friendly interface for Windows, macOS, and Linux, and is especially useful for developers, network administrators, and privacy-conscious users who want to experiment with different DNS services.

***

### Features

- **Detects current DNS** settings (primary and secondary) and displays them in real time.
- **Sets DNS** to popular providers via one-click: Cloudflare, Google, Quad9, OpenDNS, AdGuard.
- **Resets DNS** to your original (ISP) settings.
- **Supports Windows, macOS, and Linux** (with platform-specific system commands).
- **Modern, themed UI** using ttkbootstrap for a visually appealing and responsive interface.
- **Logging** of all actions and results directly in the app window.
- **Permission reminders** for admin/root access when required.

***

### Supported DNS Providers

| Provider   | Primary DNS      | Secondary DNS    |
|------------|------------------|------------------|
| Cloudflare | 1.1.1.1          | 1.0.0.1          |
| Google     | 8.8.8.8          | 8.8.4.4          |
| Quad9      | 9.9.9.9          | 149.112.112.112  |
| OpenDNS    | 208.67.222.222   | 208.67.220.220   |
| AdGuard    | 94.140.14.14     | 94.140.15.15     |

***

### System Requirements

- **Python 3.6+**
- **tkinter** (usually included with Python)
- **ttkbootstrap** (`pip install ttkbootstrap`)

***

### Installation

1. **Clone or download** the repository.
2. **Install dependencies**:
   ```bash
   pip install ttkbootstrap
   ```
3. **Run the application**:
   ```bash
   python dns_changer_app.py
   ```
   - **On Windows:** The app will attempt to relaunch itself with administrative privileges if not already running as admin.
   - **On macOS/Linux:** You must run the script as root:  
     ```bash
     sudo python3 dns_changer_app.py
     ```

***

### Usage Instructions

1. **Launch the app.** You’ll see your current DNS servers displayed.
2. **Click a provider button** (e.g., “Set Cloudflare”) to change your DNS instantly.
3. **To reset** to your original (ISP) DNS, click “Reset to Default ISP DNS”.
4. **All actions are logged** in the text area at the bottom of the window.
5. **Exit** the app using the “Exit” button.

***

### Permissions & Security

- **Changing DNS requires administrator (Windows) or root (macOS/Linux) privileges.** The app will prompt you if you don’t have the required permissions.
- **On Linux:** The app assumes your primary network interface is named `eth0`. If yours is different (e.g., `wlan0` or `enp0s3`), you’ll need to modify the script accordingly.
- **No internet connection is required to change DNS** (the app only modifies local network settings).
- **The app does not collect, store, or transmit any user data.**

***

### Limitations

- **Linux interface names:** The script currently hard-codes `eth0` for Linux. Adjust if your system uses a different interface name.
- **No DHCP support:** The app sets static DNS. If your network uses DHCP (automatic DNS assignment), the changes may be overwritten when your connection renews.
- **UI only:** There is no command-line interface or automation API.
- **Manual reset:** If you close the app before resetting, your original DNS may not be restored automatically.

***

### Troubleshooting

- **“Failed to change DNS”** usually means you did not run the app as administrator/root.
- **“Cannot Reset”** appears if the app couldn’t record your original DNS settings. In this case, reset your DNS manually.
- **Logs are your friend:** Check the log area for detailed error messages.

***

### Customization

- **UI Theme:** The app uses ttkbootstrap’s “darkly” theme by default. You can change this by modifying the `themename` parameter in the `DNSApp` class.
- **Adding Providers:** Edit the `dns_providers` dictionary in the `DNSApp` class to add or remove DNS services.

***

### Contributing

Feel free to fork and improve the code. Pull requests are welcome—especially for better cross-platform compatibility, additional features, or UI enhancements.

***

**Fastest DNS Changer** provides a simple, fast, and visually modern way to manage your DNS settings across operating systems. Whether you’re optimizing for speed, privacy, or content filtering, this app puts you in control with just a few clicks.
