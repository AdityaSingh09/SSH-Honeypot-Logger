class FakeShell:
  
    def __init__(self):

        # Initial shell state
        self.current_directory = "/home/admin"

        self.history = []

        # Fake filesystem
        self.filesystem = {
            "/home/admin": [
                "Documents",
                "Downloads",
                "secrets.txt"
            ],

            "/home/admin/Documents": [
                "notes.txt",
                "work"
            ],

            "/home/admin/Downloads": [
                "backup.zip"
            ]
        }

    def get_prompt(self):

        return f"admin@honeypot:{self.current_directory}$ "

    def handle_command(self, command):

        command = command.strip()

        self.history.append(command)

        # EXIT
        if command == "exit":

            return "logout\r\n"

        # PWD
        elif command == "pwd":

            return f"{self.current_directory}\r\n"

        # WHOAMI
        elif command == "whoami":

            return "admin\r\n"

        # UNAME
        elif command == "uname -a":

            return (
                "Linux ubuntu-server "
                "5.15.0-91-generic "
                "x86_64 GNU/Linux\r\n"
            )

        # ID
        elif command == "id":

            return (
                "uid=1000(admin) "
                "gid=1000(admin) "
                "groups=1000(admin)\r\n"
            )

        # LS
        elif command == "ls":

            files = self.filesystem.get(
                self.current_directory,
                []
            )

            return "  ".join(files) + "\r\n"

        # CD
        elif command.startswith("cd "):

            target = command[3:].strip()

            if target == "..":

                if self.current_directory != "/home/admin":

                    self.current_directory = "/".join(
                        self.current_directory.split("/")[:-1]
                    )

                    if self.current_directory == "":
                        self.current_directory = "/"

                return ""

            new_path = f"{self.current_directory}/{target}"

            if new_path in self.filesystem:

                self.current_directory = new_path

                return ""

            return f"cd: no such file or directory: {target}\r\n"

        # HISTORY
        elif command == "history":

            output = ""

            for index, cmd in enumerate(self.history, start=1):

                output += f"{index} {cmd}\r\n"

            return output

        # CAT PASSWD
        elif command == "cat /etc/passwd":

            return (
                "root:x:0:0:root:/root:/bin/bash\r\n"
                "admin:x:1000:1000:admin:/home/admin:/bin/bash\r\n"
            )

        # PS
        elif command == "ps aux":

            return (
                "root       1  0.0  0.1  22568  4108 ?        Ss   08:00   0:01 init\r\n"
                "root     532  0.0  0.2  54000  8200 ?        Ss   08:01   0:00 sshd\r\n"
                "admin   1042  0.1  0.3  72000 12000 pts/0    S+   08:10   0:00 bash\r\n"
            )

        return f"{command}: command not found\r\n"