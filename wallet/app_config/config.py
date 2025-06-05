# coding: latin-1
###############################################################################
# Copyright (c) 2023 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
"""
This config.py contains configuration data for the Wallett Web service. 

NOTE: You should only change it if you understand what you're doing.
"""

import os
from flask import session


class ConfService:

    ###################################################################################

    service_url = os.getenv("service_url")
    #service_url = "http://127.0.0.1:5000/"
    #service_url = "https://dev.tester.issuer.eudiw.dev/"

    ###################################################################################

    doctype_pid = "eu.europa.ec.eudiw.pid.1"
    scope_pid = "eu.europa.ec.eudiw.pid.1 openid"

    doctype_mdl = "org.iso.18013.5.1.mDL"
    scope_mdl = "org.iso.18013.5.1.mDL openid"

    doctype_qeaa = "eu.europa.ec.eudiw.qeaa.1"
    scope_qeaa = "eu.europa.ec.eudiw.qeaa.1 openid"

    jwt = "eyJ0eXAiOiJvcGVuaWQ0dmNpLXByb29mK2p3dCIsImFsZyI6IkVTMjU2IiwiandrIjp7Imt0eSI6IkVDIiwiY3J2IjoiUC0yNTYiLCJ4Ijoid1V1UDJPbHdIZWZlRS1ZMTZXajdQSEF6WjBKQVF5ZXZxV01mZDUtS21LWSIsInkiOiJZVy1iOE8zVWszTlVyazlvWnBBVDFsYVBlQWdpTlF3RGNvdFdpd0JGUTZFIn19.eyJhdWQiOiJodHRwczovL3ByZXByb2QuaXNzdWVyLmV1ZGl3LmRldi9vaWRjIiwibm9uY2UiOiJTcUdTMzc0eUFheFpIc254aUs5NWVnIiwiaWF0IjoxNzA0ODg2ODU1fQ.IdmxwbfJIKwcaqvADp6bzV2u-o0UwKIVmo_kQkc1rZHQ9MtBDNbO21NoVr99ZEgumTX8UYNFJcr_R95xfO1NiA"
    cwt = "2D3ShFidowEmA3RvcGVuaWQ0dmNpLXByb29mK2N3dGhDT1NFX0tleaYBAgJYKzFlNUFZOUV5QjAxWG5VemE2THBKemswMm42WV9BbW1uU2IwRkJlTlZWclUDJiABIVggPSxQrD2zl0_mXcAqz1mgqSeBoBhnmx2yxBEprBY8F20iWCDFXx9uLUVKixS6ct64s24uQmKqZjpMqIye6v4afbBHXaBYYKQBbHRyYWNrMV9saWdodAN4Gmh0dHBzOi8vdHJpYWwuYXV0aGxldGUubmV0BhpmX9yrClgrdi0xYi1uODJrRUpHYkhST1Nla0dzbVIteEV1YW1DeFlfVDB0WHRRTi1kWVhARhw4yBJ7cMouSRR42lnIdkJVUT6bFZaNFzZydros7Nr02oOjQ774Zthvb6UWJkhZgF1NbPfYNrYVLtphpCv3WQ"
    ###################################################################################
    format_vc_sd_jwt = "vc+sd-jwt"
    format_mso_mdoc = "mso_mdoc"

    vct_mdl_jwt = "eu.europa.ec.eudiw.mdl_jwt_vc_json"
    credential_identifier_mdl_mdoc = "eu.europa.ec.eudiw.mdl_mdoc"
    credential_identifier_pid_jwt = "eu.europa.ec.eudiw.pid_jwt_vc_json"
    credential_identifier_pid_mdoc = "eu.europa.ec.eudiw.pid_mdoc"

    ################################################################################### V 0.5

    # serv = "https://issuer.eudiw.dev/"
    serv = os.getenv("serv_url")

    credential_offer = serv + "credential_offer"

    v05_metadata1_na = serv + ".well-known/openid-configuration"
    
    v05_metadata2_na = "/.well-known//openid-credential-issuer"
    
    v05_redirect_uri = service_url + "redirect_na"

    ### Pre Auth

    V05_preauth_form = serv + "dynamic/preauth"

    v05_preauth_redirect_uri = serv + "preauth-code"

    ###################################################################################
