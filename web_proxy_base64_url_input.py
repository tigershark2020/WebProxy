import cfscrape
import http.server
import socket
import socketserver
import base64

LOCAL_IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

class Proxy(http.server.SimpleHTTPRequestHandler):
	def getHTML(self,url):
		htmlData = bytes()
		try:
			base64DecodedURL = base64.decodebytes(url.encode('utf8'))
			print(base64DecodedURL)
			scraper = cfscrape.create_scraper()
			sessionHeaders = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
			htmlData = scraper.get(base64DecodedURL, headers=sessionHeaders).content
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
		# req = urllib.request.urlopen(full_path)
        # self.copyfile(req, self.wfile)

httpd = socketserver.ThreadingTCPServer((LOCAL_IP, PORT), Proxy)
print("Serving on IP:\t",LOCAL_IP)
print("Serving on Port:\t", PORT)
httpd.serve_forever()
