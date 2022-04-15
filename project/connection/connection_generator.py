import sys

import sqlalchemy

from project.connection.database_connection import DatabaseConnection, TestingDatabaseConnection, \
    ProductionDatabaseConnection
from sqlalchemy.orm.scoping import scoped_session


class DatabaseConnectionGenerator:
    """ 데이터베이스 커넥션 생성기
        직접 DBConnection을 생성하는 것이 아닌
        해당 클래스의 메소드를 통해 Connection을 관리한다.
    """

    @staticmethod
    def get() -> DatabaseConnection:
        """ 객체 자체를 리턴 """
        if 'unittest' in sys.modules:
            # 테스트용
            return TestingDatabaseConnection()
        else:
            # 배포용
            return ProductionDatabaseConnection()

    @staticmethod
    def get_engine() -> sqlalchemy.engine.base.Engine:
        """ 엔진 호출 """
        if 'unittest' in sys.modules:
            return TestingDatabaseConnection().get_engine()
        else:
            return ProductionDatabaseConnection().get_engine()

    @staticmethod
    def get_session() -> scoped_session:
        """ 세션 호출 """
        # 주로 쿼리를 실행할 때 사용
        if 'unittest' in sys.modules:
            return TestingDatabaseConnection().get_session()
        else:
            return ProductionDatabaseConnection().get_session()
