from http.server import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)
Request=None

class RequestHandler_httpd(BaseHTTPRequestHandler):
	def do_GET(self):
		global Request
		messagetosend=bytes('Hello World!', "utf")
		self.send_response(200)
		self.send_header('Content-Type', 'text/plain')
		self.send_header('Content-Length', len(messagetosend))
		self.end_headers()
		self.wfile.write(messagetosend)
		Request=self.requestline
		Request=Request[5: int(len(Request)-9)]
		print(Request)
		if Request == 'on':
			GPIO.output(2, True)
		if Request == 'off':
			GPIO.output(2, False)
		return

server_address_httpd=('192.168.1.55',8080)
httpd=HTTPServer(server_address_httpd, RequestHandler_httpd)
print('Starting server:')
httpd.serve_forever()
GPIO.cleanup()
