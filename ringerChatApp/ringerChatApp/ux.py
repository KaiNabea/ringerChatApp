# Library imports
import socket              # for network communication
import ssl                 # for secure (TLS) connections
import threading           # to handle background message receiving
import tkinter as tk       # GUI framework
from tkinter import scrolledtext, messagebox  # UI widgets
import json
import os
import sys

# Import fixes to run file from project root
# Adds the project root folder to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from networking.packet import create_packet, read_packet
from networking.encryption import text_to_binary, binary_to_text


# Packet helper 
def build_packet(sender: str, sender_ip: str, sender_mac: str,
                 receiver: str, port: int, message: str) -> str:
    """
    Builds a packet for sending messages.
    Converts the message into binary before packaging it.
    """
    return create_packet(
        sender=sender,
        receiver=receiver,
        message=text_to_binary(message),  # encrypt/encode message
        ip=sender_ip,
        mac=sender_mac,
        port=port,
    )


# Network layer 
class ChatConnection:
    """
    Handles all networking logic:
    - Connecting to server
    - Sending messages
    - Receiving messages in background
    """

    def __init__(self, host: str, port: int, username: str, ca_cert: str | None):
        self.host     = host
        self.port     = port
        self.username = username
        self.ca_cert  = ca_cert
        self.sock     = None

        # Callback functions set by UI
        self._on_message  = None
        self._on_error    = None

    def set_callbacks(self, on_message, on_error):
        """Allows UI to register callback functions."""
        self._on_message = on_message
        self._on_error   = on_error

    def connect(self):
        """
        Establish a TLS connection to the server.
        Starts a background thread to listen for messages.
        """
        try:
            # Create TCP connection
            raw = socket.create_connection((self.host, self.port), timeout=100)
            
            # Create SSL context (secure connection)
            context = ssl.create_default_context()

            if self.ca_cert and os.path.exists(self.ca_cert):
                # Use trusted certificate if provided
                context.load_verify_locations(self.ca_cert)
            else:
                # Development mode (no cert validation)
                context.check_hostname = False
                context.verify_mode    = ssl.CERT_NONE
            
            # Wrap socket with SSL
            self.sock = context.wrap_socket(raw, server_hostname=self.host)
            
            # Send username to server immediately after connecting
            self.sock.sendall(self.username.encode())
            
            # Start receiving messages in background thread
            t = threading.Thread(target=self._receive_loop, daemon=True)
            t.start()
            return True
            
        except ConnectionRefusedError:
            raise Exception(f"Cannot connect to {self.host}:{self.port} - Server not running")
        except Exception as e:
            raise Exception(f"Connection failed: {e}")

    def send(self, receiver: str, message: str):
        """
        Sends a message to a specific receiver.
        """
        if not self.sock:
            return

        try:
            # Get local connection info
            local_ip, local_port = self.sock.getsockname()
            local_mac = "00:00:00:00:00:00"  # Placeholder MAC address

            # Build packet
            packet = build_packet(
                sender=self.username,
                sender_ip=local_ip,
                sender_mac=local_mac,
                receiver=receiver,
                port=local_port,
                message=message,
            )

            # Send encoded packet
            self.sock.sendall(packet.encode())

        except Exception as e:
            if self._on_error:
                self._on_error(str(e))

    def disconnect(self):
        """Closes the connection safely."""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _receive_loop(self):
        """
        Runs in a background thread.
        Continuously listens for incoming messages.
        """
        while self.sock:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                # Pass received data to UI via callback
                if self._on_message:
                    self._on_message(data.decode())

            except Exception as e:
                if self._on_error:
                    self._on_error(str(e))
                break


# GUI Styling  
DARK_BG   = "#1e1e2e"
PANEL_BG  = "#2a2a3d"
ACCENT    = "#7c6af7"
ACCENT_HV = "#9d8fff"
TEXT      = "#e0e0f0"
MUTED     = "#888899"
BUBBLE_ME = "#3d3560"
BUBBLE_RX = "#2e2e44"

# Fonts used throughout UI
FONT_MAIN = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_MONO = ("Consolas", 10)


# Login Screen 
class LoginScreen(tk.Frame):
    """
    First screen shown to user.
    Collects connection details (host, port, username, cert).
    """

    def __init__(self, master, on_connect):
        super().__init__(master, bg=DARK_BG)
        self.on_connect = on_connect
        self._build()

    def _build(self):
        """Builds the login UI layout."""
        self.pack(fill="both", expand=True)

        # Center card UI
        card = tk.Frame(self, bg=PANEL_BG, padx=36, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(card, text="Ringer", font=("Segoe UI", 22, "bold"),
                 fg=ACCENT, bg=PANEL_BG).grid(row=0, column=0, columnspan=2)

        # Input fields
        fields = [
            ("Server host", "localhost"),
            ("Port", "5000"),
            ("Username", ""),
            ("CA cert path (leave blank for dev)", ""),
        ]

        self._entries = {}

        # Create input boxes dynamically
        for i, (label, default) in enumerate(fields):
            tk.Label(card, text=label).grid(row=i+2, column=0)
            e = tk.Entry(card)
            e.insert(0, default)
            e.grid(row=i+2, column=1)
            self._entries[label] = e

        # Connect button
        tk.Button(card, text="Connect", command=self._submit).grid(
            row=len(fields)+2, column=0, columnspan=2
        )

    def _submit(self):
        """
        Validates input and calls the connect callback.
        """
        host     = self._entries["Server host"].get().strip()
        port     = self._entries["Port"].get().strip()
        username = self._entries["Username"].get().strip()
        ca_cert  = self._entries["CA cert path (leave blank for dev)"].get().strip() or None

        if not host or not username:
            messagebox.showerror("Missing fields", "Host and username are required.")
            return

        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Invalid port", "Port must be a number.")
            return

        # Pass values to App
        self.on_connect(host, port, username, ca_cert)


# Chat Screen
class ChatScreen(tk.Frame):
    """
    Main messaging interface after connecting.
    Handles displaying and sending messages.
    """

    def __init__(self, master, connection: ChatConnection, on_disconnect):
        super().__init__(master, bg=DARK_BG)
        self.conn          = connection
        self.on_disconnect = on_disconnect
        self._build()

        # Register callbacks from network layer
        self.conn.set_callbacks(
            on_message=self._handle_incoming,
            on_error=self._handle_error,
        )

    def _send(self):
        """
        Sends message from input box.
        """
        receiver = self.receiver_entry.get().strip()
        message  = self.message_entry.get().strip()

        if not receiver or not message:
            return

        self.conn.send(receiver, message)

        # Show message in UI
        self._append(f"You → {receiver}: {message}", "me")
        self.message_entry.delete(0, "end")

    def _handle_incoming(self, raw: str):
        """
        Handles incoming messages from network thread.
        Must be scheduled on main thread (Tkinter requirement).
        """
        self.after(0, lambda: self._parse_and_display(raw))

    def _parse_and_display(self, raw: str):
        """
        Converts packet back into readable message.
        """
        try:
            packet  = read_packet(raw)
            sender  = packet.get("sender", "unknown")
            message = binary_to_text(packet["message"])

            self._append(f"{sender}: {message}", "them")

        except Exception as e:
            self._append(f"Error parsing message: {e}", "system")

    def _handle_error(self, error: str):
        """Displays connection errors."""
        self.after(0, lambda: self._append(f"Connection error: {error}", "system"))

    def _append(self, text: str, tag: str):
        """Adds a message to chat history."""
        self.history.config(state="normal")
        self.history.insert("end", f" {text} \n", tag)
        self.history.config(state="disabled")
        self.history.see("end")

    def _disconnect(self):
        """Disconnect button handler."""
        self.conn.disconnect()
        self.on_disconnect()


# App Controller 
class App(tk.Tk):
    """
    Main application controller.
    Handles switching between Login and Chat screens.
    """

    def __init__(self):
        super().__init__()
        self.title("Ringer")
        self.geometry("780x560")
        self.configure(bg=DARK_BG)

        self._current = None
        self._show_login()

    def _show_login(self):
        """Displays login screen."""
        if self._current:
            self._current.destroy()
        self._current = LoginScreen(self, on_connect=self._connect)

    def _connect(self, host, port, username, ca_cert):
        """
        Creates connection and switches to chat screen.
        """
        conn = ChatConnection(host, port, username, ca_cert)

        try:
            conn.connect()
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))
            return

        if self._current:
            self._current.destroy()

        self._current = ChatScreen(self, conn, on_disconnect=self._show_login)


# Entry point 
if __name__ == "__main__":
    # Start the GUI application
    App().mainloop()