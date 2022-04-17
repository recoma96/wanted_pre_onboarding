import re
import datetime
import random
import string
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy import Column, String, ForeignKey, DateTime, func, Integer
from project.connection.connection_generator import DatabaseConnectionGenerator
from project.query.err_codes import ItemQueryErrorCode, UserQueryErrorCode

# 데이터베이스 테이블을 생성하기 위한 함수
# 밖에서 사용하지 말 것
__base = declarative_base()

""" Validate Regexes """
USER_ID_REGEX: re.Pattern = re.compile(r"^([0-9A-Za-z]{60})$")
USER_NAME_REGEX: re.Pattern = re.compile(r"^([a-zA-Zㄱ-힣0-9]{1,64})$")
ITEM_ITEMID_REGEX: re.Pattern = re.compile(r"^([0-9A-Za-z]{60})$")


class DatabaseRegexNotMatched(Exception):
    # validate 매칭이 안되는 경우에 대한 에러
    code: int

    def __init__(self, __code: object, __msg: str):
        # code는 에러 유형 식별자
        super().__init__(__msg)
        self.code = __code


def generate_id() -> str:
    """ 임의 랜덤 아이디 생성기
         Format: [날짜(microsecond까지)][랜덤]
    """
    CANDIDATE_ID: str = string.ascii_letters + "0123456789"
    now = datetime.datetime.now()
    new_id = now.strftime("%Y%M%d%H%M%S%f")  # 20 line
    for _ in range(40):
        new_id += random.choice(CANDIDATE_ID)
    return new_id


class User(__base):
    """ 사용자 테이블
        id: 60자의 랜덤 숫자/영어
        name: 유저 이름 (1자 이상 64자 이하 특수문자 제외)
    """

    __tablename__ = "user"

    id = Column("id", String(60), primary_key=True, index=True)
    name = Column("name", String(64), unique=True)

    @validates("id")
    def validate_id(self, __key, __id: str):
        if not USER_ID_REGEX.match(__id):
            raise DatabaseRegexNotMatched(UserQueryErrorCode.ID_NOT_MATCHED, "user id not matched")
        return __id

    @validates("name")
    def validate_name(self, __key, __name: str):
        if not USER_NAME_REGEX.match(__name):
            raise DatabaseRegexNotMatched(UserQueryErrorCode.NAME_NOT_MATCHED, "user name not matched")
        return __name


class Item(__base):
    """ 상품 테이블

        itemId: 상품 아이디
        userId: 유저 아이디
        name: 상품 이름
        create_date: 생성 날짜 (DB에서 자동 생성)
        end_date: 종료일
        participant_size: 참가자 수
        target_funding: 목표 금액
        funding_unit: 1회당 펀딩 금액
    """
    __tablename__ = "item"

    item_id = Column("itemId", String(60), primary_key=True, index=True)
    user_id = Column(
        "userId", ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    name = Column("name", String(128), nullable=False, unique=True)
    create_date = Column("createDate", DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column("endDate", DateTime(timezone=True), nullable=False)

    participant_size = Column("participantSize", Integer, default=0, nullable=False)
    target_money = Column("targetMoney", Integer, nullable=False)
    current_money = Column("currentMoney", Integer, nullable=False, default=0)
    funding_unit = Column("fundingUnit", Integer, nullable=False)

    """ validates """

    @validates("item_id")
    def validate_item_id(self, __key: str, __item_id: str):
        if not ITEM_ITEMID_REGEX.match(__item_id):
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.ITEM_ID_NOT_MATCHED, "item id not matched")
        return __item_id

    @validates("user_id")
    def validate_user_id(self, __key: str, __user_id: str):
        if not USER_ID_REGEX.match(__user_id):
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.USER_ID_NOT_MATCHED, "user id not matched")
        return __user_id

    @validates("name")
    def validate_name(self, __key: str, __name: str):
        # 1자 이상 128자 이하
        if not __name or len(__name) > 128:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.NAME_NOT_MATCHED, "name not matched")
        return __name

    @validates("end_date")
    def validate_end_date(self, __key: str, __date: datetime.datetime):
        # 과거여도 상관없음 단 데이터가 비어있으면 안됨
        if not __date:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.END_DATE_NOT_MATCHED, "end date must not be none")
        return __date

    @validates("participant_size")
    def validate_participant_size(self, __key: str, __size: int):
        # 참가자 수는 음수일 수가 없음
        if __size < 0:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.PARTICIPANT_SIZE_NOT_MATCHED, "participant size error")
        return __size

    @validates("target_money")
    def validate_target_money(self, __key: str, __money: int):
        # 목표 금액은 1원 이상
        if __money <= 0:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.TARGET_MONEY_NOT_MATCHED, "participant size error")
        return __money

    @validates("funding_unit")
    def validate_funding_unit(self, __key: str, __funding_unit: int):
        # 1회당 펀딩 금액은 1원 이상
        if __funding_unit <= 0:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.FUNDING_UNIT_NOT_MATCHED, "participant size error")
        return __funding_unit

    @validates("current_money")
    def validate_current_money(self, __key: str, __current_money: int):
        # 현재 금액은 0원 이상
        if __current_money < 0:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.CURRENT_MONEY_NOT_MATCHED, "current money not matched"
            )
        return __current_money


class ItemContents(__base):
    """ 해당 상품에 대한 추가적인 요소들 (주로 데이터가 방대한 경우)

        itemId: 상품 아이디
        summary: 상품 요약
    """
    __tablename__ = "itemContents"

    item_id = Column(
        "itemId", ForeignKey("item.itemId", ondelete="CASCADE"),
        nullable=False, primary_key=True
    )
    summary = Column("summary", String(2048), nullable=True)

    @validates("item_id")
    def validate_item_id(self, __key: str, __item_id: str):
        if not ITEM_ITEMID_REGEX.match(__item_id):
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.ITEM_ID_NOT_MATCHED, "item id not matched")
        return __item_id

    @validates("summary")
    def validate_summary(self, __key: str, __summary: str):
        # 비어있거나 2048자 이하
        if __summary and len(__summary) > 2048:
            raise DatabaseRegexNotMatched(
                ItemQueryErrorCode.SUMMARY_MATCHED_FAILED, "summary not matched"
            )
        return __summary


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
