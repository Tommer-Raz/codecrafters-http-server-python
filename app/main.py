import socket  # noqa: F401
import threading
import argparse
import gzip

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", help="full path directory")
args = parser.parse_args()
close = False

def send_res(conn, content, content_type="text/plain", encoding=None, close=False):
    length = len(content)
    content = content.encode()
    response = "HTTP/1.1 200 OK\r\n"
    response += f"Content-Type: {content_type}\r\n"
    if encoding is not None:
       response += f"Content-Encoding: {encoding}\r\n"
       content = gzip.compress(content)
       length = len(content)
    response += f"Content-Length: {length}\r\n"
    if close:
        response += f"Connection: close\r\n"
    response += f"\r\n"
    
    response = response.encode() + content

    conn[0].sendall(response)

def handle_request(conn):
    close = False
    while not close:
        req = conn[0].recv(1024).decode()
        endpoint = req.split(" ")[1]
        method = req.split(" ")[0]
        close = req.split("\r\n")[2].removeprefix("Connection: ") == "close"
        encodings = req.split("\r\n")[2].removeprefix("Accept-Encoding: ").split(", ")
        if method == "GET":
            if endpoint == "/":
                if close:
                    conn[0].sendall(b"HTTP/1.1 200 OK\r\nconnection: close\r\n\r\n")
                    break
                else:
                    conn[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            elif endpoint.startswith("/echo/"):
                content = endpoint.removeprefix("/echo/")
                encoding = None
                if "gzip" in encodings:
                    encoding = "gzip"
                send_res(conn, content, "text/plain", encoding, close)
                if close:
                    break
            elif endpoint.startswith("/files/"):
                file_name = endpoint.removeprefix("/files/")
                path = args.directory
                try:
                    with open(path + file_name, "r") as content_file:
                        content = content_file.read()
                        send_res(conn, content, "application/octet-stream", None, close)
                except:
                    conn[0].sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
            elif endpoint == "/user-agent":
                user_agant = req.split("\r\n")[2].removeprefix("User-Agent: ")
                if close:
                    user_agant = req.split("\r\n")[3].removeprefix("User-Agent: ")
                send_res(conn, user_agant, "text/plain", None, close)
            else:
                conn[0].sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        elif method == "POST":
            if endpoint.startswith("/files/"):
                file_name = endpoint.removeprefix("/files/")
                path = args.directory
                with open(path + file_name, "w") as content_file:
                    content_file.write(req.split("\r\n")[5])
                    conn[0].sendall(b"HTTP/1.1 201 Created\r\n\r\n")

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
