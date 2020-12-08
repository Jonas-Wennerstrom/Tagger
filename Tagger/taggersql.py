from sqlalchemy import insert, select, asc, func, exists

from taggermodels import *


##Selection

#Selects a subset of File
def select_file(session, taglist):
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
    q = session.query(File).join(
        File.contains).filter(
            Tag.name.in_(taglist)).group_by(
                File.title).having(
                    func.count()==len(taglist)).all()
    return q

def get_tags_from_names(session,taglist):
    return session.query(Tag).filter(Tag.name.in_(taglist)).all()

def get_link(session,title):
    """Returns File.link for File.title.
    """
    r =session.query(File.link).filter(
        File.title == title).scalar()
    return r


def get_all_file_titles(session):
    """Returns all file.title fields in db.
    """
    q = session.query(File.title).all()
    return sorted(q)


def get_all_tag_names(session):
    """Returns all tag.name fields in session.
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
        tagq = session.query(Tag.name).join(
            Tag.media).filter(
                File.title==title).all()
        return sorted(tagq)
    else:
        return



##Insertion

def insert_file(session, fileinfo, taglist):
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
    unique = not file_exists(session,fileinfo[1])
    if unique:
        q = get_tags_from_names(session,taglist)
        new_file = File(length=fileinfo[0],
                        title=fileinfo[1],
                        link=fileinfo[2])
        for t in q:
            new_file.contains.append(t)
        session.add(new_file)
        session.commit()
        return True
    else:
        return False


def insert_tag (session,taglist):
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
    insert_list = []
    skipped_list = []
    for new_tag in taglist:
        if not tag_exists(session,new_tag):
            insert_list.append(new_tag)
        else:
            skipped_list.append(new_tag)
    session.execute(Tag.__table__.insert(),
                    [{"name": t} for t in insert_list])
    session.commit()
    return sorted(skipped_list)



##Deletion

def delete_tag(session,taglist):
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
    q = get_tags_from_names(session,taglist)
    for row in q:
        session.delete(row)
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
    file = session.query(File).filter(File.title == title).scalar()
    session.delete(file)
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
    s = session.query(File.id).filter(~File.contains.any()).all()
    if s:
        session.execute(File.__table__.delete(),
                        [{"id": t[0]} for t in s])
        session.commit()
    
##Confirm functions
#These functions check if data exists in db

def file_exists(session,title):
    """Returns true if a file with title == title exists, else false."""
    s = session.query(exists().where(File.title == title)).scalar()
    return s

def tag_exists(session,name):
    """Returns true if a tag with name == name exists, else fales"""
    s = session.query(exists().where(Tag.name == name)).scalar()
    return s
