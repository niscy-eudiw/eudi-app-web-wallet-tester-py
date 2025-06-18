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
This wallet_pid.py file is the blueprint of the wallett Web service.
"""

import json
import os
from flask import (
    Blueprint,
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
)
import requests
from requests.auth import HTTPBasicAuth
import re
from app_config.config import ConfService as cfs

V05 = Blueprint("V05", __name__, url_prefix="/")

V05.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@V05.route('/', methods=['GET','POST'])
def wallet():
    session.clear()
    return render_template('V05/v05_wallett_menu.html', credential_offer = cfs.credential_offer)


@V05.route('/auth', methods=['GET','POST'])
def auth():
    session['authmode'] = 'auth'
    return redirect('/getmeta1_na')

@V05.route('/getmeta1_na', methods=['GET','POST'])
def getmeta1_na():
    return render_template('V05/getmetadata1.html', url = cfs.v05_metadata1_na)


@V05.route('/metadata1_na', methods=['GET','POST'])
def metadata1_na():

    url = cfs.v05_metadata1_na
    response = requests.get(url, verify=False)
    
    session['service_url'] = response.json()["issuer"]
    session['1_pushed_authorization_request_endpoint'] = response.json()['pushed_authorization_request_endpoint']
    session['2_authorization_endpoint'] = response.json()['authorization_endpoint']
    session['3_token_endpoint'] = response.json()['token_endpoint']
    session['4_credential_endpoint'] = response.json()['credential_endpoint']

    return render_template('V05/metadata2.html', metadata = response.json(), url = url)
    

@V05.route('/getmeta_na', methods=['GET','POST'])
def getmeta_na():
    url = session['service_url'] + cfs.v05_metadata2_na
    return render_template('V05/getmetadata2.html', url = url)

@V05.route('/metadata_na', methods=['GET','POST'])
def metadata_na():

    url = session['service_url'] + cfs.v05_metadata2_na
    response = requests.get(url, verify=False)

    session['6_deferred_endpoint'] = response.json()['deferred_credential_endpoint']
    session['7_notification_endpoint'] = response.json()["notification_endpoint"]
    session['credential_identifier'] = list(response.json()['credential_configurations_supported'])
    session['url_nonce'] = response.json()['nonce_endpoint']

    scope = []
    vct = []
    display = []
    for elemento2_key, elemento2_value in response.json()['credential_configurations_supported'].items():
        value_scope = elemento2_value["scope"]
        scope.append(value_scope)
        session[elemento2_key] = value_scope
        if("sd_jwt" in elemento2_key):
            value_vct = elemento2_value["vct"]
            vct.append(value_vct)
            session[elemento2_key] = value_vct

        display_name = elemento2_value["display"]
        display_name = display_name[0]["name"]
        display.append(display_name)

    session["display_name"] = display
    session['vct_list'] = vct
    
    credential_configurations = response.json()["credential_configurations_supported"]
    result = {}
 
    for name, config in credential_configurations.items():
        format_value = config.get("format")
        result[name] = format_value

    session['format'] = result
    
    session['scope_list'] = scope
    unique = set(scope)
    scope_list = list(unique)

    if(session['authmode'] == 'preauth'):
        return redirect('token_preAuth_payload')
    elif(session['authmode'] == 'credential_offer'):
        return render_template('V05/metadata1_cred_offer.html', metadata = response.json(), url = url)

    return render_template('V05/metadata1.html', metadata = response.json(), url = url)


@V05.route('/menu_options', methods=['GET','POST'])
def menu_options():
    return render_template('V05/menu_options.html', 
                           credential_identifier = session['credential_identifier'], scope_list = session['scope_list'], 
                           display_name = session["display_name"])

@V05.route('/manager', methods=['POST'])
def manager():
    session['par'] = request.form.getlist('par')
    session['scopeOption'] = request.form.getlist('scopeOption')
    session['authorization_details_Option'] = request.form.getlist('authorization_details_Option')


    print("Opções selecionadas do par:", session['par'])
    print("Opções adicionais do scopeOption:", session['scopeOption'])
    print("Opções adicionais do authorization_details_Option:", session['authorization_details_Option'])
    
    length = len(session['par'])
    if(length == 2):
        scope = ''
        indice = 0
        for vi in session['credential_identifier']:
            for eachOne in session['scopeOption']:
                if(eachOne == vi):
                    scope = scope + ' ' + session['scope_list'][indice] + ' openid'
            indice = indice + 1
    
        aux = ''
        for option in session['authorization_details_Option']:
            for eachOne in session['format']:
                if(option == eachOne):
                    if "mso_mdoc" in session['format'][eachOne]:
                        aux = aux + '{"type": "openid_credential", "credential_configuration_id": "' + eachOne +  '"}, '
                    if "dc+sd-jwt" in session['format'][eachOne]:
                        aux = aux + '{"type": "openid_credential", "format": "dc+sd-jwt", "vct": "' + eachOne + '"}, '

        aux = '[' + aux
        aux = aux.rstrip(', ') + ']'
        session['auth_detail'] = aux
        session['scope'] = scope

        if(session['auth_opt'] == 'pkcepar'):
            payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
        elif(session['auth_opt'] == 'par'):
            payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
        elif(session['auth_opt'] == 'pkce'):
            payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
        elif(session['auth_opt'] == ''):
            session['payload'] = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
            return redirect("/authorization_na_payload")
        
        return render_template('V05/walletPushedRegistration_auth_details_payload_scope.html', 
                                    url = session['1_pushed_authorization_request_endpoint'], red = cfs.v05_redirect_uri, scope = scope,
                                    auth_detail = session['auth_detail'], payload = payload)
    
    # lenghScope = len(session['scopeOption'])
    # scope = ''
    # indice = 0
    # if(lenghScope > 1):
    #     for vi in session['credential_identifier']:
    #         for eachOne in session['scopeOption']:
    #             if(eachOne == vi):
    #                 scope = scope + ' ' + session['scope_list'][indice] + ' openid'
    #         indice = indice + 1

    #     scope = scope.replace(" ", "", 1)

    #     session['scope'] = scope

    #     if(session['auth_opt'] == 'pkcepar'):
    #         payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope']
    #     elif(session['auth_opt'] == 'par'):
    #         payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope']
    #     elif(session['auth_opt'] == 'pkce'):
    #         payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope']

    #     return render_template('V05/walletPushedRegistration_na_payload.html', 
    #                                 url = session['1_pushed_authorization_request_endpoint'], red = cfs.v05_redirect_uri, scope = session['scope'], payload = payload)
        
    

    if(session['par'][0] == 'scope'):
        scope = ''
        #vct = ''
        indice = 0
        #ind_vct = 0
        for vi in session['credential_identifier']:
            for eachOne in session['scopeOption']:
                if(eachOne == vi):
                    #if "mso_mdoc" in session['format'][eachOne]:
                    scope = scope + ' ' + session['scope_list'][indice] + ' openid' 
                        
                    # elif "dc+sd-jwt" in session['format'][eachOne]:
                    #     vct = vct + ' ' + session['vct_list'][ind_vct]
                    #     ind_vct = ind_vct + 1
                        
            indice = indice + 1
        #session['vct'] = vct
        session['scope'] = scope

        if(session['auth_opt'] == 'pkcepar'):
            payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope']
        elif(session['auth_opt'] == 'par'):
            payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope']
        elif(session['auth_opt'] == 'pkce'):
            payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope']
        elif(session['auth_opt'] == ''):
            session['payload'] = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope']
            return redirect("/authorization_na_payload")
        
        return render_template('V05/walletPushedRegistration_na_payload.html', url = session['1_pushed_authorization_request_endpoint'], 
                               red = cfs.v05_redirect_uri, scope = scope, payload = payload)
        
    elif(session['par'][0] == 'authorization_details'):
        aux = ''
        for option in session['authorization_details_Option']:
            for eachOne in session['format']:
                if(option == eachOne):
                    if "mso_mdoc" in session['format'][eachOne]:
                        aux = aux + '{"type": "openid_credential", "credential_configuration_id": "' + eachOne +  '"}, '
                    if "dc+sd-jwt" in session['format'][eachOne]:
                        match = re.search(r"^eu\.europa\.ec\.eudi\.([^_]+)", eachOne)
                        match = match.group(1) if match else None

                        for vct in session['vct_list']:
                            if(match in vct):
                                aux = aux + '{"type": "openid_credential", "format": "dc+sd-jwt", "vct": "' + vct + '"}, '
            
        aux = '[' + aux
        aux = aux.rstrip(', ') + ']'
        session['auth_detail'] = aux
        
        if(session['auth_opt'] == 'pkcepar'):
            payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&authorization_details=' + session['auth_detail']
        elif(session['auth_opt'] == 'par'):
            payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&authorization_details=' + session['auth_detail']
        elif(session['auth_opt'] == 'pkce'):
            payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&authorization_details=' + session['auth_detail']
        elif(session['auth_opt'] == ''):
            session['payload'] = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&authorization_details=' + session['auth_detail']
            return redirect("/authorization_na_payload")
        return render_template('V05/walletPushedRegistration_auth_details_payload.html', red = cfs.v05_redirect_uri, auth_detail = session['auth_detail'], payload = payload)

    return "Error"

@V05.route('/pushedAuthorization_na_authdetails_scope', methods=['GET','POST'])
def pushedAuthorization_na_authdetails_scope():

    if(session['auth_opt'] == 'pkcepar'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']

    elif(session['auth_opt'] == 'par'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']

    elif(session['auth_opt'] == 'pkce'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope'] + '&authorization_details=' + session['auth_detail']
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']

    tit = 'Pushed Authorization response (Authentication details):'
    
    return render_template('V05/walletPushedRegistration_na.html', pushedAuthorization = response.json(), tit = tit)


@V05.route('/pushedAuthorization_na_authdetails', methods=['GET','POST'])
def pushedAuthorization_na_authdetails():


    if(session['auth_opt'] == 'pkcepar'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&authorization_details=' + session['auth_detail']
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']
    
    elif(session['auth_opt'] == 'par'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&authorization_details=' + session['auth_detail']
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']
    
    elif(session['auth_opt'] == 'pkce'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&authorization_details=' + session['auth_detail']
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']

    tit = 'Pushed Authorization response (Authentication details):'
    
    return render_template('V05/walletPushedRegistration_na.html', pushedAuthorization = response.json(), tit = tit)

@V05.route('/pushedAuthorization_na_scope', methods=['GET','POST'])
def pushedAuthorization_na():

    if(session['auth_opt'] == 'pkcepar'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']
    
    elif(session['auth_opt'] == 'par'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&state=af0ifjsldkj&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&scope=' + session['scope']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']
    
    
    elif(session['auth_opt'] == 'pkce'):
        url = session['1_pushed_authorization_request_endpoint']
        payload = 'response_type=code&client_id=ID&redirect_uri=' + cfs.v05_redirect_uri + '&code_challenge=-ciaVij0VMswVfqm3_GK758-_dAI0E9i97hu1SAOiFQ&code_challenge_method=S256&scope=' + session['scope']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        aux = response.json()
        session['request_uri'] = aux['request_uri']
    
    tit = 'Pushed Authorization response (scope):'
    return render_template('V05/walletPushedRegistration_na.html', pushedAuthorization = response.json(), tit = tit)

@V05.route('/authorization_na_payload', methods=['GET','POST'])
def authorization_na_payload():

    if(session['auth_opt'] == ''):
        url = session['2_authorization_endpoint'] + session['payload'] 
    else:
        url = session['2_authorization_endpoint'] + '?client_id=ID&request_uri=' + session['request_uri']

    return render_template('V05/walletAuthorization_na_payload.html', url = url)

@V05.route('/authorization_na', methods=['GET','POST'])
def authorization_na():

    if(session['auth_opt'] == ''):
        url = session['2_authorization_endpoint']
        
        return render_template('V05/url.html', url = url, uri = session['payload'])
    else:
        url = session['2_authorization_endpoint']
        uri = "client_id=ID&request_uri=" + session['request_uri']
        return render_template('V05/url.html', url = url, uri = uri)

@V05.route('/redirect_na', methods=['GET','POST'])
def redirect_na():
    error = request.args.get('error')

    if error is None:
        if(session['auth_opt'] != 'pkce' and session['auth_opt'] != ''):
            session['state'] = request.args['state']
            session['code'] = request.args['code']
            iss = request.args['iss']
        
            return render_template('V05/walletAuthorization_na.html', state = session['state'], code = session['code'], iss = iss)
        else:
            session['code'] = request.args['code']
            iss = request.args['iss']
        
            return render_template('V05/walletAuthorization_na.html', code = session['code'], iss = iss)

    else:
        desc = request.args['error_description']
        error = request.args['error']

        opt = cfs.service_url
        tit = 'Wallet Test HOME'

        return render_template('V05/errorsRed.html', err = error, err_desc = desc , opt = opt, tit = tit)

    

@V05.route('/token_na_payload', methods=['GET','POST'])
def token_na_payload():
    url = session['3_token_endpoint']
    
    if(session['auth_opt'] == 'pkce' or session['auth_opt'] == ''):
        return render_template('V05/walletToken_na_payload.html', url = url, code = session['code'], red = cfs.v05_redirect_uri)
    
    else:
        return render_template('V05/walletToken_na_payload.html', url = url, code = session['code'], state = session['state'], red = cfs.v05_redirect_uri)
    
        
@V05.route('/token_na', methods=['GET','POST'])
def token_na():
    url = session['3_token_endpoint']

    if(session['auth_opt'] == 'pkcepar'):
        payload = 'grant_type=authorization_code&code=' + session['code'] + '&redirect_uri=' + cfs.v05_redirect_uri + '&client_id=ID&state=' + session['state'] + '&code_verifier=FnWCRIhpJtl6IYwVVYB8gZkQsmvBVLfU4HQiABPopYQ6gvIZBwMrXg'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        aux = response.json()
        
        session['access_token'] = aux['access_token']
    
    elif(session['auth_opt'] == 'par'):
        payload = 'grant_type=authorization_code&code=' + session['code'] + '&redirect_uri=' + cfs.v05_redirect_uri + '&client_id=ID&state=' + session['state']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        aux = response.json()
        
        session['access_token'] = aux['access_token']
    
    elif(session['auth_opt'] == 'pkce' or session['auth_opt'] == ''):
        payload = 'grant_type=authorization_code&code=' + session['code'] + '&redirect_uri=' + cfs.v05_redirect_uri + '&client_id=ID&code_verifier=FnWCRIhpJtl6IYwVVYB8gZkQsmvBVLfU4HQiABPopYQ6gvIZBwMrXg'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        aux = response.json()
        
        session['access_token'] = aux['access_token']
    
    if(session['authmode'] == 'credential_offer'):
        tamanhoLista = len(session['credential_configuration_ids'])
        if(tamanhoLista == 1):
            for eachOne in session['credential_configuration_ids']:
                if('mso_mdoc' in session['format'][eachOne]):
                    session['opt'] = 'credential_mso'
                    session['tit'] = '5.1 Credential request: mso-mdoc Payload'
                    return render_template('V05/WalletToken_na.html', token = response.json())
                if('dc+sd-jwt' in session['format'][eachOne]):
                    session['opt'] = 'credential_sd_jwt'
                    session['tit'] = '5.1 Credential request: dc+sd-jwt Payload'
                    return render_template('V05/WalletToken_na.html', token = response.json())
        if(tamanhoLista > 1):
            # session['opt'] = 'batch_credential_na_payload'
            # session['tit'] = '6. Batch Credential payload'
            session['opt'] = 'credential'
            session['tit'] = '5.1 Credential request Payload'
            return render_template('V05/WalletToken_na.html', token = response.json())
        
    lenghScope = len(session['scopeOption'])
    if(lenghScope > 1):
        # session['opt'] = 'batch_credential_na_payload'
        # session['tit'] = '6. Batch Credential payload'
        session['opt'] = 'credential'
        session['tit'] = '5.1 Credential request Payload'
        return render_template('V05/WalletToken_na.html', token = response.json())


    length = len(session['par'])
    if(length == 2):
        # session['opt'] = 'batch_credential_na_payload'
        # session['tit'] = '6. Batch Credential payload'
        session['opt'] = 'credential'
        session['tit'] = '5.1 Credential request Payload'
        return render_template('V05/WalletToken_na.html', token = response.json())

    if(session['par'][0] == 'authorization_details'):
        length = len(session['authorization_details_Option'])
        if(length == 1):
            if('mso_mdoc' in session['format'][session['authorization_details_Option'][0]]):
                session['opt'] = 'credential_mso'
                session['tit'] = '5.1 Credential request: mso-mdoc Payload'
                return render_template('V05/WalletToken_na.html', token = response.json())
            if('dc+sd-jwt' in session['format'][session['authorization_details_Option'][0]]):
                session['opt'] = 'credential_sd_jwt'
                session['tit'] = '5.1 Credential request: dc+sd-jwt Payload'
                return render_template('V05/WalletToken_na.html', token = response.json())
        else:
            # session['opt'] = 'batch_credential_na_payload'
            # session['tit'] = '6. Batch Credential payload'
            session['opt'] = 'credential'
            session['tit'] = '5.1 Credential request Payload'
            return render_template('V05/WalletToken_na.html', token = response.json())
    elif(session['par'][0] == 'scope'):
        length = len(session['scopeOption'])
        if(length == 1):
            if('mso_mdoc' in session['format'][session['scopeOption'][0]]):
                session['opt'] = 'credential_mso'
                session['tit'] = '5.1 Credential request: mso-mdoc Payload'
                return render_template('V05/WalletToken_na.html', token = response.json())
            if('dc+sd-jwt' in session['format'][session['scopeOption'][0]]):
                session['opt'] = 'credential_sd_jwt'
                session['tit'] = '5.1 Credential request: dc+sd-jwt Payload'
                return render_template('V05/WalletToken_na.html', token = response.json())
        else:
            opt = 'batch_credential_na_payload'
            tit = '6. Batch Credential payload'
    
    return "Error"

@V05.route('/nonce_payload', methods=['GET','POST'])
def nonce_payload():
    url = session['url_nonce']
    tit = "Nonce Request"
    opt = "nonce_response"
    
    return render_template('V05/nonce_payload.html', opt = opt, tit = tit, url = url)


@V05.route('/nonce_response', methods=['GET','POST'])
def nonce_response():
    url = session['url_nonce']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + session['access_token']
    }

    payload = ""

    response = requests.request("POST", url, headers=headers, data=payload)

    return render_template('V05/nonce_response.html', response = response.json())


@V05.route('/credential_mso', methods=['GET','POST'])
def credential_na_payload():

    creden = ''

    if(session['authmode'] == 'credential_offer' or session['authmode'] == 'preauth'):
        if(session['proof_type'][0] == 'jwt'):
            creden = '{"credential_configuration_id": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
            #creden = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} } ] }'
            opt = 'credential_na'
        
            return render_template('V05/walletCredential_na_payload_mdoc_credOffer.html', token = session['access_token'], jwt = cfs.jwt, creden = creden, url = session['4_credential_endpoint'], opt = opt)

        elif(session['proof_type'][0] == 'cwt'):
            creden = '{"credential_configuration_id": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'
            #creden = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} } ] }'
            opt = 'credential_na'
        
            return render_template('V05/walletCredential_na_payload_mdoc_credOffer.html', token = session['access_token'], cwt = cfs.cwt, creden = creden, url = session['4_credential_endpoint'], opt = opt)

    aux = ''
    
    if(session['par'][0] == 'authorization_details'):
        if(session['authorization_details_Option'][0] in session):
            aux = session['authorization_details_Option'][0]
        
    elif(session['par'][0] == 'scope'):
        if(session['scopeOption'][0] in session):
            aux = session['scopeOption'][0]
            
    if(session['proof_type'][0] == 'jwt'):
        creden = '{"credential_configuration_id": "' + aux + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
    elif(session['proof_type'][0] == 'cwt'):
        creden = '{"credential_configuration_id": "' + aux + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'
    
    opt = 'credential_na'
    
    return render_template('V05/walletCredential_na_payload_mdoc.html', token = session['access_token'], creden = creden, url = session['4_credential_endpoint'], opt = opt)

@V05.route('/credential_na', methods=['GET','POST'])
def credential_na():
    url = session['4_credential_endpoint'] 

    if(session['authmode'] == 'credential_offer' or session['authmode'] == 'preauth'):
        if(session['proof_type'][0] == 'jwt'):
            for vct in session['vct_list']:
                parte = vct.split("urn:eu.europa.ec.eudi:")[-1].split(":")[0]
                for each in session.get('credential_configuration_ids', []):
                    if(parte in each):
                        payload = '{"format": "dc+sd-jwt", "vct": "' + vct + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
            #payload = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} } ] }'
            opt = 'credential_na'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            aux = response.json()
        elif(session['proof_type'][0] == 'cwt'):
            for vct in session['vct_list']:
                parte = vct.split("urn:eu.europa.ec.eudi:")[-1].split(":")[0]
                for each in session.get('credential_configuration_ids', []):
                    if(parte in each):
                        payload = '{"format": "dc+sd-jwt", "vct": "' + vct + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'
            opt = 'credential_na'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            aux = response.json()
            
    else:

        aux = ''
        
        if(session['par'][0] == 'authorization_details'):
            if(session['authorization_details_Option'][0] in session):
                aux = session['authorization_details_Option'][0]
            
        elif(session['par'][0] == 'scope'):
            if(session['scopeOption'][0] in session):
                aux = session['scopeOption'][0]

        if(session['proof_type'][0] == 'jwt'):
            payload = json.dumps({
                "credential_configuration_id": aux,
                "proof": {
                    "proof_type": "jwt",
                    "jwt": cfs.jwt
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload)
        
        elif(session['proof_type'][0] == 'cwt'):
            aux = aux.split("urn:")[-1].split(".1")[0]
            payload = json.dumps({
                "credential_configuration_id": aux,
                "proof": {
                    "proof_type": "cwt",
                    "cwt": cfs.cwt
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload)
    
    notification_ids = []
    transaction_ids = []
    print(response.json())
    if('notification_id' in response.json()):
        notification_ids.append({
            "credential_configuration_id": aux,
            "notification_id": response.json()['notification_id']
        })
        session['notification_ids'] = notification_ids
        opt = "notification_payload"
        tit = 'Notification (optional)'

        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'

        return render_template('V05/wallet_na_sd.html', creden = response.json(), opt = opt, tit = tit, home_opt = home_opt, home_tit = home_tit)
    elif('transaction_id' in response.json()):
        transaction_ids.append({
            "credential_configuration_id": aux,
            "transaction_id": response.json()['transaction_id']
        })
        session['transaction_ids'] = transaction_ids
        opt = "deferred_payload"
        tit = 'Deferred'

        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'

        return render_template('V05/wallet_na_sd.html', creden = response.json(), opt = opt, tit = tit, home_opt = home_opt, home_tit = home_tit)
    else:
        opt = cfs.service_url
        tit = 'Wallet Test HOME'
        return render_template('V05/errors.html', err = response.json(), opt = opt, tit = tit)

@V05.route('/credential_sd_jwt', methods=['GET','POST'])
def credential_na_payload_sd():

    creden = ''
    if(session['authmode'] == 'credential_offer' or session['authmode'] == 'preauth'):
        if(session['proof_type'][0] == 'jwt'):
            for vct in session['vct_list']:
                parte = vct.split("urn:eu.europa.ec.eudi:")[-1].split(":")[0]
                for each in session.get('credential_configuration_ids', []):
                    if(parte in each):
                        creden = '{"format": "dc+sd-jwt", "vct": "' + vct + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
            #creden = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} } ] }'
            opt = 'credential_na'
            
            return render_template('V05/walletCredential_na_payload_jwt_credOffer.html', token = session['access_token'], jwt = cfs.jwt, creden = creden, url = session['4_credential_endpoint'], opt = opt)
        elif(session['proof_type'][0] == 'cwt'):
            for vct in session['vct_list']:
                parte = vct.split("urn:eu.europa.ec.eudi:")[-1].split(":")[0]
                for each in session.get('credential_configuration_ids', []):
                    if(parte in each):
                        creden = '{"format": "dc+sd-jwt", "vct": "' + vct + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'
            opt = 'credential_na'
            
            return render_template('V05/walletCredential_na_payload_jwt_credOffer.html', token = session['access_token'], cwt = cfs.cwt, creden = creden, url = session['4_credential_endpoint'], opt = opt)


    aux = ''
    if(session['par'][0] == 'authorization_details'):
        if(session['authorization_details_Option'][0] in session):
            aux = session['authorization_details_Option'][0]
        
    elif(session['par'][0] == 'scope'):
        if(session['scopeOption'][0] in session):
            aux = session['scopeOption'][0]
    
    if(session['proof_type'][0] == 'jwt'):
        creden = '{"credential_configuration_id": "' + aux + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
    elif(session['proof_type'][0] == 'cwt'):
        creden = '{"credential_configuration_id": "' + aux + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'
    
    return render_template('V05/walletCredential_na_payload_sd.html', url = session['4_credential_endpoint'], token = session['access_token'], creden = creden)

@V05.route('/credential', methods=['GET','POST'])
def credential_na_payload_more_than_one():

    creden = ''
    if(session['authmode'] == 'credential_offer' or session['authmode'] == 'preauth'):
        if(session['proof_type'][0] == 'jwt'):
            for vct in session['vct_list']:
                parte = vct.split("urn:eu.europa.ec.eudi:")[-1].split(":")[0]
                for each in session.get('credential_configuration_ids', []):
                    if(parte in each):
                        creden = '{"format": "dc+sd-jwt", "vct": "' + vct + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
            #creden = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} } ] }'
            opt = 'credential_na'
            
            return render_template('V05/walletCredential_na_payload_jwt_credOffer.html', token = session['access_token'], jwt = cfs.jwt, creden = creden, url = session['4_credential_endpoint'], opt = opt)
        elif(session['proof_type'][0] == 'cwt'):
            for vct in session['vct_list']:
                parte = vct.split("urn:eu.europa.ec.eudi:")[-1].split(":")[0]
                for each in session.get('credential_configuration_ids', []):
                    if(parte in each):
                        creden = '{"format": "dc+sd-jwt", "vct": "' + vct + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'
            opt = 'credential_na'
            
            return render_template('V05/walletCredential_na_payload_jwt_credOffer.html', token = session['access_token'], cwt = cfs.cwt, creden = creden, url = session['4_credential_endpoint'], opt = opt)


    aux = []
    
    if 'scopeOption' in session and session['scopeOption'] is not None:
        for each in session['scopeOption']:
            creden = '{"credential_configuration_id": "' + each + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
            aux.append(creden)

    if 'authorization_details_Option' in session and session['authorization_details_Option'] is not None:
        print(session['authorization_details_Option'])
        for each in session['authorization_details_Option']:
            creden = '{"credential_configuration_id": "' + each + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
            aux.append(creden)

    clear_session()
    session["batch_credential"] = aux
    return render_template('V05/batch_credential_payload.html', url = session['4_credential_endpoint'], token = session['access_token'], creden = aux)


@V05.route('/batch_credential_request', methods=['GET','POST'])
def batch_credential_request():
    url = session['4_credential_endpoint'] 

    if(session['proof_type'][0] == 'jwt'):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + session['access_token']
        }

        responses = []
        for cred_str in session["batch_credential"]:

            try:
                credential = json.loads(cred_str)

                response = requests.request("POST", url, headers=headers, json=credential)

                responses.append({
                    "credential_configuration_id": credential["credential_configuration_id"],
                    "cred": response.json()
                })

            except Exception as e:
                responses.append({
                    "status_code": 500,
                    "body": {"error": str(e)}
                })

    notification_ids = []
    transaction_ids = []
    
    for response in responses:
        if 'notification_id' in response["cred"]:
            notification_ids.append({
                "credential_configuration_id": response["credential_configuration_id"],
                "notification_id": response["cred"]['notification_id']
            })
        elif 'transaction_id' in response["cred"]:
            transaction_ids.append({
                "credential_configuration_id": response["credential_configuration_id"],
                "transaction_id": response["cred"]['transaction_id']
            })
    
    if(transaction_ids != []):
        session['notification_id'] = notification_ids
        session['transaction_ids'] = transaction_ids
        opt = "deferred_payload"
        tit = 'Deferred'

        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'
        
        return render_template('V05/wallet_na_mdoc.html', creden = responses, opt = opt, tit = tit, home_opt = home_opt, home_tit = home_tit)
    
    elif(notification_ids != []):
        session['notification_ids'] = notification_ids
        session['transaction_ids'] = transaction_ids
        
        opt = "notification_payload"
        tit = 'Notification (optional)'

        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'
        
        return render_template('V05/wallet_na_mdoc.html', creden = responses, opt = opt, tit = tit, home_opt = home_opt, home_tit = home_tit)

    else:
        opt = cfs.service_url
        tit = 'Wallet Test HOME'
        return render_template('V05/errors.html', err = response.json(), opt = opt, tit = tit)



@V05.route('/credential_na_sd', methods=['GET','POST'])
def credential_na_sd():
    url = session['4_credential_endpoint'] 

    if(session['authmode'] == 'credential_offer' or session['authmode'] == 'preauth'):
        if(session['proof_type'][0] == 'jwt'):
            payload = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} } ] }'
            opt = 'credential_na'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            aux = response.json()
        elif(session['proof_type'][0] == 'cwt'):
            payload = '{ "credential_requests": [ {"credential_identifier": "' + session['credential_configuration_ids'][0] + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} } ] }'
            opt = 'credential_na'

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            aux = response.json()
    else:
        aux = ''
        if(session['par'][0] == 'authorization_details'):
            if(session['authorization_details_Option'][0] in session):
                aux = session['authorization_details_Option'][0]
        
        elif(session['par'][0] == 'scope'):
            if(session['scopeOption'][0] in session):
                aux = session['scopeOption'][0]
        
        if(session['proof_type'][0] == 'jwt'):
            payload = json.dumps({
                "credential_configuration_id": aux,
                "proof": {
                    "proof_type": "jwt",
                    "jwt": cfs.jwt
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload) 

        elif(session['proof_type'][0] == 'cwt'):
            payload = json.dumps({
                "credential_configuration_id": aux,
                "proof": {
                    "proof_type": "cwt",
                    "cwt": cfs.cwt
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + session['access_token']
            }

            response = requests.request("POST", url, headers=headers, data=payload) 

    
    notification_ids = []
    transaction_ids = []
    
    if('notification_id' in response.json()):
        notification_ids.append({
            "credential_configuration_id": aux,
            "notification_id": response.json()['notification_id']
        })
        session['notification_ids'] = notification_ids
        opt = "notification_payload"
        tit = 'Notification (optional)'

        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'

        return render_template('V05/wallet_na_sd.html', creden = response.json(), opt = opt, tit = tit, home_opt = home_opt, home_tit = home_tit)
    elif('transaction_id' in response.json()):
        transaction_ids.append({
            "credential_configuration_id": aux,
            "transaction_id": response.json()['transaction_id']
        })
        session['transaction_ids'] = transaction_ids
        opt = "deferred_payload"
        tit = 'Deferred'

        return render_template('V05/wallet_na_sd.html', creden = response.json(), opt = opt, tit = tit)
    else:
        opt = cfs.service_url
        tit = 'Wallet Test HOME'
        return render_template('V05/errors.html', err = response.json(), opt = opt, tit = tit)


@V05.route('/batch_credential_na_payload', methods=['GET','POST'])
def batch_credential_na_payload():
    
    creden = batchcreden_func()

    return render_template('V05/batch_credential_payload.html', url = session['5_batch_credential_endpoint'], 
                        creden = creden, token = session['access_token'])



@V05.route('/batch_credential_na', methods=['GET','POST'])
def batch_credential():
    url = session['5_batch_credential_endpoint']

    payload = batchcreden_func()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + session['access_token']
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    aux = response.json()
   
    if('notification_id' in aux):
        session['notification_id'] = aux['notification_id']
        opt = "notification_payload"
        tit = 'Notification (optional)'
            
        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'

        return render_template('V05/batch_credential.html', creden = response.json(), opt = opt, tit = tit, home_tit = home_tit, home_opt = home_opt)
    elif('transaction_id' in aux):
        session['transaction_id'] = aux['transaction_id']
        opt = "deferred_payload"
        tit = 'Deferred'
        
        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'

        return render_template('V05/batch_credential.html', creden = response.json(), opt = opt, tit = tit, home_tit = home_tit, home_opt = home_opt)
    else:
        opt = cfs.service_url
        tit = 'Wallet Test HOME'

        return render_template('V05/errors.html', err = response.json(), opt = opt, tit = tit)

@V05.route('/preauth')
def preauth():
    session['authmode'] = 'preauth'
    return redirect(cfs.V05_preauth_form)

@V05.route('/redirect_preauth')
def redirect_preauth():
    session['authmode'] = 'preauth'
    session["preauth"] = request.args.get('code')
    session["tx_code"] = request.args.get('tx_code')
    
    credential_offer = request.args.get('credential_offer')

    json_string = credential_offer.split('=', 1)[-1]

    credential_offer = json.loads(json_string)

    session['credential_configuration_ids'] = credential_offer["credential_configuration_ids"]
    result = []
    for config_id in session['credential_configuration_ids']:
        if "mdl_jwt_vc_json" in config_id or "pid_jwt_vc_json" in config_id:
            result.append({"type": "openid_credential", "format": "dc+sd-jwt", "vct": config_id})
            session['vct'] = config_id
        else:
            result.append({"type": "openid_credential", "credential_configuration_id": config_id})

    session['auth_detail'] = json.dumps(result)
    return redirect("getmeta1_na")

@V05.route('/token_preAuth_payload', methods=['GET','POST'])
def token_preAuth_payload():
    url = session['3_token_endpoint']
    return render_template('V05/walletToken_payload_preAuth.html', url = url, code = session["preauth"], tx_code = session['tx_code'], red = cfs.v05_preauth_redirect_uri)

@V05.route('/token_preAuth')
def token_preAuth():
    url = session['3_token_endpoint']
    payload = 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Apre-authorized_code&pre-authorized_code=' + session["preauth"] + "&tx_code=" + session['tx_code']
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    aux = response.json()
    try:
        session['access_token'] = aux['access_token']
    except Exception:
        return aux 
    
    tamanhoLista = len(session['credential_configuration_ids'])
    if(tamanhoLista == 1):
        for eachOne in session['credential_configuration_ids']:
            if('mso_mdoc' in session['format'][eachOne]):
                session['opt'] = 'credential_mso'
                session['tit'] = '5.1 Credential request: mso-mdoc Payload'
                return render_template('V05/WalletToken_na.html', token = response.json())
            if('dc+sd-jwt' in session['format'][eachOne]):
                session['opt'] = 'credential_sd_jwt'
                session['tit'] = '5.1 Credential request: dc+sd-jwt Payload'
                return render_template('V05/WalletToken_na.html', token = response.json())
    if(tamanhoLista > 1):
        # session['opt'] = 'batch_credential_na_payload'
        # session['tit'] = '6. Batch Credential payload'
        session['opt'] = 'credential'
        session['tit'] = '5.1 Credential request Payload'
        return render_template('V05/WalletToken_na.html', token = response.json())

    return "Error"

@V05.route('/credential_preAuth_payload', methods=['GET','POST'])
def credential_preAuth_payload():

    if(session['proof_type'][0] == 'jwt'):
        creden = '{"format": "mso_mdoc", "doctype": "' + session['eu.europa.ec.eudi.loyalty_mdoc'] + '", "proof": { "proof_type": "jwt", "jwt": "' +  cfs.jwt + '"} }'
    elif(session['proof_type'][0] == 'cwt'):
        creden = '{"format": "mso_mdoc", "doctype": "' + session['eu.europa.ec.eudi.loyalty_mdoc'] + '", "proof": { "proof_type": "cwt", "cwt": "' +  cfs.cwt + '"} }'

    opt = 'preauth_credential_mso'
    return render_template('V05/walletCredential_na_payload_mdoc.html', token = session['access_token'], creden = creden, url = session['4_credential_endpoint'], opt = opt)


@V05.route('/preauth_credential_mso', methods=['GET','POST'])
def preauth_credential_mso():
    url = session['4_credential_endpoint'] 

    payload = json.dumps({
        "format": cfs.format_mso_mdoc,
        "doctype": session['eu.europa.ec.eudi.loyalty_mdoc'],
        "proof": {
            "proof_type": "jwt",
            "jwt": cfs.jwt
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + session['access_token']
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    aux = response.json()

    if('notification_id' in aux):
        session['notification_id'] = aux['notification_id']
        opt = "notification_payload"
        tit = 'Notification (optional)'
        
        home_opt = cfs.service_url
        home_tit = 'Wallet Test HOME'

        return render_template('V05/wallet_na_mdoc.html', creden = response.json(), opt = opt, tit = tit, home_opt = home_opt, home_tit = home_tit)
    elif('transaction_id' in aux):
        session['transaction_id'] = aux['transaction_id']
        opt = "deferred_payload"
        tit = 'Deferred'

        return render_template('V05/wallet_na_mdoc.html', creden = response.json(), opt = opt, tit = tit)
    else:
        opt = cfs.service_url
        tit = 'Wallet Test HOME'
        return render_template('V05/wallet_na_mdoc.html', creden = response.json(), opt = opt, tit = tit)
    
@V05.route('/deferred_payload', methods=['GET','POST'])
def deferred_payload():
    opt = 'deferred'
    tit = 'Deferred Response'

    return render_template('V05/deferred_payload.html', token = session['access_token'], url = session['6_deferred_endpoint'], transaction_id = session['transaction_ids'], opt = opt, tit = tit)


@V05.route('/deferred', methods=['GET','POST'])
def deferred():
    url = session['6_deferred_endpoint'] 
    responses = []
    for each in session['transaction_ids']:
        payload = json.dumps({
            "transaction_id": each['transaction_id']
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + session['access_token']
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        responses.append({
            "credential_configuration_id": each["credential_configuration_id"],
            "cred": response.json()
        })

    for response in responses:
        if "error" in response["cred"]:
            if(response["cred"]["error"] == "issuance_pending"):
                opt = 'deferred'
                tit = 'Deferred Response'
                home_opt = cfs.service_url
                home_tit = 'Wallet Test HOME'
                return render_template('V05/deferred.html', creden = responses, opt = opt, tit = tit, home_tit = home_tit, home_opt = home_opt)
            

    notification_ids = []
    for response in responses:
        if 'notification_ids' not in session:
            if('notification_id' in response["cred"]):
                notification_ids.append({
                    "credential_configuration_id": response["credential_configuration_id"],
                    "notification_id": response["cred"]['notification_id']
                })
        else:
            session["notification_ids"].append({
                "credential_configuration_id": response["credential_configuration_id"],
                "notification_id": response["cred"]['notification_id']
            })
    
    if 'notification_ids' not in session:
        session["notification_ids"] = notification_ids

    opt = "notification_payload"
    tit = 'Notification (optional)'
    
    home_opt = cfs.service_url
    home_tit = 'Wallet Test HOME'

    return render_template('V05/deferred.html', creden = responses, opt = opt, tit = tit, home_tit = home_tit, home_opt = home_opt)

@V05.route('/notification_payload', methods=['GET','POST'])
def notification_payload():
    opt = 'notification'
    tit = 'Notification Response'

    return render_template('V05/notification_payload.html', token = session['access_token'], url = session['7_notification_endpoint'], notification_id = session['notification_ids'], opt = opt, tit = tit)


@V05.route('/notification', methods=['GET','POST'])
def notification():
    url = session['7_notification_endpoint'] 
    responses = []

    for each in session['notification_ids']:
        payload = json.dumps({
            "notification_id": each["notification_id"],
            "event": "credential_accepted"
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + session['access_token']
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        responses.append({
            "credential_configuration_id": each["credential_configuration_id"],
            "code": response.status_code,
            "test": response.text
        })

    opt = cfs.service_url
    tit = 'Wallet Test HOME'

    return render_template('V05/notification.html', response = responses, opt = opt, tit = tit)

@V05.route('/credential_offer', methods=['GET','POST'])
def credentialoffer():
    session['authmode'] = 'credential_offer'
    session['auth_opt'] = 'pkcepar'
    
    credential_offer = request.args.get('credential_offer')

    json_string = credential_offer.split('=', 1)[-1]

    credential_offer = json.loads(json_string)

    session['credential_configuration_ids'] = credential_offer["credential_configuration_ids"]
    result = []
    for config_id in session['credential_configuration_ids']:
        if "mdl_jwt_vc_json" in config_id or "pid_jwt_vc_json" in config_id:
            result.append({"type": "openid_credential", "format": "dc+sd-jwt", "vct": config_id})
            session['vct'] = config_id
        else:
            result.append({"type": "openid_credential", "credential_configuration_id": config_id})
    
    session['auth_detail'] = json.dumps(result)
    return redirect('getmeta1_na')


@V05.route('/cred_off', methods=['GET','POST'])
def cred_off():
    #session['auth_detail'] = json.dumps(session['credential_configuration_ids'])
    return render_template('V05/walletPushedRegistration_auth_details_payload.html', red = cfs.v05_redirect_uri, auth_detail = session['auth_detail'])

@V05.route('/auth_type', methods=['GET','POST'])
def auth_type():
    return render_template('V05/auth_type.html')

@V05.route('/auth_type_manager', methods=['GET','POST'])
def auth_type_manager():
    
    type_auth = request.form.getlist('type_auth')
    print("Opções selecionadas do par:", type_auth)

    lengh_TA = len(type_auth)
    session['auth_opt'] = ""
    
    if(lengh_TA == 0):
        session['auth_opt'] = ""

    elif(lengh_TA > 1):
        for eachOne in type_auth:
            session['auth_opt'] = session['auth_opt'] + eachOne
        
    else:
        session['auth_opt'] = type_auth[0]

    return redirect("/auth")

@V05.route("/proof_type", methods=['GET','POST'])
def proof_type():
    return render_template('V05/proof_type.html')

@V05.route('/proof_type_manager', methods=['GET','POST'])
def proof_type_manager():
    
    proof_type = request.form.getlist('proof_type')

    print("Opções selecionadas do proof_type:", proof_type)
    session['proof_type'] = proof_type

    return redirect('/' + session['opt'])

def batchcreden_func():
    if(session['authmode'] == 'credential_offer' or session['authmode'] == 'preauth'):
        
        if(session['proof_type'][0] == 'jwt'):
            creden = ''
            for eachOne in session['credential_configuration_ids']:
                creden = creden + '{"credential_identifier": "' + eachOne + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} }, '
            
            creden = '{"credential_requests": [' + creden
            creden = creden.rsplit(',', 1)[0] + ']}'


            return(creden)
        
        elif(session['proof_type'][0] == 'cwt'):
            creden = ''
            for eachOne in session['credential_configuration_ids']:
                creden = creden + '{"credential_identifier": "' + eachOne + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} }, '
            
            creden = '{"credential_requests": [' + creden
            creden = creden.rsplit(',', 1)[0] + ']}'


            return(creden)

    creden = ''
    length = len(session['par'])
    if(length == 2):
        for eachOne in session['scopeOption']:
            if(session['proof_type'][0] == 'jwt'):
                creden = creden + '{ "credential_identifier": "' + eachOne + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} }, '
            elif(session['proof_type'][0] == 'cwt'):
                creden = creden + '{ "credential_identifier": "' + eachOne + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} }, '

        for option in session['authorization_details_Option']:
            if(session['proof_type'][0] == 'jwt'):
                creden = creden + '{ "credential_identifier": "' + option + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} }, '
            elif(session['proof_type'][0] == 'cwt'):
                creden = creden + '{ "credential_identifier": "' + option + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} }, '

        creden = '{"credential_requests": [' + creden
        creden = creden.rsplit(',', 1)[0] + ']}'
        
        return(creden)
    
    lenghScope = len(session['scopeOption'])
    if(lenghScope > 1):
        creden = ''
        for eachOne in session['scopeOption']:
            if(session['proof_type'][0] == 'jwt'):
                creden = creden + '{ "credential_identifier": "' + eachOne + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} }, '
            if(session['proof_type'][0] == 'cwt'):
                creden = creden + '{ "credential_identifier": "' + eachOne + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} }, '
            
        creden = '{"credential_requests": [' + creden
        creden = creden.rsplit(',', 1)[0] + ']}'

        
        return(creden)
    
    lengh = len(session['authorization_details_Option'])
    if(lengh > 1):
        creden = ''
        for eachOne in session['authorization_details_Option']:
            if(session['proof_type'][0] == 'jwt'):
                creden = creden + '{ "credential_identifier": "' + eachOne + '", "proof": { "proof_type": "jwt", "jwt": "' + cfs.jwt + '"} }, '
            elif(session['proof_type'][0] == 'cwt'):
                creden = creden + '{ "credential_identifier": "' + eachOne + '", "proof": { "proof_type": "cwt", "cwt": "' + cfs.cwt + '"} }, '

        creden = '{"credential_requests": [' + creden
        creden = creden.rsplit(',', 1)[0] + ']}'

        
        return(creden)
    
def clear_session():
    manter = {
        'batch_credential',
        '4_credential_endpoint',
        'access_token',
        '7_notification_endpoint',
        'notification_id',
        'proof_type',
        '6_deferred_endpoint'
    }

    chaves = list(session.keys())

    for chave in chaves:
        if chave not in manter:
            session.pop(chave)
