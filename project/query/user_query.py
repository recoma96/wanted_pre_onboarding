import sqlalchemy.exc

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import User, DatabaseRegexNotMatched, generate_id
from project.query.query import Query
from typing import List, Dict


class UserQuery(Query):
    """ 유저 관련 쿼리 """

    @staticmethod
    def create(__name: str) -> int:
        """ 유저 생성 """
        db_session = DatabaseConnectionGenerator.get_session()

        try:
            # create
            user: User = User(id=generate_id(), name=__name)
            db_session.add(user)
            db_session.commit()
        except DatabaseRegexNotMatched as e:
            # 이름이 맞지 않음
            return e.code
        except sqlalchemy.exc.IntegrityError as e:
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
    def update(__key: str, __target_value: str, __new_name: str) -> int:
        """ 유저 이름 수정 """

        db_session = DatabaseConnectionGenerator.get_session()
        # 유저 찾기

        if __key == "name":
            user = db_session.query(User).filter(User.name == __target_value).scalar()
        elif __key == "id":
            user = db_session.query(User).filter(User.id == __target_value).scalar()
        else:
            raise TypeError("Key is not matched")

        if not user:
            # 유저가 존재하지 않는 경우
            return User.USER_NOT_EXIST

        try:
            user.name = __new_name
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
    def delete(__key: str, __value: str) -> int:
        db_session = DatabaseConnectionGenerator.get_session()

        if __key == "name":
            user = db_session.query(User).filter(User.name == __value).scalar()
        elif __key == "id":
            user = db_session.query(User).filter(User.id == __value).scalar()
        else:
            raise TypeError("Key is not matched")

        if not user:
            return User.USER_NOT_EXIST

        try:
            db_session.delete(user)
            db_session.commit()
        except Exception as e:
            # 에러 발생 시 롤백과 동시에 에러 호출
            db_session.rollback()
            raise e
        # 삭제 성공
        return 0

    """ Expected Queries """

    @staticmethod
    def search_users(__regex: str) -> List[Dict[str, str]]:
        """ 패턴으로 여러 사용자 찾기 """
        db_session = DatabaseConnectionGenerator.get_session()
        target: List[User] = db_session.query(User).filter(User.name.contains(__regex)).all()

        res: List[Dict[str, str]] = []

        for u in target:
            res.append({
                "name": u.name,
                "id": u.id
            })

        return res
