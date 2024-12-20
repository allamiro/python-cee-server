import os
import sys
import signal
import logging
import logging.handlers
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from xml.etree.ElementTree import ParseError, fromstring

# This script:
# - Creates an HTTP server on port 8000.
# - Expects to receive CEE audit events (JSON, XML, or plain text) via HTTP PUT requests at /cee endpoint.
# - Writes incoming audit event data to separate log files based on format (json, xml, text).
# - Validates incoming JSON and XML for correctness and rejects malformed requests.
# - For text/plain content, data is logged as-is without validation.
# - Gracefully shuts down on SIGINT/SIGTERM, allowing ongoing requests to complete and flushing logs.

LOG_DIR = "/Users/ghost/Desktop/GIT-PROJECTS/cee-server/"
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except OSError as e:
    print(f"Failed to create log directory {LOG_DIR}: {e}", file=sys.stderr)
    sys.exit(1)

def setup_logger(log_type):
    log_file_path = os.path.join(LOG_DIR, f"cee_events_{log_type}.log")
    handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when='D', interval=1, backupCount=7, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(log_type)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

json_logger = setup_logger("json")
xml_logger = setup_logger("xml")
text_logger = setup_logger("text")

def is_valid_json(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def is_valid_xml(data):
    try:
        fromstring(data)
        return True
    except ParseError:
        return False

class CEERequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path != "/cee":
            self.send_error(404, "Endpoint not found")
            return

        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            self.send_error(400, "No data provided")
            return

        raw_data = self.rfile.read(length)
        event_str = raw_data.decode('utf-8', errors='replace')
        content_type = self.headers.get('Content-Type', '')

        if "application/json" in content_type:
            if is_valid_json(event_str):
                json_logger.info(event_str)
                log_type = "json"
            else:
                self.send_error(400, "Invalid JSON format.")
                return
        elif "application/xml" in content_type or "text/xml" in content_type:
            if is_valid_xml(event_str):
                xml_logger.info(event_str)
                log_type = "xml"
            else:
                self.send_error(400, "Invalid XML format.")
                return
        elif "text/plain" in content_type:
            text_logger.info(event_str)
            log_type = "text"
        else:
            self.send_error(400, "Unsupported content type. Use JSON, XML, or plain text.")
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"{log_type.upper()} log received and recorded".encode('utf-8'))

    def do_GET(self):
        if self.path == "/cee":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"CEE logging endpoint active")
        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        # Override to reduce console output noise
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(),
                                               self.log_date_time_string(),
                                               format%args))

def graceful_shutdown(signum, frame):
    httpd.shutdown()  # allow current requests to complete
    httpd.server_close()
    logging.shutdown()  # flush and close all log handlers

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CEERequestHandler)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        logging.shutdown()
