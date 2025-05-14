import os

from flask import Flask
from  __init__ import create_app

app = create_app()
    
#certs_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'certs'))

#cert_path = os.path.join(certs_folder, 'cert.pem')
#key_path = os.path.join(certs_folder, 'key.pem')

#app.run(ssl_context=(cert_path, key_path), debug=True)


