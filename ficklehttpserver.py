__author__ = 'reggie'


import re, json
from socket import *


import time
import datetime
import base64
import threading
import http.server

from threading import *
from ficklepageindex import *

CONTEXT = None
HTTP_TCP_PORT = 9998


class Head(object):

    def __init__(self, header):
        self.params_hash = {}
        self.params_list = []
        self.params_string = ""
        hd = re.findall(r"(GET|POST) (?P<value>.*?)\s", header)
        try:
            if len(hd[0][1].split("?")) > 1:
                parlist = hd[0][1].split("?")[1].split("&")
                for p in parlist:
                    key = p.split("=")[0]
                    value = p.split("=")[1]
                    self.params_hash[key] = value
                    self.params_list.append(value)
                    self.params_string += str(value)+","

                self.params_string = self.params_string[:-1]

            serv = hd[0][1].split("?")[0].split("/")
            self.module = serv[len(serv)-2]
            self.method = serv[len(serv)-1]
        except:
            self.module = None
            self.method = None


class HttpServer(Thread):
     def __init__(self):
         Thread.__init__(self)


         pass

     def run(self):
        HOST_NAME = '0.0.0.0' # !!!REMEMBER TO CHANGE THIS!!!
        PORT_NUMBER = HTTP_TCP_PORT # Maybe set this to 9000.

        server_class = http.server.HTTPServer
        httpd = server_class((HOST_NAME, PORT_NUMBER),  MyHandler)
        #log.info("Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        #log.info("Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        #log.debug("Request "+s.path)
        servers = PageIndex()
        default_page = "<html><h1>Oooops No Page Found</h1></html>"

        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        path_parts = s.path.split("/")
        if len(path_parts) > 0:
            key = path_parts[1]

            if servers.has_key(key):
                (q, o) = servers.get_conn(key)
                q.put("GET")
                mesg = o.get()
                msm = str(mesg)
                time.sleep(1)
                if not msm == "400":
                    print("HTML: "+msm)
                    s.wfile.write(msm.encode('utf-8'))
                else:
                    s.wfile.write(default_page.encode('utf-8'))
            else:
                s.wfile.write(default_page.encode('utf-8'))


        if s.path == "/":
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write("<html><head><title>Fickle Page</title></head>")
            s.wfile.write("<body><p>Default Page</p>")
            s.wfile.write("</body></html>")


        # if s.path == "/d3":
        #     s.send_response(200)
        #     s.send_header("Content-type", "text/html")
        #     s.end_headers()
        #
        #     context.getProcGraph().dumpGraphToFile("force.json")
        #     with open("force.html") as f:
        #         content = f.read()
        #     f.close()
        #
        #     s.wfile.write(content)
        # if s.path == "/force.json":
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #
        #     #context.getProcGraph().dumpGraphToFile("force.json")
        #     with open("force.json") as f:
        #         content = f.read()
        #     f.close()
        #     s.wfile.write(content)
        #
        #
        # if s.path =="/graph.json":
        #     rep = context.getProcGraph().dumpGraph()
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #     s.wfile.write(str(rep))
        #
        # if s.path =="/packets.json":
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #     rep = json.dumps(dict(context.getPktShelve()))
        #
        #     s.wfile.write(str(rep))
        #
        # if s.path == "/counters.json":
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #     rep = ""
        #     for x in PmkSeed.iplugins.keys():
        #        klass = PmkSeed.iplugins[x]
        #        rep = rep + "\n" + klass.get_state_counters()
        #     s.wfile.write(str(rep))
        #
        # if s.path == "/stats.json":
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #     tm = time.time()
        #     ip = str(context.get_local_ip())
        #     if not ip:
        #         ip = "NONE"
        #     rep = '{"timestamp":'+str(tm)+',"ip":'+ip+'}\n'
        #     rep = rep + "{"
        #     for x in PmkSeed.iplugins.keys():
        #        klass = PmkSeed.iplugins[x]
        #        rep = rep + klass.get_name() + ","
        #
        #     rep = rep[0:len(rep)-1]
        #     rep = rep + "}"
        #
        #     total_in = 0
        #     total_out = 0
        #     for x in PmkSeed.iplugins.keys():
        #        klass = PmkSeed.iplugins[x]
        #        rep = rep + "\n" + klass.get_state_counters()
        #        tin, tout = klass.get_all_counters()
        #        total_in += tin
        #        total_out += tout
        #     rep += '\n'
        #     rep = rep + '{"total_in":'+str(total_in)+',"total_out":'+str(total_out)+'}'
        #     s.wfile.write(str(rep))
        #
        # if "status" in s.path:
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #     rep = ""
        #     parts = s.path.split("?")
        #     pkt_id = parts[1]
        #     pkt = context.get_pkt_from_shelve(pkt_id)
        #     if pkt:
        #         rep += json.dumps(pkt)
        #     else:
        #         rep += "{unavailable_info}"
        #
        #     s.wfile.write(str(rep))
        #
        #
        #
        # if "submit" in s.path:
        #     s.send_response(200)
        #     s.send_header("Content-type", "application/json")
        #     s.end_headers()
        #
        #     parts = s.path.split("?")
        #     container = "None"
        #     #print parts[1]
        #     pkt_dec = base64.decodestring(parts[1])
        #     log.debug("Decoded packet: "+pkt_dec)
        #     # pktd = parts[1]
        #     pktdj = json.loads(pkt_dec)
        #     pkt_len = len(pktdj)
        #
        #     stag_p = pktdj[pkt_len - 1]["stag"].split(":")
        #
        #     pkt_id = None
        #     pkt = pktdj
        #     if pkt[0]["state"] == "MERGE":
        #         pkt_id= pkt[0]["ship"]+":"+pkt[0]["container"]+":"+pkt[0]["box"]+":"+pkt[0]["fragment"]+":M"
        #     else:
        #         pkt_id= pkt[0]["ship"]+":"+pkt[0]["container"]+":"+pkt[0]["box"]+":"+pkt[0]["fragment"]
        #
        #     if len(stag_p) < 3:
        #         group = "A"
        #         type = stag_p[0]
        #         tag = stag_p[1]
        #     else:
        #         group = stag_p[0]
        #         type = stag_p[1]
        #         tag = stag_p[2]
        #
        #     dt = datetime.datetime.now()
        #     context.getTx().put((group, tag,type,pktdj))
        #
        #
        #     log.debug("Submit packet through http: "+pkt_id)
        #     rep = '{"packet_ref":'+pkt_id+', "timestamp":'+str(dt)+'}'
        #
        #     s.wfile.write(rep)
        #
        #     # s.wfile.write("<html><head><title>Pumpkin Web</title></head>")
        #     # s.wfile.write("<body><p>Submitted Packet: "+pkt_id+" "+str(dt)+"</p>")
        #     # s.wfile.write("</body></html>")
        #
        #
        # if s.path == "/":
        #     s.send_response(200)
        #     s.send_header("Content-type", "text/html")
        #     s.end_headers()
        #     s.wfile.write("<html><head><title>Pumpkin Web</title></head>")
        #     s.wfile.write("<body><p>Loaded Seeds</p>")
        #     for x in PmkSeed.iplugins.keys():
        #        klass = PmkSeed.iplugins[x]
        #        s.wfile.write("<p>"+klass.get_name()+"</p>")
        #     s.wfile.write("</body></html>")

        #s.wfile.write("<html><head><title>Title goes here.</title></head>")
        #s.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        #s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        #s.wfile.write("</body></html>")



