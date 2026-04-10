import socket
import ssl
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import json

from ringerChatApp.networking.packet import create_packet, read_packet
from ringerChatApp.networking.encryption import text_to_binary, binary_to_text


# ── Packet helper ─────────────────────────────────────────────────────────────

def build_packet(sender: str, sender_ip: str, sender_mac: str,
                 receiver: str, port: int, message: str) -> str:
    """Wraps create_packet, encoding the message to binary first."""
    return create_packet(
        sender=sender,
        receiver=receiver,
        message=text_to_binary(message),
        ip=sender_ip,
        mac=sender_mac,
        port=port,
    )


# ── Network layer ─────────────────────────────────────────────────────────────

class ChatConnection:
    def __init__(self, host: str, port: int, username: str, ca_cert: str | None):
        self.host     = host
        self.port     = port
        self.username = username
        self.ca_cert  = ca_cert
        self.sock     = None
        self._on_message  = None
        self._on_error    = None

    def set_callbacks(self, on_message, on_error):
        self._on_message = on_message
        self._on_error   = on_error

    def connect(self):
        raw = socket.create_connection((self.host, self.port), timeout=10)

        context = ssl.create_default_context()
        if self.ca_cert:
            context.load_verify_locations(self.ca_cert)
        else:
            # dev/self-signed: disable hostname + cert verification
            context.check_hostname = False
            context.verify_mode    = ssl.CERT_NONE

        self.sock = context.wrap_socket(raw, server_hostname=self.host)

        # handshake: send username first, matching server's client.recv(1024)
        self.sock.sendall(self.username.encode())

        # start background receive thread
        t = threading.Thread(target=self._receive_loop, daemon=True)
        t.start()

    def send(self, receiver: str, message: str):
        if not self.sock:
            return
        local_ip, local_port = self.sock.getsockname()
        local_mac = "00:00:00:00:00:00"   # replace with getmac if available
        packet = build_packet(
            sender=self.username,
            sender_ip=local_ip,
            sender_mac=local_mac,
            receiver=receiver,
            port=local_port,
            message=message,
        )
        self.sock.sendall(packet.encode())

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _receive_loop(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                if self._on_message:
                    self._on_message(data.decode())
            except Exception as e:
                if self._on_error:
                    self._on_error(str(e))
                break


# ── GUI ───────────────────────────────────────────────────────────────────────

DARK_BG   = "#1e1e2e"
PANEL_BG  = "#2a2a3d"
ACCENT    = "#7c6af7"
ACCENT_HV = "#9d8fff"
TEXT      = "#e0e0f0"
MUTED     = "#888899"
BUBBLE_ME = "#3d3560"
BUBBLE_RX = "#2e2e44"
FONT_MAIN = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_MONO = ("Consolas", 10)


class LoginScreen(tk.Frame):
    def __init__(self, master, on_connect):
        super().__init__(master, bg=DARK_BG)
        self.on_connect = on_connect
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        # centre card
        card = tk.Frame(self, bg=PANEL_BG, padx=36, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Ringer", font=("Segoe UI", 22, "bold"),
                 fg=ACCENT, bg=PANEL_BG).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        tk.Label(card, text="secure desktop messenger", font=("Segoe UI", 9),
                 fg=MUTED, bg=PANEL_BG).grid(row=1, column=0, columnspan=2, pady=(0, 24))

        fields = [
            ("Server host", "localhost"),
            ("Port",        "5000"),
            ("Username",    ""),
            ("CA cert path (leave blank for dev)", ""),
        ]
        self._entries = {}
        for i, (label, default) in enumerate(fields):
            tk.Label(card, text=label, font=FONT_MAIN, fg=MUTED,
                     bg=PANEL_BG, anchor="w").grid(row=i+2, column=0, sticky="w", pady=(6,0))
            e = tk.Entry(card, font=FONT_MAIN, bg="#16162a", fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         highlightthickness=1, highlightcolor=ACCENT,
                         highlightbackground=MUTED, width=30)
            e.insert(0, default)
            e.grid(row=i+2, column=1, padx=(12, 0), pady=(6,0), ipady=6)
            self._entries[label] = e

        btn = tk.Button(card, text="Connect", font=FONT_BOLD,
                        bg=ACCENT, fg="white", activebackground=ACCENT_HV,
                        activeforeground="white", relief="flat",
                        cursor="hand2", padx=24, pady=8,
                        command=self._submit)
        btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=(28, 0))

    def _submit(self):
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

        self.on_connect(host, port, username, ca_cert)


class ChatScreen(tk.Frame):
    def __init__(self, master, connection: ChatConnection, on_disconnect):
        super().__init__(master, bg=DARK_BG)
        self.conn          = connection
        self.on_disconnect = on_disconnect
        self._build()

        self.conn.set_callbacks(
            on_message=self._handle_incoming,
            on_error=self._handle_error,
        )

    def _build(self):
        self.pack(fill="both", expand=True)

        # ── top bar ──
        bar = tk.Frame(self, bg=PANEL_BG, pady=10, padx=16)
        bar.pack(fill="x")
        tk.Label(bar, text="Ringer", font=FONT_BOLD,
                 fg=ACCENT, bg=PANEL_BG).pack(side="left")
        tk.Label(bar, text=f"  logged in as  {self.conn.username}",
                 font=FONT_MAIN, fg=MUTED, bg=PANEL_BG).pack(side="left")
        tk.Button(bar, text="Disconnect", font=("Segoe UI", 9),
                  bg=PANEL_BG, fg=MUTED, activeforeground=TEXT,
                  relief="flat", cursor="hand2",
                  command=self._disconnect).pack(side="right")

        # ── main area ──
        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # message history
        self.history = scrolledtext.ScrolledText(
            main, font=FONT_MAIN, bg=DARK_BG, fg=TEXT,
            relief="flat", wrap="word", state="disabled",
            padx=16, pady=12, spacing3=6,
        )
        self.history.pack(fill="both", expand=True)

        # configure bubble tags
        self.history.tag_config("me",     background=BUBBLE_ME,
                                foreground=TEXT,   justify="right",
                                lmargin1=120, lmargin2=120, rmargin=16,
                                spacing1=4, spacing3=4)
        self.history.tag_config("them",   background=BUBBLE_RX,
                                foreground=TEXT,   justify="left",
                                lmargin1=16, lmargin2=16, rmargin=120,
                                spacing1=4, spacing3=4)
        self.history.tag_config("system", foreground=MUTED,
                                justify="center", spacing1=6, spacing3=6)

        # ── compose bar ──
        compose = tk.Frame(self, bg=PANEL_BG, padx=12, pady=10)
        compose.pack(fill="x")

        tk.Label(compose, text="To:", font=FONT_MAIN,
                 fg=MUTED, bg=PANEL_BG).pack(side="left")
        self.receiver_entry = tk.Entry(
            compose, font=FONT_MAIN, bg="#16162a", fg=TEXT,
            insertbackground=TEXT, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=MUTED, width=16
        )
        self.receiver_entry.pack(side="left", padx=(6, 12), ipady=5)

        self.message_entry = tk.Entry(
            compose, font=FONT_MAIN, bg="#16162a", fg=TEXT,
            insertbackground=TEXT, relief="flat",
            highlightthickness=1, highlightcolor=ACCENT,
            highlightbackground=MUTED,
        )
        self.message_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.message_entry.bind("<Return>", lambda _: self._send())

        tk.Button(compose, text="Send", font=FONT_BOLD,
                  bg=ACCENT, fg="white", activebackground=ACCENT_HV,
                  activeforeground="white", relief="flat",
                  cursor="hand2", padx=18, pady=5,
                  command=self._send).pack(side="left", padx=(10, 0))

    def _send(self):
        receiver = self.receiver_entry.get().strip()
        message  = self.message_entry.get().strip()
        if not receiver or not message:
            return
        self.conn.send(receiver, message)
        self._append(f"You → {receiver}: {message}", "me")
        self.message_entry.delete(0, "end")

    def _handle_incoming(self, raw: str):
        # schedule on main thread — Tkinter is not thread-safe
        self.after(0, lambda: self._parse_and_display(raw))

    def _parse_and_display(self, raw: str):
        try:
            packet  = read_packet(raw)
            sender  = packet.get("sender", packet.get("ip", "unknown"))
            message = binary_to_text(packet["message"])
            self._append(f"{sender}: {message}", "them")
        except Exception:
            self._append(raw, "them")

    def _handle_error(self, error: str):
        self.after(0, lambda: self._append(f"Connection error: {error}", "system"))

    def _append(self, text: str, tag: str):
        self.history.config(state="normal")
        self.history.insert("end", f" {text} \n", tag)
        self.history.config(state="disabled")
        self.history.see("end")

    def _disconnect(self):
        self.conn.disconnect()
        self.on_disconnect()


# ── App shell ─────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ringer")
        self.geometry("780x560")
        self.minsize(600, 420)
        self.configure(bg=DARK_BG)
        self._current = None
        self._show_login()

    def _show_login(self):
        if self._current:
            self._current.destroy()
        self._current = LoginScreen(self, on_connect=self._connect)

    def _connect(self, host, port, username, ca_cert):
        conn = ChatConnection(host, port, username, ca_cert)
        try:
            conn.connect()
        except Exception as e:
            messagebox.showerror("Connection failed", str(e))
            return

        if self._current:
            self._current.destroy()
        self._current = ChatScreen(self, conn, on_disconnect=self._show_login)


if __name__ == "__main__":
    App().mainloop()