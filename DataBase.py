from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


Base = declarative_base()


class Database:
    def __init__(self):
        db_name = 'mainDB.db'
        self.engine = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.session = session()

    def get_categories(self, **kwargs):
        if kwargs:
            filters = []
            for key, value in kwargs.items():
                filters.append(getattr(Category, key) == value)
            query = self.session.query(Category).filter(and_(*filters)).all()
        else:
            query = self.session.query(Category).all()
        return query

    def get_transactions(self, **kwargs):
        if kwargs:
            filters = []
            for key, value in kwargs.items():
                if value != -1:
                    if key != 'date_transaction':
                        filters.append(getattr(Transaction, key) == value)
                    else:
                        filters.append(getattr(Transaction, key) >= value)
            query = self.session.query(Transaction).filter(and_(*filters)).all()
        else:
            query = self.session.query(Transaction).all()
        return query

    def add_category(self, category_name):
        new_category = Category(name_category=category_name)
        self.session.add(new_category)
        self.session.commit()

    def delete_category(self, category_id):
        category_to_delete = self.session.query(Category).filter_by(category_id=category_id).first()
        if category_to_delete:
            self.session.delete(category_to_delete)
            self.session.commit()

    def add_transaction(self, name, price, type_, category_id, date_, comment):
        category = self.session.query(Category).filter_by(category_id=category_id).first()
        new_transaction = Transaction(name_transaction=name, price_transaction=price, date_transaction=date_,
                                      type_transaction=type_, comment_transaction=comment,
                                      category_id=category.category_id)
        self.session.add(new_transaction)
        self.session.commit()

    def delete_transaction(self, transaction_id):
        transaction_to_delete = self.session.query(Transaction).filter_by(transaction_id=transaction_id).first()
        if transaction_to_delete:
            self.session.delete(transaction_to_delete)
            self.session.commit()


class Transaction(Base):
    __tablename__ = "transaction"
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    name_transaction = Column(String, nullable=True)
    price_transaction = Column(Float, nullable=True)
    date_transaction = Column(DateTime, nullable=True)
    type_transaction = Column(String, nullable=True)
    comment_transaction = Column(Text)
    category_id = Column(Integer, ForeignKey('category.category_id', ondelete='CASCADE'))
    category = relationship('Category', back_populates='transactions')


class Category(Base):
    __tablename__ = "category"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name_category = Column(String, nullable=True, unique=True)
    transactions = relationship("Transaction", back_populates='category', passive_deletes=True)
