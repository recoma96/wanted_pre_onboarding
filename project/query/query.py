from abc import ABCMeta, abstractmethod


class Query(metaclass=ABCMeta):
    
    """ 각 DB테이블에 대한 CRUD 쿼리
    """

    @staticmethod
    @abstractmethod
    def create(*args):
        pass

    @staticmethod
    @abstractmethod
    def remove(*args):
        pass

    @staticmethod
    @abstractmethod
    def update(*args):
        pass

    @staticmethod
    @abstractmethod
    def delete(*args):
        pass
