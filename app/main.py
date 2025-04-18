import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn = server_socket.accept() # wait for client
    req = conn[0].recv(1024).decode().split(" ")
    if req[1] == "/":
        conn[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif req[1].startswith("/echo/"):
        content = req[1].removeprefix("/echo/")
        response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    f"\r\n"
                    ).encode() + content.encode()
        conn[0].sendall(response)
    else:
        conn[0].sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
