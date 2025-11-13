import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.auth_token_response import AuthTokenResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.user_login_request import UserLoginRequest  # noqa: E501
from openapi_server.models.user_profile import UserProfile  # noqa: E501
from openapi_server.models.user_register_request import UserRegisterRequest  # noqa: E501
from openapi_server.models.user_update_request import UserUpdateRequest  # noqa: E501
from openapi_server import util


def users_login_post(user_login_request):  # noqa: E501
    """Login and get JWT

     # noqa: E501

    :param user_login_request: 
    :type user_login_request: dict | bytes

    :rtype: Union[AuthTokenResponse, Tuple[AuthTokenResponse, int], Tuple[AuthTokenResponse, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        user_login_request = UserLoginRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def users_me_delete():  # noqa: E501
    """Deactivate current user&#39;s account

     # noqa: E501


    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def users_me_get():  # noqa: E501
    """Get current user&#39;s profile

     # noqa: E501


    :rtype: Union[UserProfile, Tuple[UserProfile, int], Tuple[UserProfile, int, Dict[str, str]]
    """
    return 'do some magic!'


def users_me_patch(user_update_request):  # noqa: E501
    """Update current user&#39;s profile

     # noqa: E501

    :param user_update_request: 
    :type user_update_request: dict | bytes

    :rtype: Union[UserProfile, Tuple[UserProfile, int], Tuple[UserProfile, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        user_update_request = UserUpdateRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def users_register_post(user_register_request):  # noqa: E501
    """Register a new user

     # noqa: E501

    :param user_register_request: 
    :type user_register_request: dict | bytes

    :rtype: Union[UserProfile, Tuple[UserProfile, int], Tuple[UserProfile, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        user_register_request = UserRegisterRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
