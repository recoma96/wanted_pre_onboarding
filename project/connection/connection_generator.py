import sys

from project.connection.database_connection import DatabaseConnection, TestingDatabaseConnection, \
    ProductionDatabaseConnection


class DatabaseConnectionGenerator:
    """ 데이터베이스 커넥션 생성기
        직접 DBConnection을 생성하는 것이 아닌
        해당 클래스의 메소드를 통해 Connection을 관리한다.
    """

    @staticmethod
    def get() -> DatabaseConnection:
        if 'unittest' in sys.modules:
            # 테스트용
            return TestingDatabaseConnection()
        else:
            # 배포용
            return ProductionDatabaseConnection()

    @staticmethod
    def get_engine() -> object:
        # 엔진 호출
        if 'unittest' in sys.modules:
            return TestingDatabaseConnection().get_engine()
        else:
            return ProductionDatabaseConnection().get_engine()

    @staticmethod
    def get_session() -> object:
        # 세션 호출
        if 'unittest' in sys.modules:
            return TestingDatabaseConnection().get_session()
        else:
            return ProductionDatabaseConnection().get_session()