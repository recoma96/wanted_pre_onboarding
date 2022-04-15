# 데이터베이스 테이블을 생성하기 위한 함수
# 밖에서 사용하지 말 것
import re

from sqlalchemy.orm import declarative_base, validates
from sqlalchemy import Column, String

from project.connection.connection_generator import DatabaseConnectionGenerator

__base = declarative_base()

""" Validate Regexes """
USER_ID_REGEX: re.Pattern = re.compile(r"^([0-9A-Za-z]{60})$")
USER_NAME_REGEX: re.Pattern = re.compile(r"^([a-zA-Zㄱ-힣0-9]{1,64})$")


class DatabaseRegexNotMatched(Exception):
    # validate 매칭이 안되는 경우에 대한 에러
    code: int

    def __init__(self, __code: int, __msg: str):
        super().__init__(__msg)
        self.code = __code


class User(__base):
    """ 사용자 테이블
        id: 60자의 랜덤 숫자/영어
        name: 유저 이름 (1자 이상 64자 이하 특수문자 제외)
    """

    # Error Codes in regex
    ID_NOT_MATCHED: int = 1
    NAME_NOT_MATCHED: int = 2
    NAME_ALREADY_EXIST: int = 3

    __tablename__ = "user"

    id = Column("id", String(60), primary_key=True, index=True)
    name = Column("name", String(64), unique=True)

    @validates("id")
    def validate_id(self, __key, __id: str):
        # 아이디는 60자 이하의 숫자/영어
        if not USER_ID_REGEX.match(__id):
            raise DatabaseRegexNotMatched(User.ID_NOT_MATCHED, "user id not matched")
        return __id

    @validates("name")
    def validate_name(self, __key, __name: str):

        if not USER_NAME_REGEX.match(__name):
            raise DatabaseRegexNotMatched(User.NAME_NOT_MATCHED, "user name not matched")
        return __name


""" Database Table Control Functions """


def rdb_create_all():
    # RDB 스키마 생성
    __base.query = DatabaseConnectionGenerator.get_session().query_property()
    __base.metadata.create_all(bind=DatabaseConnectionGenerator.get_engine())


def remove_test_db():
    # 테스트 데이터베이스 파일 제거
    import os
    if os.path.isfile("test.db"):
        os.remove("test.db")
