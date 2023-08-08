import socket
import threading
import os


def read_command(control_socket):
    # get port number of client's data_socket
    new_port = int(control_socket.recv(buffer_size).decode('ascii'))

    # create client data socket
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect data socket to client
    data_socket.connect((server_ip, new_port))

    # receive the command from client and parse
    command = control_socket.recv(buffer_size).decode('ascii')
    if len(command.split(' ')) == 1:
        if command == 'LIST':
            files = os.listdir('./serverContent')
            files = [f for f in files if os.path.isfile('./serverContent/' + f)]
            files = [f for f in files if not f.startswith('.')]
            files = ' '.join(files)
            data_socket.send(files.encode('ascii'))
        elif command == 'QUIT':
            data_socket.close()
            control_socket.close()
            return
    else:
        commandParsed = command.split(' ')
        if commandParsed[0] == 'RETR':
            try:
                with open('serverContent/' + commandParsed[1], 'rb') as f:
                    chunk = f.read(buffer_size)
                    while chunk:  # chunk == '' indicates EOF from file
                        data_socket.send(chunk)
                        chunk = f.read(buffer_size)
            except FileNotFoundError:
                response = 'File not found.'
                data_socket.send(response.encode('ascii'))
        if commandParsed[0] == 'STOR':
            with open('serverContent/' + commandParsed[1], 'wb') as f:
                chunk = data_socket.recv(buffer_size)
                try:
                    if chunk.decode('ascii') == 'File not found.':
                        print("File not found.")
                        os.remove('./serverContent/' + commandParsed[1])
                    else:
                        while chunk:
                            f.write(chunk)
                            chunk = data_socket.recv(buffer_size)
                        print("Downloaded " + commandParsed[1] + "\n")
                except UnicodeDecodeError:
                    while chunk:
                        f.write(chunk)
                        chunk = data_socket.recv(buffer_size)
                    print("Downloaded.\n")

    data_socket.close()
    read_command(control_socket)


# server parameters
server_ip = 'localhost'
server_port = 8907
buffer_size = 1024

# create server welcome socket, bind, and listen
welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcome_socket.bind((server_ip, server_port))
welcome_socket.listen()

print('The server is ready to communicate')

# accept incoming connections and multithreading
while True:
    control_socket, addr = welcome_socket.accept()
    threading.Thread(target=read_command, args=(control_socket,)).start()
