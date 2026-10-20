from __future__ import annotations
import os, hashlib, secrets, hmac
from datetime import datetime, timedelta, timezone, date
from decimal import Decimal
from sqlalchemy import create_engine, String, Text, ForeignKey, Numeric, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./pulse.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(engine, expire_on_commit=False)
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'
    id:Mapped[str]=mapped_column(String,primary_key=True,default=lambda:secrets.token_hex(12))
    email:Mapped[str]=mapped_column(String,unique=True,index=True)
    name:Mapped[str]=mapped_column(String)
    password_hash:Mapped[str]=mapped_column(String)
class Organization(Base):
    __tablename__='organizations'
    id:Mapped[str]=mapped_column(String,primary_key=True,default=lambda:secrets.token_hex(12))
    name:Mapped[str]=mapped_column(String)
    currency:Mapped[str]=mapped_column(String,default='EUR')
    opening_balance:Mapped[Decimal]=mapped_column(Numeric(18,2),default=0)
    demo:Mapped[bool]=mapped_column(default=False)
    settings:Mapped[str]=mapped_column(Text,default='{}')
class Membership(Base):
    __tablename__='memberships'
    __table_args__=(UniqueConstraint('user_id','org_id'),)
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True)
    org_id:Mapped[str]=mapped_column(ForeignKey('organizations.id'),index=True)
    role:Mapped[str]=mapped_column(String,default='OWNER')
class AuthSession(Base):
    __tablename__='sessions'
    token_hash:Mapped[str]=mapped_column(String,primary_key=True)
    user_id:Mapped[str]=mapped_column(ForeignKey('users.id'))
    expires_at:Mapped[datetime]=mapped_column(DateTime)
class Transaction(Base):
    __tablename__='transactions'
    __table_args__=(UniqueConstraint('org_id','reference'),)
    id:Mapped[str]=mapped_column(String,primary_key=True,default=lambda:secrets.token_hex(12))
    org_id:Mapped[str]=mapped_column(ForeignKey('organizations.id'),index=True)
    amount:Mapped[Decimal]=mapped_column(Numeric(18,2))
    date:Mapped[date]=mapped_column(Date)
    direction:Mapped[str]=mapped_column(String)
    category:Mapped[str]=mapped_column(String)
    description:Mapped[str]=mapped_column(String)
    reference:Mapped[str]=mapped_column(String)
    currency:Mapped[str]=mapped_column(String,default='EUR')
    source:Mapped[str]=mapped_column(String,default='manual')
class Invoice(Base):
    __tablename__='invoices'
    id:Mapped[str]=mapped_column(String,primary_key=True,default=lambda:secrets.token_hex(12))
    org_id:Mapped[str]=mapped_column(ForeignKey('organizations.id'),index=True)
    number:Mapped[str]=mapped_column(String)
    counterparty:Mapped[str]=mapped_column(String)
    email:Mapped[str]=mapped_column(String)
    amount:Mapped[Decimal]=mapped_column(Numeric(18,2))
    paid:Mapped[Decimal]=mapped_column(Numeric(18,2),default=0)
    due_date:Mapped[date]=mapped_column(Date)
    direction:Mapped[str]=mapped_column(String)
class Record(Base):
    __tablename__='records'
    id:Mapped[str]=mapped_column(String,primary_key=True,default=lambda:secrets.token_hex(12))
    org_id:Mapped[str]=mapped_column(ForeignKey('organizations.id'),index=True)
    kind:Mapped[str]=mapped_column(String,index=True)
    data:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc).replace(tzinfo=None))
def password_hash(password):
    salt=secrets.token_hex(16)
    return salt+':'+hashlib.scrypt(password.encode(),salt=salt.encode(),n=16384,r=8,p=1).hex()
def verify_password(password, encoded):
    salt,digest=encoded.split(':')
    return hmac.compare_digest(hashlib.scrypt(password.encode(),salt=salt.encode(),n=16384,r=8,p=1).hex(),digest)
def init_db(): Base.metadata.create_all(engine)
