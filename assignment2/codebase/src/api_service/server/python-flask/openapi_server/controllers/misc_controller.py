import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server import util

from openapi_server.logging_service import logging_client


def root_get():  # noqa: E501
    """Greeting

    Return a welcome message. # noqa: E501


    :rtype: Union[str, Tuple[str, int], Tuple[str, int, Dict[str, str]]
    """

    logging_client.send_logs([{
        "service_name": "api-service",
        "level": "INFO",
        "path": "/",
        "method": "GET",
        "user_sid": "",
        "message": "Root endpoint accessed"
    }])

    return 'Hello SUSTech Goods Store!'
