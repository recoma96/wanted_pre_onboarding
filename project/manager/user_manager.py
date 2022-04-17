from typing import Dict, Optional

from manager.manager import Manager
from query.err_codes import UserQueryErrorCode
from query.user_query import UserQuery


class UserManager(Manager):

    def __new__(cls, *args, **kwargs):
        # 하나의 서버에 하나의 객체만 있어야 하기 때문에 Singletone Pattern 도입
        if not hasattr(cls, 'user_manager_instance'):
            cls.user_manager_instance = super(UserManager, cls).__new__(cls)
        return cls.user_manager_instance

    def add_user(self, name: str) -> int:
        """ 유저 생성

        :param name: 새로운 이름
        :return: 에러 코드
        """
        try:
            return UserQuery.create(name).value
        except Exception as e:
            raise e

    def get_user(self,
                 name: Optional[str] = None,
                 user_id: Optional[str] = None) -> Dict[str, object]:
        """ 유저 정보 얻기 """
        if user_id:
            return UserQuery.read("id", user_id)
        elif name:
            return UserQuery.read("name", name)
        else:
            return None

    def update_user(self,
                    new_name: str,
                    user_name: Optional[str] = None,
                    user_id: Optional[str] = None) -> bool:
        """ 유저 수정

        :param new_name:
        :param user_name:
        :param user_id:
        :return: 성공시 True, 실패시(이름이 중복되는 경우) False, 에러시 Raise Error
        """
        if user_id:
            if UserQuery.update(key="id", target_value=user_id, new_name=new_name) == \
                    UserQueryErrorCode.SUCCEED:
                return True
            else:
                return False
        elif user_name:
            if UserQuery.update(key="name", target_value=user_name, new_name=new_name) == \
                    UserQueryErrorCode.SUCCEED:
                return True
            else:
                return False
