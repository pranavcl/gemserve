from pathlib import Path
from logging import basicConfig, getLogger, INFO
from OpenSSL import crypto
from traceback import print_exc
from socket import socket
from ssl import create_default_context, Purpose, SSLSocket
from sys import argv, exit
from os import path, mkdir

basicConfig()
logger = getLogger(__name__)
logger.setLevel(INFO)

HOST = "0.0.0.0"
PORT = 1965
MAXCONN = 5
base_url = "."

if len(argv) > 1:
    base_url = argv[1]

context = create_default_context(Purpose.CLIENT_AUTH)

def end():
    input("Press Enter to exit...")
    exit()

if not path.exists(base_url):
    logger.error(f"❌ Directory {base_url} does not exist")
    end()

def gen_index():
    folder_path = f"{base_url}/docs"
    if not path.exists(folder_path):
        logger.info(f"⏳ Creating {base_url}/docs/ folder...")
        try:
            mkdir(folder_path)
            logger.info(f"✅ Created {base_url}/docs/ folder")
        except:
            print_exc()
            logger.error("❌ Failed to create docs file")

    if not Path(f"{base_url}/docs/index.gmi").is_file():
        logger.info(f"⏳ Creating {base_url}/docs/index.gmi...")
        try:
            f = open(f"{base_url}/docs/index.gmi", "w")
            f.write(
"""
# Congratulations! Your Gemini capsule is up :D

This page (index.gmi) is stored in a folder named "docs". Go ahead and open it in a text editor like Notepad. Make some changes to it and refresh your browser to see them live.

## How to format GMI

```gmi
# Heading 1
## Heading 2
### Heading 3

=> page2.gmi Internal Link Text
=> gemini://geminiprotocol.net External Link Text

> This is a blockquote
> Great for poetry, notes, or messages.

Lists

* List item 1
* List item 2
* List item 3
```

## How to host your capsule on the internet

You'll need a real TLS certificate (not a self-signed one) for your public domain. Stop the GemServe server, delete the cert.pem and key.pem files and create new ones with certbot:

```bash
certbot certonly --standalone -d your.domain.name
```

Add DNS records on your provider's website like so:

* Record Type: A
* Name: @
* Value: [Your IPv4 address]

You can also add a AAAA record if your machine has an IPv6 address:

* Record Type: AAAA
* Name: @
* Value: [Your IPv6 address]

## Further Resources

=> gemini://geminiquickst.art Gemini Quickstart Guide
=> gemini://geminiprotocol.net Official Gemini protocol capsule
=> gemini://geminiprotocol.net/docs/gemtext.gmi Gemtext markup introduction
""")
            f.close()
            logger.info(f"✅ Created /docs/index.gmi")
        except:
            print_exc()
            logger.error("❌ Failed to create index file")

def gen_cert_key():
    if Path(f"{base_url}/cert.pem").is_file() and Path(f"{base_url}/key.pem").is_file():
        logger.info("✅ Certificate and private key exist")
    else:
        logger.info("⏳ Creating certificate and private key...")

        try:
            key = crypto.PKey()
            key.generate_key(crypto.TYPE_RSA, 2048)

            cert = crypto.X509()
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10*365*24*60*60) # 10 years
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(key)
            cert.sign(key, "SHA1")

            with open(f"{base_url}/cert.pem", "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

            with open(f"{base_url}/key.pem", "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

            logger.info("✅ Created cert.pem and key.pem")
        except:
            print_exc()
            logger.error("❌ Failed to create cert.pem and key.pem")
            end()

def serve():
    with socket() as sock:
        try:
            sock.bind((HOST, PORT))
            sock.listen(MAXCONN)
            sock.settimeout(1.0)
            logger.info(f"📥 Server started on port 1965. Open gemini://localhost in your Gemini browser to view your website.")
        except:
            print_exc()
            logger.error("❌ Failed to start server")
            end()

        try:
            while True:
                try:
                    client, addr = sock.accept() # type: ignore
                except TimeoutError:
                    continue  # Timeout, loop again to check for KeyboardInterrupt
                except Exception:
                    print_exc()
                    continue

                conn: SSLSocket | None = None

                try:
                    conn = context.wrap_socket(client, server_side=True)
                except:
                    print_exc()
                    logger.error("❌ Failed to bind socket to TLS socket")
                    logger.info("ℹ️ This is likely because your browser does not trust the self-signed certificate created by GemServe.\nTo fix this, add an exception for localhost in your browser (Press Ctrl+Shift+U in Lagrange).")

                if conn == None:
                    continue

                try:
                    request = conn.recv(1024).decode().strip()
                    # print(f"Request: {request}")
                    # print(f"Address: {addr}")
                    
                    splits = request.split("/")
                    requested_file = splits[len(splits)-1]

                    if(requested_file == ""):
                        requested_file = "index.gmi"

                    if not Path(f"{base_url}/docs/{requested_file}").is_file():
                        logger.error(f"❌ File not found: {base_url}/docs/{requested_file}")
                        conn.send(b"51 Not Found\r\n")
                        continue

                    f = open(f"{base_url}/docs/{requested_file}", "r")
                    res = f.read()
                    f.close()

                    conn.send(b"20 text/gemini\r\n")
                    conn.send(res.encode())
                finally:
                    conn.close()
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user (KeyboardInterrupt)")
            sock.close()
            end()

print("GemServe v1.0\nCreated by pranav.cl\n")
gen_index()
gen_cert_key()
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
serve()
