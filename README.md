# FCS


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
