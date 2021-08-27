import http.server
import socket
import socketserver
import cfscrape
import base64

local_ip = socket.gethostbyname(socket.gethostname())
PORT = 8000

class Proxy(http.server.SimpleHTTPRequestHandler):
	def getHTML(self,url):
		htmlData = bytes()
		try:
			scraper = cfscrape.create_scraper()
			sessionHeaders = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
			htmlData = scraper.get(url, headers=sessionHeaders).content
		except Exception as error:
			print(error)
			htmlData = bytes(str("").encode("utf-8"))
		return htmlData

	def do_GET(self):
		full_path = self.path
		url = full_path[1:]
		htmlData = self.getHTML(url)
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

		htmlEncoded = encoded = base64.b64encode(htmlData).decode("utf-8")
		self.wfile.write(bytes(htmlEncoded, "utf8"))

httpd = socketserver.ThreadingTCPServer((local_ip, PORT), Proxy)
print("serving at port ", PORT)
httpd.serve_forever()
