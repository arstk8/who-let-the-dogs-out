import json
import time
import urllib.request
from os import getenv

from jose import jwt, jwk
from jose.utils import base64url_decode


class AuthorizationValidator:
    def __init__(self):
        region = getenv('AWS_REGION')
        userpool_id = getenv('USERPOOL_ID')
        keys_url = f'https://cognito-idp.{region}.amazonaws.com/{userpool_id}/.well-known/jwks.json'
        with urllib.request.urlopen(keys_url) as f:
            response = f.read()

        self.app_client_id = getenv('APP_CLIENT_ID')
        self.keys = json.loads(response.decode('utf-8'))['keys']

    def validate(self, token):
        key_index = self.__get_key_index(token)
        self.__validate_key_index(key_index)

        public_key = jwk.construct(self.keys[key_index])
        self.__validate_signature(public_key, token)

        claims = jwt.get_unverified_claims(token)
        self.__validate_token(claims)

        return claims

    def __get_key_index(self, token):
        key_index = -1
        kid = self.__get_kid(token)
        for i in range(len(self.keys)):
            if kid == self.keys[i]['kid']:
                key_index = i
                break
        return key_index

    @staticmethod
    def __get_kid(token):
        headers = jwt.get_unverified_headers(token)
        return headers['kid']

    @staticmethod
    def __validate_key_index(key_index):
        if key_index == -1:
            print('Public key not found in jwks.json')
            raise Exception('Unauthorized')

    @staticmethod
    def __validate_signature(public_key, token):
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            print('Signature verification failed')
            raise Exception('Unauthorized')

    def __validate_token(self, claims):
        if time.time() > claims['exp']:
            print('Token is expired')
            raise Exception('Unauthorized')
        if claims['client_id'] != self.app_client_id:
            print('Token was not issued for this audience')
            raise Exception('Unauthorized')
