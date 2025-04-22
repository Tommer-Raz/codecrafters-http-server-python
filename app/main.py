import socket  # noqa: F401
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="full path directory")
args = parser.parse_args()

def send_res(conn, content, content_type="text/plain"):
    response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    f"\r\n"
                    ).encode() + content.encode()
    conn[0].sendall(response)

def handle_request(conn):
    req = conn[0].recv(1024).decode()
    endpoint = req.split(" ")[1]
    if endpoint == "/":
        conn[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif endpoint.startswith("/echo/"):
        content = endpoint.removeprefix("/echo/")
        send_res(conn, content)
    elif endpoint.startswith("/files/"):
        file_name = endpoint.removeprefix("/files/")
        path = args.directory
        try:
            with open(path + file_name, "r") as content_file:
                content = content_file.read()
                send_res(conn, content, "application/octet-stream")
        except:
            conn[0].sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    elif endpoint == "/user-agent":
        user_agant = req.split("\r\n")[2].removeprefix("User-Agent: ")
        send_res(conn, user_agant)
    else:
        conn[0].sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        conn = server_socket.accept() # wait for client
        threading.Thread(target=handle_request, args=(conn, )).start()

if __name__ == "__main__":
    main()
