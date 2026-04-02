# 크롤러가 수집한 데이터 테이블 - 크롤러 DB에서 읽기만 함
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


email_identifier = Table(
    'email_identifier', Base.metadata,
    Column('domain_id', Integer, ForeignKey('domains.id')),
    Column('email_id', Integer, ForeignKey('emails.id'))
)

address_identifier = Table(
    'address_identifier', Base.metadata,
    Column('domain_id', Integer, ForeignKey('domains.id')),
    Column('address_id', Integer, ForeignKey('addresses.id'))
)


class CrawlerDomain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(32), unique=True)
    scheme = Column(String(5), nullable=False)
    netloc = Column(String(255), unique=True, nullable=False)


class CrawlerEmail(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    domains = relationship('CrawlerDomain', secondary=email_identifier)


class CrawlerAddress(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    address = Column(String(34), unique=True)
    domains = relationship('CrawlerDomain', secondary=address_identifier)
