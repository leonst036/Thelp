import customtkinter as ctk
import tkinter as tk
import jsonParser
import sshManager
import subprocess
import threading
import sys
import os
import shlex
import time
from paramiko.ssh_exception import SSHException

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MonitorWindow(ctk.CTkToplevel):
    def __init__(self, parent, server, client):
        super().__init__(parent)
        self.title(f"Monitoring {server.get('name')}")
        self.geometry("700x500")
        self.server = server
        self.client = client
        self.running = True

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Layout
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        # CPU Graph
        self.cpu_frame = ctk.CTkFrame(self)
        self.cpu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.cpu_label = ctk.CTkLabel(self.cpu_frame, text="CPU Usage: 0%", font=("Arial", 16, "bold"))
        self.cpu_label.pack(pady=5)
        self.cpu_canvas = tk.Canvas(self.cpu_frame, bg="#1e1e1e", highlightthickness=0)
        self.cpu_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # RAM Graph
        self.ram_frame = ctk.CTkFrame(self)
        self.ram_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.ram_label = ctk.CTkLabel(self.ram_frame, text="RAM Usage: 0%", font=("Arial", 16, "bold"))
        self.ram_label.pack(pady=5)
        self.ram_canvas = tk.Canvas(self.ram_frame, bg="#1e1e1e", highlightthickness=0)
        self.ram_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Stats
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.net_label = ctk.CTkLabel(self.stats_frame, text="Network: \u2193 0 B/s | \u2191 0 B/s", font=("Arial", 14))
        self.net_label.pack(pady=5)
        
        self.top_label = ctk.CTkLabel(self.stats_frame, text="Top Processes:\n", font=("monospace", 12), justify="left")
        self.top_label.pack(pady=5)
        
        self.cpu_data = []
        self.ram_data = []
        
        # Start monitoring
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def on_close(self):
        self.running = False
        try:
            self.client.close()
        except:
            pass
        self.destroy()

    def format_bytes(self, b):
        if b < 1024: return f"{b:.0f} B"
        elif b < 1024*1024: return f"{b/1024:.1f} KB"
        else: return f"{b/1024/1024:.1f} MB"

    def draw_graph(self, canvas, data, color):
        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10 or h < 10 or not data:
            return
            
        max_points = 60
        dx = w / (max_points - 1)
        
        # Draw background grid lines
        for i in range(1, 5):
            y = h - (i * h / 4)
            canvas.create_line(0, y, w, y, fill="#333333", dash=(2, 2))
            
        line_points = []
        poly_points = [(0, h)]
        
        start_idx = max(0, len(data) - max_points)
        draw_data = data[start_idx:]
        
        for i, val in enumerate(draw_data):
            x = i * dx
            y = h - (val / 100.0) * h
            line_points.append((x, y))
            poly_points.append((x, y))
            
        poly_points.extend([(line_points[-1][0], h), (0, h)])
        
        if len(line_points) > 1:
            try:
                canvas.create_polygon(poly_points, fill=color, outline="", stipple="gray50")
            except tk.TclError:
                # System may not support stipple
                canvas.create_polygon(poly_points, fill=color, outline="")
            canvas.create_line(line_points, fill=color, width=2)
            
    def monitor_loop(self):
        last_rx = 0
        last_tx = 0
        last_time = 0
        
        while self.running:
            try:
                cmd = (
                    "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'; "
                    "free -m | awk 'NR==2{printf \"%.1f\\n\", $3*100/$2}'; "
                    "cat /proc/net/dev | grep -v 'lo:' | awk '{rx+=$2; tx+=$10} END {print rx\" \"tx}'; "
                    "ps aux --sort=-%cpu | head -n 4 | tail -n 3 | awk '{print $11\" \"$3}'"
                )
                stdin, stdout, stderr = self.client.exec_command(cmd)
                out = stdout.read().decode().strip().split('\n')
                
                if len(out) >= 3 and self.running:
                    try:
                        cpu_usage = float(out[0].strip() or 0)
                        ram_usage = float(out[1].strip() or 0)
                        net_vals = out[2].strip().split()
                        if len(net_vals) == 2:
                            current_rx, current_tx = float(net_vals[0]), float(net_vals[1])
                        else:
                            current_rx, current_tx = 0, 0
                        
                        top_procs = out[3:]

                        t = time.time()
                        if last_time > 0:
                            dt = t - last_time
                            rx_speed = (current_rx - last_rx) / dt
                            tx_speed = (current_tx - last_tx) / dt
                        else:
                            rx_speed, tx_speed = 0, 0
                        last_rx, last_tx, last_time = current_rx, current_tx, t

                        self.cpu_data.append(cpu_usage)
                        self.ram_data.append(ram_usage)
                        
                        if len(self.cpu_data) > 60: self.cpu_data.pop(0)
                        if len(self.ram_data) > 60: self.ram_data.pop(0)

                        procs_str = "\n".join([f"{os.path.basename(p.split()[0])[:20]:<25} {p.split()[1]}% CPU" for p in top_procs if len(p.split()) >= 2])
                        
                        # Update UI
                        def update_ui():
                            if not self.running: return
                            self.cpu_label.configure(text=f"CPU Usage: {cpu_usage:.1f}%")
                            self.ram_label.configure(text=f"RAM Usage: {ram_usage:.1f}%")
                            self.net_label.configure(text=f"Network: \u2193 {self.format_bytes(rx_speed)}/s | \u2191 {self.format_bytes(tx_speed)}/s")
                            self.top_label.configure(text=f"Top Processes:\n{procs_str}")
                            
                            self.draw_graph(self.cpu_canvas, self.cpu_data, "#00ff00")
                            self.draw_graph(self.ram_canvas, self.ram_data, "#00aaff")

                        self.after(0, update_ui)
                    except ValueError:
                        pass
                    
                time.sleep(2)
            except SSHException:
                break

class ThelpApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Thelp GUI")
        self.geometry("900x600")

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Navigation Frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.nav_label = ctk.CTkLabel(self.navigation_frame, text="Thelp", font=ctk.CTkFont(size=20, weight="bold"))
        self.nav_label.grid(row=0, column=0, padx=20, pady=20)

        self.local_btn = ctk.CTkButton(self.navigation_frame, text="Local Commands", command=self.show_local_commands)
        self.local_btn.grid(row=1, column=0, padx=20, pady=10)

        self.remote_btn = ctk.CTkButton(self.navigation_frame, text="SSH Servers", command=self.show_servers)
        self.remote_btn.grid(row=2, column=0, padx=20, pady=10)

        # Main Content Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Top area in main frame (buttons)
        self.list_frame = ctk.CTkScrollableFrame(self.main_frame, height=150)
        self.list_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Bottom area (output log)
        self.output_box = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(family="monospace", size=12))
        self.output_box.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.output_box.configure(state="disabled")

        # Interactive Input area
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.cmd_input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type input for running command and press Enter...")
        self.cmd_input_entry.grid(row=0, column=0, sticky="ew")
        self.cmd_input_entry.bind("<Return>", self.send_input)

        self.cmd_input_btn = ctk.CTkButton(self.input_frame, text="Send", width=60, command=self.send_input)
        self.cmd_input_btn.grid(row=0, column=1, padx=(10, 0))

        self.current_stdin = None
        self.current_stdin_lock = threading.Lock()

        self.show_local_commands()

    def send_input(self, event=None):
        text = self.cmd_input_entry.get()
        self.cmd_input_entry.delete(0, 'end')

        with self.current_stdin_lock:
            if self.current_stdin and not self.current_stdin.closed:
                try:
                    self.current_stdin.write(text + "\n")
                    self.current_stdin.flush()
                    self.log(f" > {text}")
                except Exception as e:
                    self.log(f"> Failed to send input: {e}")
            else:
                self.log("> No active command waiting for input.")

    def log(self, text):
        def _log():
            self.output_box.configure(state="normal")
            self.output_box.insert("end", text + "\n")
            self.output_box.see("end")
            self.output_box.configure(state="disabled")
        self.after(0, _log)

    def clear_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

    def show_local_commands(self):
        self.clear_list()
        self.log("--- Loading Local Commands ---")
        try:
            command_names = jsonParser.get_command_names()
            for i, name in enumerate(command_names):
                row_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
                row_frame.grid(row=i, column=0, sticky="ew", pady=2)
                row_frame.grid_columnconfigure(1, weight=1)

                edit_btn = ctk.CTkButton(row_frame, text="✎", width=30, command=lambda idx=i: self.edit_local_command(idx))
                edit_btn.grid(row=0, column=0, padx=(10, 5), pady=3, sticky="w")

                btn = ctk.CTkButton(row_frame, text=name, command=lambda idx=i: self.run_local_command(idx))
                btn.grid(row=0, column=1, padx=(5, 10), pady=3, sticky="ew")

            self.list_frame.grid_columnconfigure(0, weight=1)
                
            # Add new command button
            add_btn = ctk.CTkButton(self.list_frame, text="+ Add Command", fg_color="green", hover_color="darkgreen", command=self.add_new_local_command)
            add_btn.grid(row=len(command_names), column=0, padx=10, pady=10, sticky="ew")
        except Exception as e:
            self.log(f"No commands found or error: {e}")

    def edit_local_command(self, index):
        cmd_data = jsonParser.get_full_command_by_index(index)
        if not cmd_data:
            return

        old_name = cmd_data.get("name", "")
        old_cmd = cmd_data.get("command", "")

        name = self.get_input(f"Enter new name (leave empty to keep: '{old_name}')")
        if name is None:
            return
        if name.strip() == "":
            name = old_name
            
        command = self.get_input(f"Enter new command (leave empty to keep: '{old_cmd}')")
        if command is None:
            return
        if command.strip() == "":
            command = old_cmd
            
        try:
            jsonParser.update_command(index, name, command)
            self.log(f"> Updated command: {name}")
            self.show_local_commands()
        except Exception as e:
            self.log(f"> Failed to update command: {e}")

    def add_new_local_command(self):
        name = self.get_input("Enter new command name:")
        if not name:
            return

        command = self.get_input("Enter the shell command (optionally include {input}):")
        if not command:
            return

        try:
            jsonParser.add_command(name, command)
            self.log(f"> Added new command: {name}")
            self.show_local_commands()
        except Exception as e:
            self.log(f"> Failed to add command: {e}")

    def show_servers(self):
        self.clear_list()
        self.log("--- Loading SSH Servers ---")
        try:
            server_names = jsonParser.get_server_names()
            for i, name in enumerate(server_names):
                row_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
                row_frame.grid(row=i, column=0, sticky="ew", pady=2)
                row_frame.grid_columnconfigure(1, weight=1)

                btn = ctk.CTkButton(row_frame, text=name, command=lambda idx=i: self.show_server_commands(idx))
                btn.grid(row=0, column=1, padx=(5, 5), pady=3, sticky="ew")

                monitor_btn = ctk.CTkButton(row_frame, text="Monitor", width=60, fg_color="blue", command=lambda idx=i: self.monitor_gui_server(idx))
                monitor_btn.grid(row=0, column=2, padx=(5, 10), pady=3, sticky="e")

            # Add new server button
            add_btn = ctk.CTkButton(self.list_frame, text="+ Add Server", fg_color="green", hover_color="darkgreen", command=self.add_new_server)
            add_btn.grid(row=len(server_names), column=0, padx=10, pady=10, sticky="ew")
        except Exception as e:
            self.log(f"No servers found or error: {e}")

    def add_new_server(self):
        name = self.get_input("Enter server display name:")
        if not name:
            return

        host = self.get_input("Enter host/IP address:")
        if not host:
            return

        port_str = self.get_input("Enter port (default 22):")
        port = 22
        if port_str:
            try:
                port = int(port_str)
            except ValueError:
                self.log("> Invalid port. Using default 22.")

        username = self.get_input("Enter username:")
        if not username:
            return

        password = self.get_input("Enter password (leave empty if using key/agent):")
        # Let's allow empty password string

        try:
            jsonParser.add_server(name, host, username, password or "", port)
            self.log(f"> Added new server: {name}")
            self.show_servers()
        except Exception as e:
            self.log(f"> Failed to add server: {e}")

    def show_server_commands(self, server_index):
        self.clear_list()
        server = jsonParser.get_server_by_index(server_index)
        self.log(f"--- Commands for {server.get('name', 'Server')} ---")

        commands = server.get('commands', {})
        command_keys = list(commands.keys())
        for i, key in enumerate(command_keys):
            cmd = commands[key]
            name = cmd.get("name", key)
            
            row_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, sticky="ew", pady=2)
            row_frame.grid_columnconfigure(1, weight=1)

            edit_btn = ctk.CTkButton(row_frame, text="✎", width=30, command=lambda idx=i, s_idx=server_index: self.edit_server_command(s_idx, idx))
            edit_btn.grid(row=0, column=0, padx=(10, 5), pady=3, sticky="w")

            btn = ctk.CTkButton(row_frame, text=name, command=lambda idx=i, s=server: self.run_server_command(s, idx))
            btn.grid(row=0, column=1, padx=(5, 10), pady=3, sticky="ew")

        # Add new command button
        add_btn = ctk.CTkButton(self.list_frame, text="+ Add Command", fg_color="green", hover_color="darkgreen", command=lambda s_idx=server_index: self.add_new_server_command(s_idx))
        add_btn.grid(row=len(command_keys), column=0, padx=10, pady=(10, 5), sticky="ew")

        back_btn = ctk.CTkButton(self.list_frame, text="← Back to Servers", fg_color="gray", command=self.show_servers)
        back_btn.grid(row=len(command_keys)+1, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        self.list_frame.grid_columnconfigure(0, weight=1)

    def edit_server_command(self, server_index, cmd_index):
        cmd_data = jsonParser.get_full_server_command_by_index(server_index, cmd_index)
        if not cmd_data:
            return

        old_name = cmd_data.get("name", "")
        old_cmd = cmd_data.get("command", "")

        name = self.get_input(f"Enter new name (leave empty to keep: '{old_name}')")
        if name is None:
            return
        if name.strip() == "":
            name = old_name
            
        command = self.get_input(f"Enter new command (leave empty to keep: '{old_cmd}')")
        if command is None:
            return
        if command.strip() == "":
            command = old_cmd
            
        try:
            jsonParser.update_server_command(server_index, cmd_index, name, command)
            self.log(f"> Updated server command: {name}")
            self.show_server_commands(server_index)
        except Exception as e:
            self.log(f"> Failed to update server command: {e}")

    def add_new_server_command(self, server_index):
        name = self.get_input("Enter new command name:")
        if not name:
            return

        command = self.get_input("Enter the shell command (optionally include {input}):")
        if not command:
            return

        try:
            jsonParser.add_server_command(server_index, name, command)
            self.log(f"> Added new server command: {name}")
            self.show_server_commands(server_index)
        except Exception as e:
            self.log(f"> Failed to add server command: {e}")

    def get_input(self, prompt="Enter input:"):
        dialog = ctk.CTkInputDialog(text=prompt, title="Input Required")
        return dialog.get_input()

    def monitor_gui_server(self, server_index):
        server = jsonParser.get_server_by_index(server_index)
        if not server:
            return
            
        self.log(f"--- Starting monitor window for {server.get('name')} ---")
        
        def connect_and_show():
            client = sshManager.connect_ssh_server(
                server['host'],
                server['port'],
                server['username'],
                server['password']
            )
            if not client:
                self.log(f"Connection to {server.get('name')} failed for monitoring.")
                return
            
            self.after(0, lambda: MonitorWindow(self, server, client))
            
        threading.Thread(target=connect_and_show, daemon=True).start()

    def run_local_command(self, index):
        command = jsonParser.get_command_by_index(index)
        if "{input}" in command:
            user_input = self.get_input("Enter input for command:")
            if user_input is None:
                return
            command = command.replace("{input}", shlex.quote(user_input))

        self.log(f"\n> Executing Local: {command}")

        def run():
            try:
                process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
                with self.current_stdin_lock:
                    self.current_stdin = process.stdin

                for line in iter(process.stdout.readline, ''):
                    if line: self.log(line.rstrip())
                for line in iter(process.stderr.readline, ''):
                    if line: self.log(f"ERROR: {line.rstrip()}")
                process.wait()

                with self.current_stdin_lock:
                    self.current_stdin = None

                self.log("> Execution Complete")
            except Exception as e:
                self.log(f"Execution failed: {e}")

        threading.Thread(target=run, daemon=True).start()

    def run_server_command(self, server, index):
        command = jsonParser.get_server_command_by_index(server, index)
        if "{input}" in command:
            user_input = self.get_input("Enter input for command:")
            if user_input is None:
                return
            command = command.replace("{input}", shlex.quote(user_input))

        self.log(f"\n> Executing on {server.get('name')}: {command}")

        def run():
            client = sshManager.connect_ssh_server(
                server['host'],
                server['port'],
                server['username'],
                server['password']
            )
            if not client:
                self.log("Connection failed.")
                return

            try:
                stdin, stdout, stderr = client.exec_command(command)
                with self.current_stdin_lock:
                    self.current_stdin = stdin

                for line in stdout:
                    self.log(line.strip())
                for line in stderr:
                    self.log(f"ERROR: {line.strip()}")

                with self.current_stdin_lock:
                    self.current_stdin = None

                self.log("> Execution Complete")
            except Exception as e:
                self.log(f"Execution failed: {e}")
            finally:
                client.close()

        threading.Thread(target=run, daemon=True).start()

def launch():
    app = ThelpApp()
    app.mainloop()

if __name__ == "__main__":
    launch()

