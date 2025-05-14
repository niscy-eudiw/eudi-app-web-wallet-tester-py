# EUDIW Wallet Tester (for Issuer)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

:heavy_exclamation_mark: **Important!** Before you proceed, please read
the [EUDI Wallet Reference Implementation project description](https://github.com/eu-digital-identity-wallet/.github/blob/main/profile/reference-implementation.md)


### Overview

The EUDIW Wallet Tester (for Issuer) allows to test the OID4VCI (draft 13) flow with a Issuer, in a Web GUI.

## :heavy_exclamation_mark: Disclaimer

The released software is a initial development release version:

-   The initial development release is an early endeavor reflecting the efforts of a short timeboxed
    period, and by no means can be considered as the final product.
-   The initial development release may be changed substantially over time, might introduce new
    features but also may change or remove existing ones, potentially breaking compatibility with your
    existing code.
-   The initial development release is limited in functional scope.
-   The initial development release may contain errors or design flaws and other problems that could
    cause system or other failures and data loss.
-   The initial development release has reduced security, privacy, availability, and reliability
    standards relative to future releases. This could make the software slower, less reliable, or more
    vulnerable to attacks than mature software.
-   The initial development release is not yet comprehensively documented.
-   Users of the software must perform sufficient engineering and additional testing in order to
    properly evaluate their application and determine whether any of the open-sourced components is
    suitable for use in that application.
-   We strongly recommend not putting this version of the software into production use.
-   Only the latest version of the software will be supported


## Installation
1. Enter the wallett folder

  ```shell
  cd wallett
  ```

2. Create .venv to install flask and other libraries

  Windows:
  
  ```shell
  python -m venv .venv 
  ```
  
  Linux:

  ```shell
  python3 -m venv .venv
  ```

3. Activate the environment

  windows:
    
  ```shell
  . .venv\Scripts\Activate
  ```
    
  Linux:
  
  ```shell
  . .venv/bin/activate
  ```
    
  4. Install the necessary libraries to run the code

  ```shell
  pip install Flask-Cors flask==2.3.3 werkzeug==2.3.7 requests
  ```
  or
  ```shell
  pip install -r requirements.txt
  ```

  5. Run the Project
  ```shell
  flask run --debug --cert=certs/cert.pem --key=certs/key.pem
  flask --app wallet run --debug --cert=wallet/certs/cert.pem --key=wallet/certs/key.pem
  ```

or

 ```shell
gunicorn app:app -b 127.0.0.1:5000 --keyfile=certs/key.pem --certfile=certs/cert.pem
  ```

# Important Note

  It is worth noting that the project must run on HTTPS. 
  By default, it will already be running on HTTPS, but if the user changes the service_url (discussed in more detail below), they must ensure that it is using HTTPS.

  
# How to use the project version 0.5 (V0.5)
1. Url
  ```shell
  https:127.0.0.1:5000/
  ```

As soon as you access the URL, the V0.5 version presentation page will be displayed. Below, you can see the entire flow and what is possible to do. This test version of the wallet is intended to test considering the OpenID for Verifiable Credential Issuance - draft 13, where it is possible to test using 3 different types of Par options to perform the Push Authorization Request, which are:

1. Scope
2. Authorization Details
3. Both of the other mentioned options, simultaneously (Scope and Authorization Details)

Depending on the combinations selected in the options menu to perform the Push Authorization Request, the Credential or Batch Credential will be used. On the options menu page, it will also display the information of the type of request made (Credential or Batch Credential).

# Configuration

  There is a configuration file located at 'wallet/app_config/config.py', where the user can modify some variables to change how the project operates. 
  Here are the most relevant ones:
  
  1. service_url
  
  By default, it is set to 'https://127.0.0.1:5000/'
  As mentioned earlier, the project must run on HTTPS. In case the user changes it to another domain, there is a certificate folder ('wallet/certs') where the certificates are stored.
  In the 'wallet/run.py' file used to run the project, the path to the certificates is specified. Therefore, if you change the 'service_url', you may need to update this file or the certificates folder.


## How to contribute

We welcome contributions to this project. To ensure that the process is smooth for everyone
involved, follow the guidelines found in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

### License details

Copyright (c) 2023 European Commission

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
# Docker

  1. Introduction
  You can use Docker to run the project easily in a containerized environment.

# Using an Docker image

1. Required Files:
      1. docker-compose.yml → Manages services, images, environment variables, and container orchestration.

2. Setup

    A docker-compose.yml file needs to be created with the following content:
      
      ```shell
      services:
        wallet:
          image: ghcr.io/niscy-eudiw/eudi-app-web-wallet-tester-py:latest
          ports:
            - "5000:5000"
          environment: 
            - FLASK_RUN_PORT= 5000
            - service_url= ...
      ```

    Key Settings:

      1. 
      ```shell
      ports:
        - "5000:5000"
      environment: 
        - FLASK_RUN_PORT= 5000
      ```
        
    This maps the internal/external Flask port (default: 5000) to the host machine.
      
      2. service_url="" -> Set the URL where the service will be available. For local use http://localhost:5000/ 
    
3. Running

    In the directory where the created docker-compose.yml file is located, run the following command:

    ```shell
    docker-compose up
    ```

# Using the source code
1. Required Files:
      1. Dockerfile → Defines the environment and how the application is built.

      2. docker-compose.yml → Manages services, environment variables, and container orchestration.

2. Setup

    Before running, you must configure the environment variables inside docker-compose.yml.

    Key Settings:

      1. 
      ```shell
      ports:
        - 5000:5000
      environment: 
        - FLASK_RUN_PORT= 5000
      ```
        
    This maps the internal/external Flask port (default: 5000) to the host machine.

      2. service_url="" -> Set the URL where the service will be available. For local use http://localhost:5000/

3. Running

    To start the service, navigate to the folder containing the files mentioned above and run:

    ```shell
    docker-compose up --build
    ```
