import os
import socket
import random


def no_connection():
    # create client control socket
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # attempt to connect
    command = input("Please connect to a server by typing: CONNECT <server name/IP address> <server port>\n")
    command = command.split(' ')

    # if wrong format for connect command, retry
    if len(command) < 3 or command[0] != 'CONNECT':
        no_connection()

    # if right format, try to connect
    try:
        control_socket.connect((command[1], int(command[2])))
    # if unable to connect, try again
    except:
        print('Could not connect.')
        no_connection()

    # begin sending commands
    send_command(control_socket)


def send_command(control_socket):
    # send the server our port and create server data socket
    control_socket.send(str(new_port).encode('ascii'))
    data_socket, addr = welcome_socket.accept()

    # get command as input, parse, and go
    # checking for valid command
    command = input("Please enter a command\n")
    commandParsed = command.split(' ')
    while len(commandParsed) > 2:
        command = input("Please enter a valid command\n")
        commandParsed = command.split(' ')
    if len(commandParsed) == 1:
        while commandParsed[0] not in oneCommands:
            command = input("Please enter a valid command\n")
            commandParsed = command.split(' ')
            if len(commandParsed) == 2 and commandParsed[0] in twoCommands:
                break
    if len(commandParsed) == 2:
        while commandParsed[0] not in twoCommands:
            command = input("Please enter a valid command\n")
            commandParsed = command.split(' ')
            if len(commandParsed) == 1 and commandParsed[0] in oneCommands:
                break

    # executing command
    if len(commandParsed) == 1:
        # list command
        if command == 'LIST':
            control_socket.send(command.encode('ascii'))
            files = data_socket.recv(buffer_size).decode('ascii')
            print(files)
        # quit command
        elif command == 'QUIT':
            control_socket.send(command.encode('ascii'))
            control_socket.close()
            data_socket.close()
            no_connection()

    elif len(commandParsed) == 2:
        # retr command
        if commandParsed[0] == 'RETR':
            control_socket.send(command.encode('ascii'))
            with open('clientContent/' + commandParsed[1], 'wb') as f:
                chunk = data_socket.recv(buffer_size)
                try:
                    if chunk.decode('ascii') == 'File not found.':
                        print("File not found.")
                        os.remove('./clientContent/' + commandParsed[1])
                    else:
                        while chunk:
                            f.write(chunk)
                            chunk = data_socket.recv(buffer_size)
                        print("Downloaded.\n")
                except UnicodeDecodeError:
                    while chunk:
                        f.write(chunk)
                        chunk = data_socket.recv(buffer_size)
                    print("Downloaded.\n")
        # stor command
        elif commandParsed[0] == 'STOR':
            control_socket.send(command.encode('ascii'))
            try:
                with open('clientContent/' + commandParsed[1], 'rb') as f:
                    chunk = f.read(buffer_size)
                    while chunk:  # chunk == '' indicates EOF from file
                        data_socket.send(chunk)
                        chunk = f.read(buffer_size)
                print("Stored " + commandParsed[1])
            except FileNotFoundError:
                print('File not found.')
                response = 'File not found.'
                data_socket.send(response.encode('ascii'))

    data_socket.close()
    send_command(control_socket)


# only valid commands
oneCommands = ['LIST', 'QUIT']
twoCommands = ['RETR', 'STOR']

# create server welcome socket
server_ip = 'localhost'
new_port = random.randrange(1000, 8000)
buffer_size = 1024
welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcome_socket.bind((server_ip, new_port))
welcome_socket.listen()

# force a connection
no_connection()
