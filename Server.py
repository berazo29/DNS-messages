import argparse
from sys import argv
import socket
import binascii


def hex_encode(word):
    str_encoded = ''

    if word == '':
        return str_encoded

    else:
        x = word.split('.')
        for i in x:
            if len(i) < 16:
                str_len = str(hex(len(i))).replace('0x', '0')
            else:
                str_len = str(hex(len(i))).replace('0x','')
            str_ = str(i).encode('utf-8')

            str_encoded += str_len + binascii.hexlify(str_).decode('utf-8')
    return str_encoded


def space_hex(s):
    if s == '':
        return ''
    return ' '.join(map('{}{}'.format, *(s[::2], s[1::2]))).strip()


# Extract number of answer only if valid
def extract_ans(hex_str):
    if hex_str == '':
        return 0
    if len(hex_str) < 16:
        return 0
    x = int(hex_str[12:16], 16)
    return x

# Extract ip from hex when only one answer
def extract_one_ip(hex_str):
    if hex_str == '':
        return ''
    size = len(hex_str)
    if size < 16:
        return ''

    x = hex_str[size - 8:]
    x = space_hex(x).split(' ')
    ip = ''
    for i in x:
        ip += str(int(i, 16)) + '.'
    ip = ip.rstrip(ip[-1])
    return ip

def send_udp_message(message, address, port):
    """send_udp_message sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")

def format_hex(hex):
    """format_hex returns a pretty version of a hex string"""
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)

parser = argparse.ArgumentParser(description="""Server""")
parser.add_argument('-f', type=str, help='File to read for root server', default='source_strings.txt', action='store', dest='in_file')
parser.add_argument('port', type=int, help='This is the root server port to listen', action='store')
# parser.add_argument('next_port', type=int, help='This is the top server port to listen', action='store')
args = parser.parse_args(argv[1:])
print(args)

# load the text file with the ip addresses as dictionary
domain_names = {}
with open(args.in_file) as f:
    for line in f:
        key = line.lower().strip()
        domain_names[key] = {'domain': key, 'ip': []}

print(domain_names)
print(domain_names['google.com']['domain'])

# Find next server ip address
thostname = ''


# Create a new socket
try:
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[S]: Server socket created")

except socket.error as error:
    print("Server socket error: {}".format(error))
    exit()

server_addr = ('', args.port)
ss.bind(server_addr)
ss.listen(1)

# print server info
host = socket.gethostname()
print("[S]: Server hostname is {}".format(host))
localhost_ip = socket.gethostbyname(host)
print("[S]: Server IP address is {}".format(localhost_ip))
print("[S]: Server port number is {}".format(args.port))

# Parts of the message
header = "AA AA 01 00 00 01 00 00 00 00 00 00"
end = "00 00 01 00 01"

while True:

    # accept a client
    csockid, addr = ss.accept()
    print("[S]: Got a connection request from a client at {}".format(addr))

    with csockid:
        while True:
            data = csockid.recv(512)
            data = data.decode('utf-8')

            body = space_hex(hex_encode(data))
            message = header + " " + body + " " + end
            response = send_udp_message(message, "8.8.8.8", 53)
            print(response)
            ans = extract_ans(response)

            # No answer close connection
            if ans == 0:
                break
            # Get the ip from the last
            elif ans == 1:
                sent = extract_one_ip(response)
                csockid.sendall(sent.encode('utf-8'))
            else:
                csockid.sendall('121.121.121.121'.encode('utf-8'))


            # try:
            #     if domain_names[data] and domain_names[data][1] != 'NS':
            #         print('[C]: {}'.format(data))
            #         print('[S]: {}'.format(domain_names[data]))
            #         csockid.sendall(str(domain_names[data][0] + ' ' + domain_names[data][1]).encode('utf-8'))
            #     else:
            #         csockid.sendall(str(thostname).encode('utf-8'))
            #
            #
            # except:
            #     if not data:
            #         break
            #     res_localhost = thostname
            #     print('[C]: {}'.format(data))
            #     print('[S]: {}'.format(res_localhost))
            #     csockid.sendall(str(res_localhost).encode('utf-8'))
# ss.close()
# exit()