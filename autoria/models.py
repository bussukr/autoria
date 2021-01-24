from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from datetime import datetime
import pytz 

import autoria.settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(autoria.settings.SQLALCHEMY_DATABASE_URI)


def create_offers_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class TruckOffers(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "truck_offers"
    
    
    id = Column(Integer, primary_key=True)
    auto_id = Column('auto_id', Integer)
    product_link = Column('product_link', String)
    product_name = Column('product_name', String)
    brand = Column('brand', String)
    model = Column('model', String)
    production_date = Column('production_date', Integer)
    mileage = Column('mileage', Integer)
    body_type = Column('body_type', String)
    color = Column('color', String)
    gearbox_type = Column('gearbox_type', String)
    price_currency = Column('price_currency', String)
    price = Column('price', Float)
    price_eur = Column('price_eur', Float)
    price_usd = Column('price_usd', Float)
    usd_exch_rate = Column('usd_exch_rate', Float)
    eur_exch_rate = Column('eur_exch_rate', Float)
    description = Column('description', String)
    record_date = Column('record_date', DateTime, index=True, default=datetime.now(pytz.timezone('Europe/Kiev')))