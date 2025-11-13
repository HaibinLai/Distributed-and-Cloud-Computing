import unittest

from flask import json

from openapi_server.models.auth_token_response import AuthTokenResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.user_login_request import UserLoginRequest  # noqa: E501
from openapi_server.models.user_profile import UserProfile  # noqa: E501
from openapi_server.models.user_register_request import UserRegisterRequest  # noqa: E501
from openapi_server.models.user_update_request import UserUpdateRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def test_users_login_post(self):
        """Test case for users_login_post

        Login and get JWT
        """
        user_login_request = {"password":"password","sid":"sid"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/users/login',
            method='POST',
            headers=headers,
            data=json.dumps(user_login_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_me_delete(self):
        """Test case for users_me_delete

        Deactivate current user's account
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/users/me',
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_me_get(self):
        """Test case for users_me_get

        Get current user's profile
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/users/me',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_me_patch(self):
        """Test case for users_me_patch

        Update current user's profile
        """
        user_update_request = {"email":"email","username":"username"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/users/me',
            method='PATCH',
            headers=headers,
            data=json.dumps(user_update_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_register_post(self):
        """Test case for users_register_post

        Register a new user
        """
        user_register_request = {"password":"password","email":"email","sid":"sid","username":"username"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/users/register',
            method='POST',
            headers=headers,
            data=json.dumps(user_register_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
