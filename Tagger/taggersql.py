from sqlalchemy import insert, select, asc, func, exists

from taggermodels import *


##Selection

#Selects a subset of File
def select_file(session, tagword):
    """Returns a list of all File entries with entries in Match matching
    all tags in tagword.

    Parameters:
        session: An SQLAlchemy database session.
        tagword (string): A string of 'tags' separated by ','.

    Returns:
        q (SQLAlchemy object): Information on entries in table File with
            entries in table Match corresponding to entries in table Tag
            corresponding to all 'tags' in tagword.
    """
    taglist = tagword.split(",")
    q = session.query(File).filter(
            File.id==Match.file_id).filter(
                Match.tag_id==Tag.id).filter(
                    Tag.name.in_(taglist)).group_by(
                        Match.file_id).having(
                            func.count(1) == len(taglist)).order_by(
                                asc(File.title)).all()
    #Effectively: Get all Tag.id for tags in taglist, find File with
    #Matches to all of them.

    return q


def get_link(session,title):
    """Returns File.link for File.title.

    Parameters:
        session: An SQLAlchemy database session.
        title (string): A title to be queried in session.

    Returns:
        r (string): Data in link attribute for entry in table File in
            session with title == title.
    """
    r =session.query(File.link).filter(File.title == title).one()
    return r[0]


def get_all_file_titles(session):
    """Returns all file.title fields in db.

    Parameters:
        session: An SQLAlchemy database session.

    Returns:
        q (list): A sorted list of all title attributes of entries in
            table File in session.
    """
    q = session.query(File.title).all()
    return sorted(q)


def get_all_tag_names(session):
    """Returns all tag.name fields in session.

    Parameters:
        session: An SQLAlchemy database session.

    Returns:
        q (list): A sorted list of all name attributes of entries in
            table Tag in session.
    """
    q = session.query(Tag.name).all()
    return sorted(q)

def get_all_matchs(session,title):
    """Returns all tag.name entries in session with Match entries
    linked with File.title.

    Parameters:
        session: An SQLAlchemy database session.

    Returns:
        q (list): A sorted list of all name attributes of entries in
            table Tag in session which also have entries in table Match
            coupled with id of File entry with title == title.
    """
    if title:
        fileid = session.query(File.id).filter(
            File.title == title).one()
        tagq = session.query(Tag.name).filter(
            Match.tag_id == Tag.id).filter(
                Match.file_id == fileid[0]).order_by(
                    asc(Tag.name)).all()
        return sorted(tagq)
    else:
        return



##Insertion

def insert_file(session, fileinfo, tagword):
    """Inserts fileinfo into table File in session and entries in table
    Match for each tag in tagword coupled with the new File entry.

    Parameters:
        session: An SQLAlchemy database session.
        fileinfo (list): Length, Title, Link to be entered into session.
        tagword (string): A string of 'tags' separated by ','.

    Returns:
        True if insertion was successful, else False.

    Side-effects:
        Entry in table File created with fileinfo. Entries in table
            Match created coupling new File entry with each 'tag' in
            Tagword.
    """
    unique = session.query(File).filter(~ exists().where(
        File.title==fileinfo[1])).all()
    if unique:
        file_ins = File.__table__.insert().values(
            length=fileinfo[0], title=fileinfo[1], link=fileinfo[2])
        result = session.execute(file_ins)
        ins_file_id = result.lastrowid
        session.commit()
        taglist = tagword.split(",")
        q = session.query(Tag.id).filter(
                Tag.name.in_(taglist)).all()
        for row in q:
            match_ins = Match.__table__.insert().values(
                file_id=ins_file_id, tag_id=row[0])
            session.execute(match_ins)
        session.commit()
        return True
    else:
        return False


def insert_tag (session,tagword):
    """Inserts each 'tag' in tagword into table Tag in session.

    Parameters:
        session: An SQLAlchemy database session.
        tagword (string):  A string of 'tags' separated by ','.

    Returns:
        q (list): A sorted list of all tags in Tagword which already
            exist in table Tag.

    Side-effects:
        New entries created in table Tag in session for each
            non-duplicate tag in tagword.
    """
    taglist = tagword.split(",")
    r = []
    for new_tag in taglist:
        unique = session.query(Tag).filter(~ exists().where(Tag.name==new_tag)).all()
        if unique:
            ins = Tag.__table__.insert().values(name=new_tag)
            session.execute(ins)
            session.commit()
        else:
            r.append(new_tag)
    return sorted(r)



##Deletion

def delete_tag(session,tagword):
    """Deletes all 'tags' in tagword from session.

    Parameters:
        session: An SQLAlchemy database session.
        tagword (string):  A string of 'tags' separated by ','.

    Side-effects:
        All entries in table Tag in session with name in tagword
            deleted.
        All entries in table Match in session matching tags in
            tagword deleted.
    """
    taglist = tagword.split(",")
    q = session.query(Tag.id).filter(
            Tag.name.in_(taglist)).all()
    for row in q:
        session.query(Tag).filter(Tag.id == row[0]).delete()
        session.query(Match).filter(Match.tag_id == row[0]).delete()
    session.commit()


def delete_file(session,title):
    """Deletes File.title == title from session.

    Parameters:
        session: An SQLAlchemy database session.
        title (string): A title to be deleted.

    Side-effects:
        Any entry in table File in session with title==title deleted
        All entries in table Match in session matching File.title
            deleted.
    """
    fileid = session.query(File.id).filter(File.title == title).scalar()
    session.query(File).filter(File.id == fileid).delete()
    session.query(Match).filter(Match.file_id == fileid).delete()
    session.commit()


def cleanup_files(session):
    """Deletes all entries in table File in session without any entry
        in table Match.

    Parameters:
        session: An SQLAlchemy database session.

    Side-effects:
        All entries in table File whose id do not exist in Match.file_id
            deleted.
    """
    s = session.query(File).filter(~ exists().where(
        Match.file_id==File.id)).all()
    for row in s:
        session.query(File).filter(File.id==row.id).delete()
    session.commit()
    
