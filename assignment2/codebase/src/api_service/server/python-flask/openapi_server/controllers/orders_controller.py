import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.order import Order  # noqa: E501
from openapi_server.models.order_create_request import OrderCreateRequest  # noqa: E501
from openapi_server import util


def orders_get():  # noqa: E501
    """List all orders of current user

     # noqa: E501


    :rtype: Union[List[Order], Tuple[List[Order], int], Tuple[List[Order], int, Dict[str, str]]
    """
    return 'do some magic!'


def orders_id_delete(id):  # noqa: E501
    """Cancel an order

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def orders_id_get(id):  # noqa: E501
    """Get an order by id (current user&#39;s order)

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'do some magic!'


def orders_post(order_create_request):  # noqa: E501
    """Place an order

     # noqa: E501

    :param order_create_request: 
    :type order_create_request: dict | bytes

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        order_create_request = OrderCreateRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
