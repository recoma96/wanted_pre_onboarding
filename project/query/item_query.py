import string
import datetime
import random
from typing import List, Dict

from project.query.query import Query
from project.query.user_query import UserQuery


class ItemQuery(Query):
    """ 상품 CRUD 쿼리
    """

    # 아이디를 랜덤하게 생성할 때 사용하는 문자열
    CANDIDATE_ID: str = string.ascii_letters + "0123456789"

    @staticmethod
    def __generate_id() -> str:
        """ 계정을 생성할 때 사용하는 랜덤 id
            Format: [날짜(microsecond까지)][랜덤]
        """
        now = datetime.datetime.now()
        new_id = now.strftime("%Y%M%d%H%M%S%f")  # 20 line
        for _ in range(40):
            new_id += random.choice(UserQuery.CANDIDATE_ID)
        return new_id

    @staticmethod
    def create(__user: List[str], __name: str, __summary: str, __end_date: datetime.datetime) -> int:
        pass

    @staticmethod
    def read(__key: str, __value: str) -> Dict[str, object]:
        pass

    @staticmethod
    def update(__user: List[str],
               __name: str = None, __summary: str = None, __end_date: datetime.datetime = None) -> int:
        pass

    @staticmethod
    def delete(__key: str, __value: str, __item_id: str):
        pass

    """ Founding Table과 같이 사용하는 검색 쿼리 """

    @staticmethod
    def sort_by_createdate() -> List[Dict[str, object]]:
        """ 생성일을 기준으로 정렬 """
        pass

    @staticmethod
    def sort_by_fundingmoney() -> List[Dict[str, object]]:
        """ 펀딩코인순으로 정렬 """
        pass
