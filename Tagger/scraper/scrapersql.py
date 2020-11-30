from taggermodels import *
from sqlalchemy import insert, select

##Insertion

def insert_file(session,fileinfo):
    exists = session.query(File.id).filter(
        File.title == fileinfo[1]).all()
    if exists:
        res = insert_file(session,[fileinfo[0],fileinfo[1]+" i",fileinfo[2]])
        return res
    else:
        ins = File.__table__.insert().values(
                length=fileinfo[0], title=fileinfo[1], link=fileinfo[2])
        result = session.execute(ins)
        return result.inserted_primary_key[0]

def insert_both(session, fileinfo, tagword):
    """Inserts a file, a list of tags, and matches between them.
        Checks to ensure unique tag.names."""
    taglist = tagword.split(",")
    tag_id_list = []
    for i in taglist:
        q = session.query(Tag.id).filter(Tag.name==i).scalar()
        if q:
            tag_id_list.append(q)
        else:
            ins = Tag.__table__.insert().values(name=i)
            result = session.execute(ins)
            tag_id_list.append(result.inserted_primary_key[0])
    new_file_id = insert_file(session,fileinfo)
    session.commit()
    for i in tag_id_list:
        ins = Match.__table__.insert().values(
            file_id=new_file_id, tag_id=i)
        session.execute(ins)
    session.commit()
