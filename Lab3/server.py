import socket
import threading

# Shared in-memory key-value store
data_store = {}

# Lock to prevent race conditions when multiple clients
# access the dictionary at the same time
store_lock = threading.Lock()


def handle_client(client_socket, client_address):
    print(f"Connected: {client_address}")

    try:
        while True:
            message = client_socket.recv(1024).decode("utf-8").strip()

            if not message:
                break

            print(f"[{client_address}] {message}")

            parts = message.split()

            if len(parts) == 0:
                response = "ERROR: Empty command"

            elif parts[0].upper() == "PUT":
                if len(parts) < 3:
                    response = "ERROR: Usage PUT <key> <value>"
                else:
                    key = parts[1]
                    value = " ".join(parts[2:])

                    with store_lock:
                        data_store[key] = value

                    response = "OK"

            elif parts[0].upper() == "GET":
                if len(parts) != 2:
                    response = "ERROR: Usage GET <key>"
                else:
                    key = parts[1]

                    with store_lock:
                        if key in data_store:
                            response = data_store[key]
                        else:
                            response = "NOT FOUND"

            else:
                response = "ERROR: Unknown command"

            client_socket.sendall((response + "\n").encode("utf-8"))

    except ConnectionResetError:
        print(f"Client {client_address} disconnected unexpectedly")

    except Exception as e:
        print(f"Error with client {client_address}: {e}")

    finally:
        client_socket.close()
        print(f"Disconnected: {client_address}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allows quick restart of server
    server_socket.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR, 1)

    server_address = ("127.0.0.1", 12345)

    try:
        server_socket.bind(server_address)
        server_socket.listen(5)

        print("Server listening on port 12345...")

        while True:
            client_socket, client_address = server_socket.accept()

            # Create a new thread for each client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )

            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    except Exception as e:
        print(f"Server error: {e}")

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()