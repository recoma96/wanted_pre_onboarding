import string
import datetime
import random
from typing import List, Dict

import sqlalchemy.exc

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import User, Item, DatabaseRegexNotMatched
from project.query.query import Query
from project.query.user_query import UserQuery


class ItemQuery(Query):
    """ 상품 CRUD 쿼리
    """

    @staticmethod
    def create(__user: List[str],
               __name: str,
               __summary: str,
               __end_date: datetime.datetime,
               __funding_unit: int,
               __target_money: int) -> int:
        """

        :param __user:          게시자 정보 이름 또는 아이디가 들어간다.
        :param __name:          상품 이름
        :param __summary:       상품에 대한 설명
        :param __end_date:      만료일
        :param __funding_unit:  1회당 금액   
        :param __target_money:  목표 금액
        :return:
        """
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
