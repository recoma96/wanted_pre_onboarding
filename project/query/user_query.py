import string
from datetime import datetime
import random

import sqlalchemy.exc

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import User, DatabaseRegexNotMatched
from project.query.query import Query
from typing import List, Dict


class UserQuery(Query):
    # 아이디를 랜덤하게 생성할 때 사용하는 문자열
    CANDIDATE_ID: str = string.ascii_letters + "0123456789"

    @staticmethod
    def __generate_id() -> str:
        """ 계정을 생성할 때 사용하는 랜덤 id
            Format: [날짜(microsecond까지)][랜덤]
        """
        now = datetime.now()
        new_id = now.strftime("%Y%M%d%H%M%S%f")  # 20 line
        for _ in range(40):
            new_id += random.choice(UserQuery.CANDIDATE_ID)
        return new_id

    @staticmethod
    def create(__name: str) -> int:
        """ 유저 생성 """
        db_session = DatabaseConnectionGenerator.get_session()
        while True:
            try:
                # create
                user: User = User(id=UserQuery.__generate_id(), name=__name)
                db_session.add(user)
                db_session.commit()
            except DatabaseRegexNotMatched as e:
                # 이름이 맞지 않음
                return e.code
            except sqlalchemy.exc.IntegrityError:
                # 동일한 이름의 유저를 생성하려고 할 때 발생한다.
                # 트랜잭션을 롤백한다.
                db_session.rollback()
                return User.NAME_ALREADY_EXIST
            except Exception as e:
                # 기타 예외
                raise e
            else:
                # 성공 시 0 리턴
                return 0

    @staticmethod
    def read(__key: str, __value: str) -> Dict[str, str]:
        """ 유저 정보 찾기 """

        db_session = DatabaseConnectionGenerator.get_session()

        target: User = None

        if __key == "name":
            target = db_session.query(User).filter(User.name == __value).scalar()
        elif __key == "id":
            target = db_session.query(User).filter(User.id == __value).scalar()
        else:
            raise TypeError("Key is not matched")

        if not target:
            # 데이터 없음
            return None
        return {
            "id": target.id,
            "name": target.name
        }


    @staticmethod
    def update(__item: List[str], __new_name: str):
        pass

    @staticmethod
    def delete(__item: List[str]):
        pass
