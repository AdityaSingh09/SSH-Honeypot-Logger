import socket
import threading
import paramiko
import uuid
from datetime import datetime
from shell import FakeShell
from database import (
    initialize_database,
    log_login_attempt,
    create_session,
    close_session,
    log_command
)
from logger import generate_event, print_event


HOST_KEY = paramiko.RSAKey(filename="keys/server_rsa.key")


class SSHHoneypot(paramiko.ServerInterface):

    def __init__(self, client_ip):

        self.client_ip = client_ip

        # Used for shell synchronization
        self.event = threading.Event()

    def check_channel_exec_request(self, channel, command):
      return False
    
    def check_auth_password(self, username, password):

        print("\n=== LOGIN ATTEMPT ===")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"IP Address: {self.client_ip}")

        log_login_attempt(
            self.client_ip,
            username,
            password
        )

        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):

        if kind == "session":
            return paramiko.OPEN_SUCCEEDED

        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(
        self,
        channel,
        term,
        width,
        height,
        pixelwidth,
        pixelheight,
        modes
    ):
        return True

    def check_channel_shell_request(self, channel):

        # Signal that shell request succeeded
        self.event.set()

        return True

# Handle the connection and create a new session for session telemerty 
def handle_connection(client_socket, address):

    print(f"\n[+] Connection received from {address[0]}")
    
    session_id = str(uuid.uuid4())

    start_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    create_session(
        session_id,
        address[0],
        start_time
    )

    print(
        f"[SESSION START] "
        f"{session_id}"
    )
    event = generate_event(
        category="SESSION",
        event_type="session_started",
        session_id=session_id,
        source_ip=address[0]
    )
    print_event(event)

    transport = paramiko.Transport(client_socket)

    transport.add_server_key(HOST_KEY)

    server = SSHHoneypot(address[0])

    try:

        transport.start_server(server=server)

        channel = transport.accept(20)

        if channel is None:
            print("[-] No channel opened.")
            return

        print("[+] Waiting for shell request...")

        server.event.wait(10)

        if not server.event.is_set():
            print("[-] No shell request received.")
            return

        print("[+] Interactive shell opened.")
        
        # Create a new shell instance for this connection
        shell = FakeShell()

        channel.send("\r\n")
        channel.send("Welcome to Ubuntu 22.04 LTS\r\n")
        channel.send(shell.get_prompt())
        
        
        buffer = ""

        while True:

            data = channel.recv(1024).decode("utf-8")

            if not data:
                break
            channel.send(data)
            buffer += data

            # Wait until Enter key
            if "\r" not in buffer and "\n" not in buffer:
                continue

            command = buffer.strip()

            buffer = ""

            if not command:
                channel.send(shell.get_prompt())
                continue

            print(f"[COMMAND] {command}")

            
            log_command(
                session_id,
                command,
                shell.current_directory
            )
            response = shell.handle_command(command)

            channel.send(response)

            if command == "exit":
                break

            channel.send(shell.get_prompt())

            
            

    except Exception as e:

        print(f"[-] Error: {e}")

    finally:
        end_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
        )

        close_session(
            session_id,
            end_time
        )
        event = generate_event(

            category="SESSION",

            event_type="session_ended",

            session_id=session_id,

            source_ip=address[0]

        )

        print_event(event)       

        print(
            f"[SESSION END] "
            f"{session_id}"
        )

        transport.close()

       
def start_server(host="127.0.0.1", port=2222):

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind((host, port))

    server_socket.listen(100)

    # Prevent blocking forever
    server_socket.settimeout(1)

    print(f"[+] SSH Honeypot running on port {port}")

    try:

        while True:

            try:

                client_socket, address = server_socket.accept()

                client_thread = threading.Thread(
                    target=handle_connection,
                    args=(client_socket, address)
                )

                client_thread.daemon = True

                client_thread.start()

            except socket.timeout:
                continue

    except KeyboardInterrupt:

        print("\n[!] Shutting down honeypot...")

    finally:

        server_socket.close()

        print("[+] Socket closed.")


if __name__ == "__main__":

    initialize_database()

    start_server()