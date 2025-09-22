# dns_changer_app.py

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
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.dns_providers = {
            "Cloudflare": ["1.1.1.1", "1.0.0.1"],
            "Google": ["8.8.8.8", "8.8.4.4"],
            "Quad9": ["9.9.9.9", "149.112.112.112"],
            "OpenDNS": ["208.67.222.222", "208.67.220.220"],
            "AdGuard": ["94.140.14.14", "94.140.15.15"]
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

        title_label = ttk.Label(main_frame, text="Fastest DNS Changer", font=("Helvetica", 16, "bold"), bootstyle="danger")
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
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Buttons for changing DNS
        ttk.Button(button_frame, text="Set Cloudflare", command=lambda: self.apply_dns("Cloudflare"), bootstyle="success").pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Set Google", command=lambda: self.apply_dns("Google"), bootstyle="primary").pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Set Quad9", command=lambda: self.apply_dns("Quad9"), bootstyle="info").pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Set OpenDNS", command=lambda: self.apply_dns("OpenDNS"), bootstyle="secondary").pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Set AdGuard", command=lambda: self.apply_dns("AdGuard"), bootstyle="warning").pack(fill=tk.X, pady=5)
        
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
        
        success = set_dns(dns_ips[0], dns_ips[1])
        
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
