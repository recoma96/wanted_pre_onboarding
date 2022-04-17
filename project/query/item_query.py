import datetime
from typing import List, Dict

import sqlalchemy.exc
from sqlalchemy import desc

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import User, Item, DatabaseRegexNotMatched, generate_id, ItemContents
from project.query.err_codes import ItemQueryErrorCode
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
               __target_money: int) -> ItemQueryErrorCode:
        """

        :param __user:          게시자 정보 이름 또는 아이디가 들어간다.
        :param __name:          상품 이름
        :param __summary:       상품에 대한 설명
        :param __end_date:      만료일
        :param __funding_unit:  1회당 금액   
        :param __target_money:  목표 금액
        :return: 에러 코드
        """

        # 유저 찾기
        user: Dict[str, object] = UserQuery.read(*__user)
        if not user:
            # 유저 없음
            return ItemQueryErrorCode.USER_NOT_EXISTS

        db_session = DatabaseConnectionGenerator.get_session()

        # DB에 insert
        try:
            item: Item = Item(
                item_id=generate_id(),
                user_id=user['id'],
                name=__name,
                end_date=__end_date,
                target_money=__target_money,
                funding_unit=__funding_unit
            )
            contents: ItemContents = ItemContents(
                item_id=item.item_id,
                summary=__summary
            )
            db_session.add(item)
            db_session.add(contents)
            db_session.commit()
        except DatabaseRegexNotMatched as e:
            # validate failed
            return e.code
        except sqlalchemy.exc.IntegrityError:
            # DB 상에서의 에러
            # rollback
            db_session.rollback()
            return ItemQueryErrorCode.ITEM_ALREADY_EXISTS
        except Exception as e:
            # 외의 에러
            db_session.rollback()
            raise e
        else:
            return ItemQueryErrorCode.SUCCEED

    @staticmethod
    def read(__key: str, __value: str) -> Dict[str, object]:

        # 상품 갖고오기
        db_session = DatabaseConnectionGenerator.get_session()

        # 상품 정보 갖고오기
        item: Item = None

        if __key == 'id':
            item = db_session.query(Item).filter(Item.item_id == __value).scalar()
        elif __key == "name":
            item = db_session.query(Item).filter(Item.name == __value).scalar()

        if not item:
            # 정보 없음
            return None

        # 컨텐츠 가져오기
        contents: ItemContents = \
            db_session.query(ItemContents).filter(ItemContents.item_id == item.item_id).scalar()

        # 개시자 정보 구하기
        user: Dict[str, object] = UserQuery.read("id", item.user_id)

        # 달성률 구하기
        percentage: float = (item.current_money / item.target_money) * 100

        return {
            "item_id": item.item_id,
            "name": item.name,
            "user_name": user['name'],
            "summary": contents.summary,
            "end_date": item.end_date,
            "funding_unit": item.funding_unit,
            "target_money": item.target_money,
            "current_money": item.current_money,
            "participant_size": item.participant_size,
            "funding_gage": percentage
        }

    @staticmethod
    def update(item_code: List[str],
               name: str = None,
               summary: str = None,
               end_date: datetime.datetime = None,
               funding_unit: int = None,
               participant_size: int = None,
               current_money: int = None) -> ItemQueryErrorCode:
        """ 상품 상세정보 갖고오기
        """
        # 상품 정보 갖고오기
        db_session = DatabaseConnectionGenerator.get_session()
        ikey, ivalue = item_code
        item: Item = None
        if ikey == 'id':
            item = db_session.query(Item).filter(Item.item_id == ivalue).scalar()
        elif ikey == "name":
            item = db_session.query(Item).filter(Item.name == ivalue).scalar()

        if not item:
            # 상품 없음
            return ItemQueryErrorCode.ITEM_NOT_EXISTS

        # contents 갖고오기
        contents: ItemContents = \
            db_session.query(ItemContents).filter(ItemContents.item_id == item.item_id).scalar()

        try:
            # item 정보 수정
            if name:
                item.name = name
            if end_date:
                item.end_date = end_date
            if funding_unit is not None:
                item.funding_unit = funding_unit
            if participant_size:
                item.participant_size = participant_size
            if current_money:
                item.current_money = current_money
            if summary is not None:
                contents.summary = summary
        except DatabaseRegexNotMatched as e:
            return e.code

        # DB에 업로드
        try:
            db_session.commit()
        except sqlalchemy.exc.IntegrityError:
            # DB 내부 에러
            # 보통 상품 이름이 충돌할 때 발생한다
            db_session.rollback()
            return ItemQueryErrorCode.ITEM_ALREADY_EXISTS
        except Exception as e:
            db_session.rollback()
            raise e

        return ItemQueryErrorCode.SUCCEED

    @staticmethod
    def delete(key: str, value: str) -> ItemQueryErrorCode:

        db_session = DatabaseConnectionGenerator.get_session()
        deleted_item: Item = None

        """ 아이템 삭제 """
        if key == "id":
            # 아이디를 이용한 삭제
            deleted_item = db_session.query(Item).filter(Item.item_id == value).scalar()
        elif key == "name":
            # 상풍명을 이용한 삭제
            deleted_item = db_session.query(Item).filter(Item.name == value).scalar()

        # 없음
        if not deleted_item:
            return ItemQueryErrorCode.ITEM_NOT_EXISTS

        # 삭제할 컨텐츠
        contents = \
            db_session.query(ItemContents).filter(ItemContents.item_id == deleted_item.item_id).scalar()
        try:
            db_session.delete(deleted_item)
            db_session.delete(contents)
            db_session.commit()
        except Exception as e:
            # DB 내부 오류
            db_session.rollback()
            raise e

        # 삭제 성공
        return ItemQueryErrorCode.SUCCEED

    """ expanded query """

    @staticmethod
    def __make_element_for_list(user: User, item: Item):

        # 리스트에 들어갈 항목을 만드는 데 사용하는 함수
        # 파라미터는 다음과 같다
        """
            name: 상품 이름
            user_name: 게시자 이름
            current_money: 총 달성 금액
            percentage: 달성률
            create_date: 생성일
            end_date: 종료일 (d-day)
        """

        return {
            "name": item.name,
            "user_name": user.name,
            "current_money": item.current_money,
            "percentage": (item.current_money / item.target_money) * 100,
            "end_date": item.end_date,
            "create_date": item.create_date
        }

    @staticmethod
    def read_item_list_by_name_regex(name_regex: str) -> List[Dict[str, object]]:
        """ 일부 문자열 패턴을 이용한 상품 리스트 구하기 """

        db_session = DatabaseConnectionGenerator.get_session()
        res: List[Dict[str, object]] = []

        # 검색
        for user, item in db_session.query(User, Item). \
                filter(User.id == Item.user_id). \
                filter(Item.name.like(f'%{name_regex}%')).all():
            res.append(ItemQuery.__make_element_for_list(user, item))

        return res

    """ Founding Table과 같이 사용하는 검색 쿼리 """

    @staticmethod
    def sort_by_createdate() -> List[Dict[str, object]]:
        """ 생성일을 기준으로 정렬 """

        db_session = DatabaseConnectionGenerator.get_session()
        res: List[Dict[str, object]] = []

        # 데이터 수집
        for user, item in db_session.query(User, Item). \
                filter(User.id == Item.user_id). \
                order_by(Item.create_date).all():
            res.append(ItemQuery.__make_element_for_list(user, item))

        return res

    @staticmethod
    def sort_by_fundingmoney() -> List[Dict[str, object]]:
        """ 펀딩코인순으로 정렬 """

        db_session = DatabaseConnectionGenerator.get_session()
        res: List[Dict[str, object]] = []

        # 데이터 수집
        for user, item in db_session.query(User, Item). \
                filter(User.id == Item.user_id). \
                order_by(desc(Item.current_money)).all():
            res.append(ItemQuery.__make_element_for_list(user, item))

        return res
