import json
from abc import ABCMeta, abstractmethod

import sqlalchemy.engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session


class DatabaseConnection(metaclass=ABCMeta):
    """ RDB 커넥션
        데이터베이스 엔진을 직접 관리하는 객체
        해당 객체는 DB 접속의 문제를 줄이기 위해
        하나의 서버에 하나의 객체만 생성되어야 하기 때문에 Singletone Pattern을 도입하였다.

        하위 클래스로 테스트용 커넥션과, 배포용 커넥션이 있다.
    """

    engine: sqlalchemy.engine.base.Engine
    session: scoped_session

    @abstractmethod
    def __init__(self, *args):
        pass

    def get_engine(self) -> object:
        # 데이터베이스 내부 엔진 얻기
        return self.engine

    def get_session(self) -> object:
        # 데이터베이스 내부 세션 얻기
        return self.session

    @abstractmethod
    def connect(self):
        # 외부 연결
        pass

    @abstractmethod
    def disconnect(self):
        # 연결 해제
        pass


class TestingDatabaseConnection(DatabaseConnection):
    """ 테스팅용 데이터베이스 커넥션

        오로지 unittest에서만 사용해야 하며 배포용으로는 사용 금지
    """

    __state = {"engine": None, "session": None}

    def __init__(self, *args):
        # __state에서 기존의 엔진 가져오기
        # 이걸로 여러개 생성해도 실제 DB 커넥션은 단 하나만 생성된다.
        self.__dict__ = self.__state

    def connect(self):
        if not self.engine:
            # engine이 없는 경우 -> connection을 활성화하지 않음
            # test.db 파일을 이용한 테스팅
            self.engine = create_engine("sqlite:///test.db")
            self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def disconnect(self):
        # 연결 해제
        if self.engine and self.session:
            self.session.remove()
        self.session, self.engine = None, None


class ProductionDatabaseConnection(DatabaseConnection):
    """ 배포용 데이터베이스 커넥션
    """

    __state = {"engine": None, "session": None}

    def __init__(self, *args):
        self.__dict__ = self.__state

    def connect(self):
        # Production의 경우 config 파일에서 데이터베이스 정보를 불러와서 킨다
        with open("configs/rdb.json", "rt") as f:
            data = json.load(f)

            self.engine = create_engine(
                f"mysql+pymysql://{data['user']}:{data['password']}@{data['host']}:{data['port']}/{data['database']}")
            self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def disconnect(self):
        if self.engine and self.session:
            self.session.remove()
        self.session, self.engine = None, None
