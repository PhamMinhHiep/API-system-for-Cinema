from sqlalchemy import Column, String, Integer, Float, ForeignKey, DATE
from sqlalchemy.orm import relationship
from database import Base


class UserInfo(Base):
    __tablename__ = "account1"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    passwd = Column(String)
    # account_id = Column(Integer, ForeignKey('account.id'))


class TicketModel(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orderfilm.id'))
    chair_id = Column(Integer, ForeignKey('chair.id'))
    schedule_id = Column(Integer, ForeignKey('schedule.id'))
    child1 = relationship('OrderModel', back_populates='parent')
    child2 = relationship('ChairModel', back_populates='parent')
    child3 = relationship('ScheduleModel', back_populates='parent')


class MovieInfo(Base):
    __tablename__ = "movie"
    id = Column(Integer, primary_key=True, index=True)
    typeFilm = Column(String)
    duration = Column(String)
    title = Column(String)
    release_date = Column(DATE)
    director = Column(String)
    cast = Column(String)
    Rated = Column(String)
    parent = relationship('ScheduleModel', back_populates='child1')


class ScheduleModel(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey('room.id'))
    movie_id = Column(Integer, ForeignKey('movie.id'))
    time_start = Column(String)
    price = Column(Float)
    parent = relationship('TicketModel', back_populates='child3')
    child1 = relationship('MovieInfo', back_populates='parent')
    child2 = relationship('RoomModel', back_populates='parent')


class CinemaInfo(Base):
    __tablename__ = "cinema"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    info = Column(String)
    city = Column(String)
    cinemas = relationship("RoomModel", back_populates="child")


class ChairModel(Base):
    __tablename__ = "chair"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("room.id"))
    position = Column(String)
    room = relationship("RoomModel", back_populates="chairs")
    parent = relationship('TicketModel', back_populates='child2')


class RoomModel(Base):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    cinema_id = Column(Integer, ForeignKey("cinema.id"))
    chairs = relationship("ChairModel", back_populates="room")
    child = relationship('CinemaInfo', back_populates='cinemas')
    parent = relationship('ScheduleModel', back_populates='child2')


class OrderModel(Base):
    __tablename__ = "orderfilm"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    state = Column(String)
    child = relationship('AccountModel', back_populates='parent2')
    parent = relationship('TicketModel', back_populates='child1')


class CustomerModel(Base):
    __tablename__ = "customer"
    fullname = Column(String)
    age = Column(Integer)
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    child = relationship('AccountModel', back_populates='parent', uselist=False)


class AccountModel(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    parent = relationship('CustomerModel', back_populates='child')
    parent2 = relationship('OrderModel', back_populates='child')
