import socket


def main():
    client_socket = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)

    server_address = ("127.0.0.1", 12345)

    try:
        client_socket.connect(server_address)

        print("Connected to server.")
        print("Commands:")
        print("PUT <key> <value>")
        print("GET <key>")
        print("EXIT")

        while True:
            command = input("> ").strip()

            if command.upper() == "EXIT":
                print("Closing connection...")
                break

            client_socket.sendall((command + "\n").encode("utf-8"))

            response = client_socket.recv(1024).decode("utf-8").strip()

            print("Server response:", response)

    except ConnectionRefusedError:
        print("Unable to connect. Make sure the server is running.")

    except Exception as e:
        print(f"Client error: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()