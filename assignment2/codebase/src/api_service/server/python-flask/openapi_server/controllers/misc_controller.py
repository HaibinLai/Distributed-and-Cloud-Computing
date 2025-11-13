import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server import util


def root_get():  # noqa: E501
    """Greeting

    Return a welcome message. # noqa: E501


    :rtype: Union[str, Tuple[str, int], Tuple[str, int, Dict[str, str]]
    """
    return 'Hello SUSTech Goods Store!'
