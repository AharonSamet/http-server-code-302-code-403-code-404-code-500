# HTTP Server Shell
# Author: Aharon Samet

"""
    ############ Summary of the commands ###########
    # To review the exercise,                      #
    # please enter the following resources         #
    #                                              #
    # 127.0.0.1               - see some site      #
    # 127.0.0.1/forbidden.txt - see code 403       #
    # 127.0.0.1/text.txt      - see code 302       #
    # 127.0.0.1/t             - see code 404       #
    #                                              #
    # 127.0.0.1:80/calculate-area?height=3&width=4 #
    #  to see the calculation of a triangle        #
    #                                              #
    # 127.0.0.1:80/calculate-next?num=66           #
    # Enter a number and get the same number + 1   #
    ################################################
"""

# import modules:
import socket
import os
from typing import Dict

# ###############################  set constants ###############################
IP = '0.0.0.0'
PORT = 80

SOCKET_TIMEOUT = 0.1
ROOT_DIRECTORY = r'C:\wwwroot'
URL_TEST = r'\index.html'
LOCAL_ADDRESS = '127.0.0.1/'

# method and version
METHOD = 'GET'
VERSION = 'HTTP/1.1'
LINE_EXTENSION = '\r\n'
END_LINE_EXTENSION = '\r\n\r\n'

# Sites without access permission 403
LIST_SITES_FORBIDDEN = ['127.0.0.1/forbidden.txt', '127.0.0.1/forbidden1.txt']

# Sites that have moved to other addresses 302
REDIRECTION_DICTIONARY = ['127.0.0.1/text.txt', '127.0.0.1/wow.txt']

# Functions calculate-next
CALCULATOR: Dict[str, str] = {'next': 'calculate-next', 'area': 'calculate-area'}

# a Dictionary: Response line
RESPONSE_LINE: Dict[int, str] = {200: 'HTTP/1.1 200 OK' + LINE_EXTENSION,
                                 404: 'HTTP/1.1 404 Not Found' + LINE_EXTENSION,
                                 302: 'HTTP/1.1 302 Moved Temporarily' + LINE_EXTENSION,
                                 403: 'HTTP/1.1 403 Forbidden' + LINE_EXTENSION,
                                 500: 'HTTP/1.1 500 Internal Server Error' + LINE_EXTENSION}

# a Dictionary: File names, the file to send to the client:
FILE_NAMES: Dict[int, str] = {200: r'C:\wwwroot\index.html',
                              404: r'C:\wwwroot\Q4.4\404.html',
                              302: r'C:\wwwroot\Q4.4\302.html',
                              403: r'C:\wwwroot\Q4.4\403.html',
                              500: r'C:\wwwroot\Q4.4\500.html'}


# ###############################  end of constants ###############################


def send_to_client(client_socket, http_response):
    client_socket.send(http_response)


def get_file_data(file_name):
    """ Get data from file """
    try:
        with open(file_name, 'rb') as input_file:
            data = input_file.read()
        return data
    except Exception as err:
        return str(err).encode()


def create_http_header(url, code):
    """ create http header
    :param url: the url-request from the client
    :param code: the status-code
    :return: Response line + header-http: [version, sp, status code, sp, phrase, cr lf]...
    """
    http_header = ''
    if code != 200:
        data = get_file_data(FILE_NAMES.get(code))
        len_data = len(data)
        http_header = (RESPONSE_LINE.get(code) + 'Content-Length: ' + str(len_data) + END_LINE_EXTENSION).encode()\
                      + data
        return http_header
    file_type = url.split('.')[-1]
    if file_type == 'html':
        http_header = RESPONSE_LINE.get(code) + 'Content-Type: text/html; charset=utf-8' + LINE_EXTENSION
    elif file_type == 'jpg':
        http_header = RESPONSE_LINE.get(code) + 'Content-Type: image/jpeg' + LINE_EXTENSION
    elif file_type == 'js':
        http_header = RESPONSE_LINE.get(code) + \
                      'Content-Type: text/javascript; charset=UTF-8' + LINE_EXTENSION
    elif file_type == 'css':
        http_header = RESPONSE_LINE.get(code) + 'Content-Type: text/css' + LINE_EXTENSION
    elif file_type == 'ico':
        http_header = RESPONSE_LINE.get(code) + 'Content-Type: favicon/ico' + LINE_EXTENSION
    elif file_type == 'png':
        http_header = RESPONSE_LINE.get(code) + 'Content-Type: image/png' + LINE_EXTENSION
    data = get_file_data(url)
    len_data = len(data)
    http_header = (http_header + 'Content-Length: ' + str(len_data) +
                   END_LINE_EXTENSION).encode() + data
    return http_header


def calculate_area(height, width):
    """ A function that calculates the area of a right-angled triangle

    :param height: Height of the triangle
    :param width: Width of the triangle
    :return: the area of the triangle
    """
    sum_of_area = int(height) * int(width) / 2
    len_data = 'Content-Length: ' + str(sum_of_area / 4)
    http_header = RESPONSE_LINE.get(200) + 'Content-Type: text/html; charset=utf-8' + len_data \
                  + END_LINE_EXTENSION
    http_header += str(sum_of_area)
    return http_header.encode()


def calculate_next(value):
    """A function that returns the number entered as an input and adds one to it

    :param value: the number we want to be add by one
    :return: Builds the header for the response,
             And returns it inclusive with the number we raised in 1
    """
    http_header = RESPONSE_LINE.get(200) + 'Content-Type: text/html; charset=utf-8' + END_LINE_EXTENSION
    if value[0].isdigit():
        value = int(value) + 1
    elif value.startswith('-'):
        value = -int(value[1:]) + 1
    http_header += str(value)
    return http_header.encode()


def handle_url_request(url, client_socket):
    """ checking the url:
        receiving the http-header (by function 'create_http_header')
        send the response to client (by function 'send_to_client')
    """
    # checking if the request is calculate_area
    if url.split('\\')[-1].split('?')[0] == CALCULATOR.get('area'):
        try:
            url = url.split('?')[-1]
            height = url.split('&')[0].split('=')[-1]
            width = url.split('=')[-1]
            if height.isdigit() and width.isdigit():
                http_response = calculate_area(height, width)
                send_to_client(client_socket, http_response)
                return
            # else - go to code 404 (not-found)
        except Exception as err:
            print(err)

    # checking if the request is calculate-next
    if url.split('\\')[-1].split('?')[0] == CALCULATOR.get('next'):
        try:
            value = url.split('?')[-1]
            value = value.split('=')[-1]
            if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                http_response = calculate_next(value)
                send_to_client(client_socket, http_response)
                return
            # else - go to code 404 (not-found)
        except Exception as err:
            print(err)
    # checking status-code-error 302 (Sites that have moved to other addresses):
    if LOCAL_ADDRESS + url.split('\\')[-1] in REDIRECTION_DICTIONARY:
        http_response = create_http_header(url, 302)
        send_to_client(client_socket, http_response)
        return
    # checking status-code-error 403 (Sites without access permission):
    elif LOCAL_ADDRESS + url.split('\\')[-1] in LIST_SITES_FORBIDDEN:
        http_response = create_http_header(url, 403)
        send_to_client(client_socket, http_response)
        return
    # checking status-code-error 404: (NOT FOUND)
    elif not os.path.exists(url) or not os.path.isfile(url):
        http_response = create_http_header(url, 404)
        send_to_client(client_socket, http_response)
        return
    # else: status-code = 'OK 200':
    http_response = create_http_header(url, 200)
    send_to_client(client_socket, http_response)


def full_url(resource):
    """ Prepare the url, To enable the server to find the file on the computer

    :param resource: receiving the resource/url from client
    :return: the full url
    """
    # if (url/resource == '127.0.0.1':)
    if resource == '/' or resource == ' ':
        url = "{0}{1}".format(ROOT_DIRECTORY, URL_TEST)
    # else (if url/resource == 'Specific resource')
    else:
        url = "{0}{1}".format(ROOT_DIRECTORY, str(resource).replace('/', '\\'))
    print(f'the client request = {url}')
    return url


def handle_client_request(resource, client_socket):
    url = full_url(resource)
    # checking the url:
    handle_url_request(url, client_socket)


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    if request != b'':
        # Divide the request line: [method, sp, url, version, cr lf]
        request = request.decode().split('\r')[0]
        method = request.split()[0]
        url = request.split()[1]
        version = request.split()[2]
        if method == METHOD and version == VERSION:
            return True, url
        else:
            return False, None
    else:
        return True, None


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    try:
        client_request = client_socket.recv(1024)
        valid_http, resource = validate_http_request(client_request)
        if valid_http and resource is not None:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        elif not valid_http and resource is None:
            print('Error: Not a valid HTTP request')
            # code 500: Internal Server Error
            data = get_file_data(FILE_NAMES.get(500))
            len_data = len(data)
            http_header = (RESPONSE_LINE.get(500) + 'Content-Length: ' + str(len_data) + '\r\n\r\n').encode() + data
            send_to_client(client_socket, http_header)
        else:
            print('the client is in the middle of sending')
        client_socket.close()
    except Exception as err:
        print(str(err))
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    print("Listening for connections on port %d" % PORT)
    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
