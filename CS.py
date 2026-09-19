import asyncio
import asyncssh
import sys
import glob
from pathlib import Path


HOST = "0.0.0.0"
PORT = None

IP = None

SEARCH_FLAG = False
File_list = []
Search_for_file = None


incorrect_args = '''
incorrect args =c

SERVER:
    fcs 0 <ip> <port>

CLIENT:
    fcs 1 <search> <ip> <port> <files>

1 - server/client (1/0)
2 - Search for file (0 - no, 1 - yes)
3 - IP
4 - PORT
5 - "file1,file2" or "*.png"

Examples:

Server:
    fcs 0 0.0.0.0 8022

Client with explicit files:
    fcs 1 0 192.168.1.100 8022 "file1.txt,file2.jpg"

Client with search:
    fcs 1 1 192.168.1.100 8022 "*.png"
'''


def Server():

    SAVE_DIR = Path("")
    HOST_KEY = "server_key"

    class SSHServer(asyncssh.SSHServer):

        def begin_auth(self, username):
            return False

    async def main():

        SAVE_DIR.mkdir(exist_ok=True)

        if not Path(HOST_KEY).exists():

            print("Generating server key...")

            key = asyncssh.generate_private_key("ssh-ed25519")
            key.write_private_key(HOST_KEY)

        await asyncssh.create_server(
            SSHServer,
            HOST,
            PORT,
            server_host_keys=[HOST_KEY],
            sftp_factory=asyncssh.SFTPServer,
        )

        print(f"Server started on {HOST}:{PORT}")
        print(f"Files directory: {SAVE_DIR.resolve()}")

        await asyncio.Future()

    asyncio.run(main())


def FindFiles():

    return list(
        glob.iglob(
            Search_for_file,
            recursive=True
        )
    )


def progress_handler(src, dst, transferred, total):

    if total == 0:
        percent = 100
    else:
        percent = transferred / total * 100

    bar_length = 30

    filled = int(bar_length * percent / 100)
    bar = "#" * filled + "-" * (bar_length - filled)

    transferred_mb = transferred / 1024 / 1024
    total_mb = total / 1024 / 1024

    print(
        f"\r[{bar}] "
        f"{percent:6.2f}% "
        f"{transferred_mb:.2f}/{total_mb:.2f} MB",
        end="",
        flush=True
    )


async def Client():

    async with asyncssh.connect(
        IP,
        port=PORT,
        username="anonymous",
        known_hosts=None,
    ) as conn:

        async with conn.start_sftp_client() as sftp:

            for filename in File_list:

                print(f"\nSending: {filename}")

                await sftp.put(
                    filename,
                    Path(filename).name,
                    progress_handler=progress_handler,
                )

                print("\nDone")


def main():

    global File_list
    global SEARCH_FLAG
    global Search_for_file
    global HOST
    global PORT
    global IP


    if len(sys.argv) < 2:
        print(incorrect_args)
        return

    # server/client

    try:
        cs = int(sys.argv[1])
    except ValueError:
        print(incorrect_args)
        return

    if cs not in (0, 1):
        print(incorrect_args)
        return

    # SERVER

    if cs == 0:

        if len(sys.argv) < 4:
            print(incorrect_args)
            return

        HOST = sys.argv[2]

        try:
            PORT = int(sys.argv[3])
        except ValueError:
            print(incorrect_args)
            return

        if PORT < 1 or PORT > 65535:
            print("Invalid port")
            return

        Server()
        return

    # CLIENT

    if len(sys.argv) < 6:
        print(incorrect_args)
        return

    try:
        search_flag = int(sys.argv[2])
    except ValueError:
        print(incorrect_args)
        return

    if search_flag not in (0, 1):
        print(incorrect_args)
        return

    # IP

    IP = sys.argv[3]

    # PORT

    try:
        PORT = int(sys.argv[4])
    except ValueError:
        print(incorrect_args)
        return

    if PORT < 1 or PORT > 65535:
        print("Invalid port")
        return


    if search_flag == 1:

        SEARCH_FLAG = True
        Search_for_file = sys.argv[5]

        File_list = FindFiles()


    else:

        SEARCH_FLAG = False

        File_list = [
            file.strip()
            for file in sys.argv[5].split(",")
            if file.strip()
        ]

    print(f"Target: {IP}:{PORT}")

    print("Files to send:")

    for file in File_list:
        print(f"  {file}")

    if not File_list:
        print("No files found")
        return

    asyncio.run(Client())


main()
