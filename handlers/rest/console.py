import base64
import json
import socket
import traceback
from urllib.parse import urlparse, parse_qs, urlsplit

import tornado.ioloop
import tornado.iostream
import tornado.web
from tornado.options import options as opts
from tornado.iostream import StreamClosedError

from connman import ReDBConnection
from consolelist import ConsoleList
from exc import XenAdapterUnauthorizedActionException, EmperorException
from handlers.base import BaseWSHandler
from xenadapter.vm import VM


class ConsoleHandler(BaseWSHandler):
    def check_origin(self, origin):
        return True

    def initialize(self, pool_executor):
        super().initialize(pool_executor=pool_executor)

        username = opts.username
        password = opts.password
        self.auth_token = base64.encodebytes('{0}:{1}'.format
                                             (username,
                                              password).encode())


    async def open(self):
        '''
        This method proxies WebSocket calls to XenServer
        '''


        # Get VM vnc url
        url_parsed = urlparse(self.request.uri)
        try:
            secret = parse_qs(url_parsed.query)['secret'][0]
        except KeyError:
            await self.write_message("No argument secret")
            self.close()
            return


        async with ReDBConnection().get_async_connection() as conn:
            url = await ConsoleList.get_url_by_secret(conn, secret)

        vnc_url_parsed = urlsplit(url)
        port = vnc_url_parsed.port
        if port is None:
            port = 80 # TODO: If scheme is HTTPS, use 443
        self.sock = socket.create_connection((vnc_url_parsed.hostname, port))
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.sock.setblocking(0)
        self.halt = False
        self.translate = False
        self.key = None

        uri = f'{vnc_url_parsed.path}?{vnc_url_parsed.query}'
        lines = [
            'CONNECT {0} HTTP/1.1'.format(uri),  # HTTP 1.1 creates Keep-alive connection
            'Host: {0}'.format(opts.vmemperor_host),
            #   'Authorization: Basic {0}'.format(self.auth_token),
        ]
        self.sock.send('\r\n'.join(lines).encode())
        self.sock.send(b'\r\nAuthorization: Basic ' + self.auth_token)
        self.sock.send(b'\r\n\r\n')
        tornado.ioloop.IOLoop.current().spawn_callback(self.server_reading)

    def on_message(self, message):
        assert (isinstance(message, bytes))
        self.sock.send(message)

    def select_subprotocol(self, subprotocols):
        if 'binary' in subprotocols:
            proto = 'binary'
        else:
            proto = subprotocols[0] if len(subprotocols) else ""


        return proto

    async def server_reading(self):
        try:
            data_sent = False
            http_header_read = False
            stream = tornado.iostream.IOStream(self.sock)
            while self.halt is False:
                try:
                    if not data_sent:
                        data = await stream.read_bytes(100, partial=True)
                        if not http_header_read:
                            notok = b'200 OK' not in data
                            if notok:
                                self.log.error(f"Unable to open VNC Console {self.request.uri}: Error: {data}")
                                self.write_message(data)
                                self.close()
                                return
                            else:
                                http_header_read = True

                        try:
                            index = data.index(b'RFB')
                        except ValueError:
                            self.log.warning("server_reading: 200 OK returned, but no RFB in first data message. Continuing")
                            continue

                        data = data[index:]
                        data_sent = True
                    else:
                        data = await stream.read_bytes(1024, partial=True)
                except StreamClosedError as e:
                    self.log.info(f"{self.request.uri}: Stream closed: {e}")
                    self.halt = True
                    self.close()
                    break
                await self.write_message(data, binary=True)

        except:
            if self.halt is False:
                traceback.print_exc()
            else:
                pass

    def on_close(self):
        self.halt = True

        try:
            self.sock.send(b'close\n')
        except:
            pass
        finally:
            self.sock.close()