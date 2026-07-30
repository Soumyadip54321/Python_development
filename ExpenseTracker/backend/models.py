'''
Script that contains all ORM classes
'''
from datetime import date
from sqlalchemy import Text,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    pass

class Expense(Base):
    '''
    ORM class that connects to Expense table in the database.
    '''
    __tablename__ = 'expenses'

    id:Mapped[int]
    expense_id:Mapped[int] = mapped_column(primary_key=True)
    expense_date:Mapped[date] = mapped_column(nullable=False)
    amount:Mapped[float] = mapped_column(nullable=False)
    category:Mapped[str] = mapped_column(nullable=False)
    notes:Mapped[str] = mapped_column(Text)

class LoggedUsers(Base):
    '''
    ORM class that connects to LOGGED_USERS table in the database.
    '''
    __tablename__ = 'LOGGED_USERS'

    ID:Mapped[int] = mapped_column(primary_key=True)
    USERNAME:Mapped[str] = mapped_column(String(45),nullable=False)
    PASSWORD:Mapped[str] = mapped_column(nullable=False)



