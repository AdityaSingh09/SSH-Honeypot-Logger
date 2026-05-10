import socket
import threading
import paramiko
from datetime import datetime

HOST_KEY = paramiko.RSAKey(filename="keys/server_rsa.key")

class SSHHoneypot(paramiko.ServerInterface):

    def check_auth_password(self, username, password):

        print("\n=== LOGIN ATTEMPT ===")
        print(f"Time: {datetime.now()}")
        print(f"Username: {username}")
        print(f"Password: {password}")

        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"


def handle_connection(client_socket, address):

    print(f"\n[+] Connection received from {address[0]}")

    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)

    server = SSHHoneypot()

    try:
        transport.start_server(server=server)

        channel = transport.accept(20)

        if channel is None:
            print("[-] No channel opened.")
            return

    except Exception as e:
        print(f"[-] Error: {e}")

    finally:
        transport.close()


def start_server(host="127.0.0.1", port=2222):
  
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((host, port))
    server_socket.listen(100)

    # Prevent infinite blocking
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

                # Thread exits with main program
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
    start_server()