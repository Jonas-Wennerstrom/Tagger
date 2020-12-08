from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class File(Base):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True)
    length = Column(Integer)
    title = Column(String, unique=True)
    link = Column(String)
    contains = relationship('Tag',
                            secondary='match',
                            back_populates='media'
                            )

class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    media = relationship('File',
                         secondary='match',
                         back_populates='contains'
                         )

class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("file.id"))
    tag_id = Column(Integer, ForeignKey("tag.id"))    
