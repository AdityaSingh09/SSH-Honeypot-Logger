def handle_command(command):
  
    command = command.strip()

    if command == "ls":

        return (
            "Documents  Downloads  secrets.txt\r\n"
        )

    elif command == "pwd":

        return "/home/admin\r\n"

    elif command == "whoami":

        return "admin\r\n"

    elif command == "uname -a":

        return (
            "Linux ubuntu-server "
            "5.15.0-91-generic "
            "x86_64 GNU/Linux\r\n"
        )

    elif command == "id":

        return (
            "uid=1000(admin) "
            "gid=1000(admin) "
            "groups=1000(admin)\r\n"
        )

    elif command == "cat /etc/passwd":

        return (
            "root:x:0:0:root:/root:/bin/bash\r\n"
            "admin:x:1000:1000:admin:/home/admin:/bin/bash\r\n"
        )

    elif command == "ps aux":

        return (
            "root       1  0.0  0.1  22568  4108 ?        Ss   08:00   0:01 init\r\n"
            "root     532  0.0  0.2  54000  8200 ?        Ss   08:01   0:00 sshd\r\n"
            "admin   1042  0.1  0.3  72000 12000 pts/0    S+   08:10   0:00 bash\r\n"
        )

    elif command == "history":

        return (
            "1 ls\r\n"
            "2 pwd\r\n"
            "3 whoami\r\n"
        )

    elif command == "exit":

        return "logout\r\n"

    else:

        return f"{command}: command not found\r\n"