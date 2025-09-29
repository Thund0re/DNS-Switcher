#!/usr/bin/env python3
# dns_switcher.py

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import platform
import re
import os
import sys

# Import ttkbootstrap for modern, themed widgets
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledFrame

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

def get_platform():
    """Returns the current operating system."""
    return platform.system()

def get_current_dns():
    """
    Gets the current DNS servers for the active network interface.
    Returns a tuple of (primary, secondary) DNS servers.
    """
    os_name = get_platform()
    try:
        if os_name == "Windows":
            result = subprocess.run(['powershell', 'Get-DnsClientServerAddress -InterfaceAlias * | Select-Object -ExpandProperty ServerAddresses'], capture_output=True, text=True)
            dns_list = [line.strip() for line in result.stdout.splitlines() if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', line.strip())]
        elif os_name == "Darwin":  # macOS
            result = subprocess.run(['networksetup', '-getdnsservers', 'Wi-Fi'], capture_output=True, text=True)
            dns_list = [line.strip() for line in result.stdout.splitlines() if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', line.strip())]
        else:  # Linux
            result = subprocess.run(['cat', '/etc/resolv.conf'], capture_output=True, text=True)
            dns_list = [line.split()[1] for line in result.stdout.splitlines() if line.startswith('nameserver') and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', line.split()[1])]
        
        primary = dns_list[0] if len(dns_list) > 0 else "Not Found"
        secondary = dns_list[1] if len(dns_list) > 1 else "Not Found"
        
        return primary, secondary
    except Exception as e:
        Messagebox.show_error("Error", f"Failed to get current DNS servers: {e}")
        return "Error", "Error"

def set_dns(primary_dns, secondary_dns):
    """
    Sets the DNS servers based on the operating system.
    This function requires administrative/root privileges.
    """
    os_name = get_platform()
    try:
        # Check for administrative privileges on Unix-like systems
        if os_name in ["Linux", "Darwin"]:
            if os.getuid() != 0:
                Messagebox.show_warning("Permission Required", "This application needs to be run with root privileges (sudo) to change DNS settings.")
                return False
        
        # Build command based on OS
        if os_name == "Windows":
            command = f'netsh interface ipv4 set dnsservers name="Wi-Fi" static {primary_dns} primary && netsh interface ipv4 add dnsservers name="Wi-Fi" {secondary_dns} index=2'
        elif os_name == "Darwin":  # macOS
            command = f'networksetup -setdnsservers "Wi-Fi" {primary_dns} {secondary_dns}'
        else:  # Linux
            command = f'nmcli dev mod "eth0" ipv4.dns "{primary_dns},{secondary_dns}"'
            # Note: For Linux, the network interface 'eth0' might vary. You may need to change this.
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        # This error is expected if not running as admin/root on Windows
        Messagebox.show_error("Error", f"Failed to set DNS: {e.stderr}\n\nPlease ensure you run this application as an administrator.")
        return False
    except Exception as e:
        Messagebox.show_error("An unexpected error occurred", f"An unexpected error occurred: {e}")
        return False

def run_as_admin():
    """
    Relaunches the script with administrator/root privileges.
    """
    os_name = get_platform()
    if os_name == "Windows":
        try:
            import ctypes
            # Check if we are already running as admin
            if ctypes.windll.shell32.IsUserAnAdmin():
                return
            
            # Re-launch the script as admin
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit(0)
        except Exception as e:
            Messagebox.show_error("Error", f"Could not relaunch as administrator: {e}")
    else:
        # On Linux/macOS, users need to use sudo manually
        if os.getuid() != 0:
            Messagebox.show_warning("Permission Required", "This application needs to be run with root privileges (sudo) to change DNS settings. Please run it as 'sudo python3 dns_changer_app.py' or 'sudo ./dns_changer_app.py' from the terminal.")

class DNSApp(ttk.Window):
    def __init__(self):
        # Initialize the ttkbootstrap window with a theme
        super().__init__(themename="darkly")
        self.title("Fastest DNS Changer")
        self.geometry("550x750")
        self.resizable(False, False)
        
        self.dns_providers = {
            "Cloudflare": ["1.1.1.1", "1.0.0.1"],
            "Google": ["8.8.8.8", "8.8.4.4"],
            "Quad9": ["9.9.9.9", "149.112.112.112"],
            "OpenDNS": ["208.67.222.222", "208.67.220.220"],
            "AdGuard": ["94.140.14.14", "94.140.15.15"],
            "CleanBrowsing": ["185.228.168.9", "185.228.169.9"],
            "Control D": ["76.76.2.0", "76.76.10.0"],
            "DNS.SB": ["185.222.222.222", "45.11.45.11"],
            "DNS0.EU": ["193.110.81.254", "185.253.5.254"],
            "Mullvad": ["194.242.2.2"],
            "UncensoredDNS": ["91.239.100.100", "89.233.43.71"],
            "Comcast": ["75.75.75.75", "75.75.76.76"],
            "Verisign": ["64.6.64.6", "64.6.65.6"],
            "Yandex": ["77.88.8.8", "77.88.8.1"],
            "Freifunk München": ["5.1.66.255", "185.150.99.255"],
            "French Data Network": ["80.67.169.12", "80.67.169.40"],
            "NWPS.fi": ["95.217.11.63", "135.181.103.31"],
            "Alternate DNS": ["76.76.19.19", "76.223.100.101"],
            "Digitalcourage": ["5.9.164.112"],
            "Njalla": ["95.215.19.53"],
            "CMRG DNS": ["199.58.83.33"],
            "Lightning Wire Labs": ["81.3.27.54"],
            "Applied Privacy": ["146.255.56.98"],
            "Digitale Gesellschaft": ["185.95.218.42", "185.95.218.43"],
            "FlokiNET": ["185.246.188.51", "185.247.225.17"],
            "GetDNS": ["185.49.141.37"],
            "DNS4EU": ["86.54.11.100", "86.54.11.200"],
            "LinuxPatch": ["45.80.1.6"],
            "Restena Foundation": ["158.64.1.29"]
        }
        
        self.current_primary_dns = tk.StringVar(self)
        self.current_secondary_dns = tk.StringVar(self)
        self.initial_dns = None
        
        self.create_widgets()
        self.refresh_dns_display()
        
    def create_widgets(self):
        """Creates and places all GUI widgets."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Fast DNS Changer", font=("Helvetica", 16, "bold"), bootstyle="light")
        title_label.pack(pady=(0, 20))

        # Current DNS display with updated styling
        current_frame = ttk.Labelframe(main_frame, text="Current DNS Servers", padding=10, bootstyle="info")
        current_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(current_frame, text="Primary:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        primary_label = ttk.Label(current_frame, textvariable=self.current_primary_dns)
        primary_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(current_frame, text="Secondary:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        secondary_label = ttk.Label(current_frame, textvariable=self.current_secondary_dns)
        secondary_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # DNS Providers Frame
        providers_frame = ttk.Labelframe(main_frame, text="DNS Providers", padding=10, bootstyle="info")
        providers_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

        # Scrollable frame for the buttons
        scroll_frame = ScrolledFrame(providers_frame, autohide=True)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        # Create a grid of buttons for all DNS providers
        COLUMNS = 3
        row, col = 0, 0
        for provider_name in self.dns_providers:
            button = ttk.Button(scroll_frame, text=provider_name, command=lambda p=provider_name: self.apply_dns(p), bootstyle="outline")
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col >= COLUMNS:
                col = 0
                row += 1
        
        # Reset button
        reset_button = ttk.Button(main_frame, text="Reset to Default ISP DNS", command=self.reset_dns, bootstyle="success")
        reset_button.pack(fill=tk.X, pady=(20, 5))
        
        # Exit button
        exit_button = ttk.Button(main_frame, text="Exit", command=self.destroy, bootstyle="light")
        exit_button.pack(fill=tk.X, pady=5)
        
        # Log area
        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=6)
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)
        self.log("Ready to change DNS settings.")
    
    def log(self, message):
        """Adds a message to the log area."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def refresh_dns_display(self):
        """Refreshes the displayed current DNS servers."""
        primary, secondary = get_current_dns()
        self.current_primary_dns.set(primary)
        self.current_secondary_dns.set(secondary)
        self.log(f"Current DNS: Primary={primary}, Secondary={secondary}")

    def apply_dns(self, provider_name):
        """Applies the selected DNS settings."""
        if not self.initial_dns:
            self.initial_dns = get_current_dns()
        
        dns_ips = self.dns_providers[provider_name]
        
        self.log(f"Attempting to set DNS to {provider_name}...")
        
        # Handle providers with only one DNS server
        primary_dns = dns_ips[0]
        secondary_dns = dns_ips[1] if len(dns_ips) > 1 else primary_dns
        
        success = set_dns(primary_dns, secondary_dns)
        
        if success:
            Messagebox.show_info("Success", f"DNS has been set to {provider_name} successfully!")
            self.refresh_dns_display()
        else:
            self.log("Failed to change DNS. Please ensure you have administrative privileges.")

    def reset_dns(self):
        """Resets the DNS to the initial, default settings."""
        if not self.initial_dns:
            self.log("No initial DNS recorded. Cannot reset.")
            Messagebox.show_warning("Cannot Reset", "The app was unable to determine your initial DNS. Please try again or reset manually.")
            return

        primary_dns, secondary_dns = self.initial_dns
        
        self.log("Attempting to reset DNS to default...")
        
        if set_dns(primary_dns, secondary_dns):
            Messagebox.show_info("Success", "DNS has been reset to default successfully!")
            self.refresh_dns_display()
        else:
            self.log("Failed to reset DNS. Please ensure you have administrative privileges.")

if __name__ == "__main__":
    run_as_admin()
    app = DNSApp()
    app.mainloop()
