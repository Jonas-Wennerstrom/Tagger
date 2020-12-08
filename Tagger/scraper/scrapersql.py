from taggermodels import *
from sqlalchemy import insert, select

##Insertion


def create_file_entry(session,fileinfo):
    exists = session.query(File).filter(File.title == fileinfo[1]).scalar()
    if exists:
        return create_file_entry(session,[fileinfo[0],
                                          fileinfo[1]+" i",
                                          fileinfo[2]])
    else:
        new_file = File(length=fileinfo[0],
                        title=fileinfo[1],
                        link=fileinfo[2])
    return new_file

def insert_both(session,fileinfo,taglist):  
    new_file = create_file_entry(session,fileinfo)
    for n in taglist:
        q = session.query(Tag).filter(Tag.name==n).scalar()
        if q:
            new_file.contains.append(q)
        else:
            new_tag = Tag(name=n)
            session.add(new_tag)
            new_file.contains.append(new_tag)
    session.add(new_file)
    session.commit()
