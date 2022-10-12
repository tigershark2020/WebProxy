import cfscrape
import http.server
from urllib.parse import unquote
import netifaces as ni
import socketserver
import base64
import magic
import hashlib

LOCAL_IP = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
PORT = 8000

class Proxy(http.server.SimpleHTTPRequestHandler):

	def hash_bytes(self, binData):
		sha384_checksum = hashlib.sha384(binData).hexdigest().upper()
		return sha384_checksum

	def getData(self,base64_encoded_url):
		binData = bytes()
		try:
			url_decoded_base64_encoded_url = unquote(base64_encoded_url)
			base64_decoded_url = base64.decodebytes(url_decoded_base64_encoded_url.encode('utf8'))
			print(base64_decoded_url.decode('utf8'))
			scraper = cfscrape.create_scraper()
			sessionHeaders = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
			binData = scraper.get(base64_decoded_url, headers=sessionHeaders, stream=True, verify=False).content
		except Exception as error:
			print(error)
			binData = bytes(str("").encode("utf-8"))
		return binData

	def getMimeType(self, binData):
		mime = magic.Magic(mime=True)
		mime_type = ""
		try:
			mime_type = mime.from_buffer(binData)
		except Exception as e:
			mime_type = "application/octet-stream"
		return mime_type

	def do_GET(self):
		full_path = self.path
		url_params = full_path[1:]
		url_params_array = url_params.split("&")
		
		base64_encoded_url = ""
		for url_param in url_params_array:
			url_param_array = url_param.split("=")
			if url_param_array[0] == "base64_encoded_url":		
				base64_encoded_url = url_param_array[1]
				print(base64_encoded_url)
		
		binData = self.getData(base64_encoded_url)
		mime_type = self.getMimeType(binData)

		byteRangeKey = "range"
		
		byteRangeHeaderValue = ""
		if byteRangeKey in self.headers:
			byteRangeHeaderValue = self.headers[byteRangeKey]
		
		byteRangeStart = 0
		byteRangeEnd = 0

		if byteRangeHeaderValue != "":
			byteRangeHeaderValueArray = byteRangeHeaderValue.split("=")
			if len(byteRangeHeaderValueArray) > 1:
				byteRangeHeaderValueRangeArray = byteRangeHeaderValueArray[1].split("-")
				if len(byteRangeHeaderValueRangeArray) > 1:
					byteRangeStart = int(byteRangeHeaderValueRangeArray[0])
					byteRangeEnd = int(byteRangeHeaderValueRangeArray[1])
		
		content_length = len(binData)
		
		if byteRangeEnd != 0:
			# buffer = bytearray()
			# buffer[byteRangeStart:byteRangeStart+byteRangeEnd] = bytearray(data)
			# data = bytes(buffer)
			# content_length = byteRangeEnd - byteRangeStart
			print("Byte Ranges:\t" + str(byteRangeStart) + "-" + str(byteRangeEnd)) 

		self.send_response(200)
		self.send_header('Content-type',mime_type)
		self.server_version = 'Python'
		self.end_headers()

		try:
			if mime_type.startswith("text/"):
				encodedText = base64.b64encode(binData).decode("utf-8")
				self.wfile.write(bytes(encodedText, "utf8"))
			else:
				self.wfile.write(binData)
		except Exception as e:
			print(e)

		# req = urllib.request.urlopen(full_path)
        # self.copyfile(req, self.wfile)

httpd = socketserver.ThreadingTCPServer((LOCAL_IP, PORT), Proxy)
print("Serving on IP:\t",LOCAL_IP)
print("Serving on Port:\t", PORT)
httpd.serve_forever()
