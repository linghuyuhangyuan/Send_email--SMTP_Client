import base64
from socket import *
from email.base64mime import body_encode
from typing import Tuple


class Client:
    def __init__(self, client_socket: socket) -> None:
        self._socket = client_socket
        self._sent_mails = []
        self._drafts = []
        self._contacts = {}
        recv = self._socket.recv(1024).decode()
        assert "220" == recv[:3], f"connect to server failed:{recv}"
        print(recv)

    def send_msg(self, msg: bytes, receive_size: int = 1024) -> str:
        self._socket.send(msg)
        return self._socket.recv(receive_size).decode()

    def send_all_msg(self, msg: bytes, receive_size: int = 1024) -> str:
        self._socket.sendall(msg)
        return self._socket.recv(receive_size).decode()

    def add_contact(self, name: str, address: str) -> None:
        self._contacts[name] = address
        print(f"contact {name}: {address} added!\n")

    @staticmethod
    def base64_encode(msg: str) -> bytes:
        msg = base64.b64encode(msg.encode()).decode() + '\r\n'
        return msg.encode()

    def hello(self, msg: str = 'HELO Alice\r\n') -> None:
        recv = self.send_msg(msg.encode())
        assert '250' == recv[:3], f"helo failed:{recv}"
        print(recv)
    
    def auth_login(self, username: str, password: str) -> None:
        msg = "AUTH LOGIN\r\n".encode()
        recv1 = self.send_all_msg(msg)
        if recv1[:3] != '334':
            print(f"auth message failed:{recv1}")
            return False

        username = self.base64_encode(username)
        recv2 = self.send_all_msg(username)
        if recv2[:3] != '334':
            print(f"auth username failed:{recv2}")
            return False

        password = self.base64_encode(password)
        recv3 = self.send_msg(password)
        if recv3[:3] != '235':
            print(f"auth password failed:{recv3}")
            return False

        print(recv3)
        return True

    def mail_from(self, from_addr: str) -> None:
        recv = self.send_all_msg(('MAIL FROM: <' + from_addr + '>\r\n').encode())
        assert '250' == recv[:3], f"send mail from failed:{recv}"

    def rcpt_to(self, to_addr: str) -> None:
        recv = self.send_all_msg(('RCPT TO: <' + to_addr + '>\r\n').encode())
        assert '250' == recv[:3], f"send rcpt to failed:{recv}"

    def send_data(self, data_content: str, from_address: str, to_address: str, subject: str = None,
                  content_type: str = "text/plain") -> None:
        recv1 = self.send_msg('DATA\r\n'.encode())
        assert '354' == recv1[:3], f"send DATA failed:{recv1}"
        message = 'from:' + from_address + '\r\n'
        message += 'to:' + to_address + '\r\n'
        if subject is not None:
            message += 'subject:' + subject + '\r\n'
        message += 'Content-Type:' + content_type + '\t\n'
        message += '\r\n' + data_content + "\r\n.\r\n"
        recv2 = self.send_all_msg(message.encode())
        assert '250' == recv2[:3], f"send data content failed:{recv2}"
        sent_mail = {"to": to_address, "cont": message}
        self._sent_mails.append(sent_mail)
        print(f"data has sent to: {to_address}\n")

    def send_mail(self, from_address: str, to_address: str, subject: str, msg: str) -> None:
        """
        send whole mail
        """
        if to_address in self._contacts:
            to_address = self._contacts[to_address]
        self.mail_from(from_address)
        self.rcpt_to(to_address)
        if subject:
            self.send_data(msg, from_address, to_address, subject)
        else:
            self.send_data(msg, from_address, to_address)

    def quit(self) -> None:
        self._socket.sendall('QUIT\r\n'.encode())

    def close_connect(self) -> None:
        self._socket.close()

    def get_sent_mails(self) -> None:
        return self._sent_mails

    def store_in_drafts(self, subject: str, msg: str) -> None:
        self._drafts.append({"sub": subject, "msg": msg})

    def get_draft(self, no: int) -> Tuple[str, str]:
        if no >= len(self._drafts) or no < 0:
            return None
        draft = self._drafts[no]
        return draft['sub'], draft['msg']
    
    def get_drafts(self):
        return self._drafts
    
    def get_draft_len(self) -> int:
        return len(self._drafts)
    
    def get_contacts(self):
        return self._contacts
    
    def get_contact(self, name):
        try:
            return self._contacts[name]
        except KeyError:
            return None 
