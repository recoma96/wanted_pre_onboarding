import sqlalchemy.exc

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import User, DatabaseRegexNotMatched, generate_id
from project.query.err_codes import UserQueryErrorCode
from project.query.query import Query
from typing import List, Dict


class UserQuery(Query):
    """ 유저 관련 쿼리 """

    @staticmethod
    def create(name: str) -> UserQueryErrorCode:
        """ 유저 생성 """
        db_session = DatabaseConnectionGenerator.get_session()

        try:
            # create
            user: User = User(id=generate_id(), name=name)
            db_session.add(user)
            db_session.commit()
        except DatabaseRegexNotMatched as e:
            # 이름이 맞지 않음
            return e.code
        except sqlalchemy.exc.IntegrityError:
            # DB 내부 에러
            # 동일한 이름의 유저를 생성하려고 할 때 발생한다.
            # 트랜잭션을 롤백한다.
            db_session.rollback()
            return UserQueryErrorCode.NAME_ALREADY_EXIST
        except Exception as e:
            # 기타 예외
            db_session.rollback()
            raise e
        else:
            # 성공 시 0 리턴
            return UserQueryErrorCode.SUCCEED

    @staticmethod
    def read(key: str, value: str) -> Dict[str, str]:
        """ 유저 정보 찾기 """

        db_session = DatabaseConnectionGenerator.get_session()
        
        # key에 따른 User 정보 찾기
        if key == "name":
            target = db_session.query(User).filter(User.name == value).scalar()
        elif key == "id":
            target = db_session.query(User).filter(User.id == value).scalar()
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
    def update(key: str, target_value: str, new_name: str) -> int:
        """ 유저 이름 수정 """

        db_session = DatabaseConnectionGenerator.get_session()
        # 유저 찾기

        if key == "name":
            user = db_session.query(User).filter(User.name == target_value).scalar()
        elif key == "id":
            user = db_session.query(User).filter(User.id == target_value).scalar()
        else:
            raise TypeError("Key is not matched")

        if not user:
            # 유저가 존재하지 않는 경우
            return UserQueryErrorCode.USER_NOT_EXIST

        try:
            user.name = new_name
            db_session.commit()
        except DatabaseRegexNotMatched as e:
            # 이름이 맞지 않음
            return e.code
        except sqlalchemy.exc.IntegrityError:
            # 동일한 이름의 유저를 생성하려고 할 때 발생한다.
            # 트랜잭션을 롤백한다.
            db_session.rollback()
            return UserQueryErrorCode.NAME_ALREADY_EXIST
        except Exception as e:
            # 기타 예외
            raise e
        else:
            # 성공 시 0 리턴
            return UserQueryErrorCode.SUCCEED

    @staticmethod
    def delete(key: str, value: str) -> int:
        """ User Remove Query
            그러나 해당 유저가 만든 상품까지 삭제를 하지 않고 이는 Manager단에서 상품 삭제를 수행한다
            TODO 현재 요구사항에는 User 삭제 API가 없으므로 추가 요구사항이 들어올 경우 Manager단에서 추가 구현 예정
        """
        db_session = DatabaseConnectionGenerator.get_session()

        if key == "name":
            user = db_session.query(User).filter(User.name == value).scalar()
        elif key == "id":
            user = db_session.query(User).filter(User.id == value).scalar()
        else:
            # key 매칭 실패
            raise TypeError("Key is not matched")

        if not user:
            # 해당 유저 없음
            return UserQueryErrorCode.USER_NOT_EXIST

        try:
            # 삭제 수행
            db_session.delete(user)
            db_session.commit()
        except Exception as e:
            # 에러 발생 시 롤백과 동시에 에러 호출
            db_session.rollback()
            raise e
        # 삭제 성공
        return UserQueryErrorCode.SUCCEED

    """ Expanded Queries """

    @staticmethod
    def search_users(regex: str) -> List[Dict[str, str]]:
        """ 패턴으로 여러 사용자 찾기 """
        db_session = DatabaseConnectionGenerator.get_session()
        target: List[User] = db_session.query(User).filter(User.name.contains(regex)).all()

        res: List[Dict[str, str]] = []

        for u in target:
            res.append({
                "name": u.name,
                "id": u.id
            })

        return res
