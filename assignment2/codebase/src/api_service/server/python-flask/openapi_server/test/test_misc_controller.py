import unittest

from flask import json

from openapi_server.test import BaseTestCase


class TestMiscController(BaseTestCase):
    """MiscController integration test stubs"""

    def test_root_get(self):
        """Test case for root_get

        Greeting
        """
        headers = { 
            'Accept': 'text/plain',
        }
        response = self.client.open(
            '/',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
