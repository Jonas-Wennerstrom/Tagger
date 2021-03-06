########################
## Tagger
##
## A database management system and GUI.
##
## Author: Jonas Wennerström
## https://github.com/Jonas-Wennerstrom
########################

import os.path
import ntpath
import math
from os import startfile

from appJar import gui
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from taggersql import *
from taggercreatedb import *



###Global variables.
#Column of main button positions
BUTTON_POS = 2
#Max number of Properties shown in each tab.
MAX_PROPS = 10
#Window size on launch
WINDOW_SIZE = "900x600"
#All auto-entries containing all file names
AUTO_ENTRIES = ["Remove file","Same title"]
#All tag table 'names'
TAG_TABLE_PREFIXES = ["Tags to match","Tags to filter",
                      "Tags to delete", "New matched tags"]
#Used to store File title: File link to reduce SQL queries
FILE_DICT = {}
##Alterable from GUI
#How play_window will display results
DISPLAY_OPTION = "Overview"
#Max number of entries in each Property
MAX_PROPSIZE = 10
#To be defined through user selection of db file
session = None

#Initializiation of GUI
app = gui()


###Aux functions

##Information-gathering functions
#These functions collect user-supplied information from the GUI for use
#in other functions.

def list_files():
    """Returns a list of all file.name from the db in the current
    session.
    """
    if not session:
        no_session_warning()
        return None
    r = []
    q_res = get_all_file_titles(session)
    for row in q_res:
        r.append(row.title)
    return r


def listify_ticked(prop_title):
    """Returns a list of all ticked values in Properties with titles
    beginning with prop_title.

    Parameters:
        prop_title (str): Prefix of properties inspected.

    Returns:
        taglist (str list): List of all 'ticked' values.
    """
    if not session:
        no_session_warning()
        return None
    taglist = []
    if prop_title not in TAG_TABLE_PREFIXES:
        raise Exception("Invalid argumentto listify_ticked: "
                        "Value of prop_titles was: "
                        "{}".format(prop_titles))
    for i in range(MAX_PROPS):
        tdict = app.getProperties(prop_title + str(i))
        for x in tdict:
            if tdict.get(x):
                taglist.append(x)
    return taglist


def update_auto_entries():
    """Updates all auto entries in the GUI to contain all file titles."""
    for i in AUTO_ENTRIES:
        app.changeAutoEntry(i,list_files())



##Minor functions
#These functions perform minor tasks or update the GUI

def open_file(title):
    """Queries active database for file.title == title, then opens
    corresponding link.

    Parameters:
        title(string): File title to be queried in db.

    Side-effect:
        Calls on os to open link provided in db if one exists.
    """
    if not session:
        no_session_warning()
        return None
    global FILE_DICT
    if title.startswith("Open the file "):
        title = title[len("Open the file "):]
    #Poor solution but one I'm uncertain of how to improve
    fileinfo = FILE_DICT[title]
    path = fileinfo.link
    if path and path != " ":
        startfile(path)
    else:
        app.errorBox("No link", "There is no link to '"+title+"'.",
                     parent="Play file")


def inspect_file(title):
    """Shows information of a single file. Information collected from "
    FILE_DICT[title]. 
    """
    global FILE_DICT
    fileinfo = FILE_DICT[title]
    app.openSubWindow("Inspect file")
    app.emptyCurrentContainer()
    linktitle = "Open the file "+title
    app.addLabel("insp_l", "Length", 0,0)
    app.addLabel("insp_tl", "Title", 0,1)
    app.addLabel("insp_tg", "Tags", 0,2)
    app.addLabel(title+"insp_l", fileinfo.length,1,0)
    app.addLink("Open the file "+title,open_file,1,1)
    tag_res = fileinfo.contains
    msg_title = "All "+linktitle+" tags"
    app.addEmptyMessage(msg_title,1,2)
    msg_list = []
    for tag in tag_res:
        msg_list.append(tag.name)
        msg_list.append("\n")
    msg_list.pop()
    msg_string = ''.join(msg_list)
    app.setMessage(msg_title, msg_string)
    #Styling
    app.setMessageAlign(msg_title, "left")
    app.setLabelAlign(title+"insp_l","right")
    app.setLinkAlign(linktitle, "left")
    app.setLabelWidth(title+"insp_l",10)
    app.setLinkWidth("Open the file "+title,70)
    app.setMessageWidth(msg_title,200)
    app.stopSubWindow()
    app.showSubWindow("Inspect file")

    
def path_leaf(path):
    """Given a filepath, returns filename."""
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def make_tag_tables():
    """Empties and repopulates all Properties.

    Side-effects:
        Updates GUI Properties with and Message 'existing_tags'
    """
    if not session:
        no_session_warning()
        return None
    tdict = {}
    tlist = get_all_tag_names(session)
    tmp = "Existing tags:\n"
    for i in tlist:
        tmp = tmp + i[0] + "\n"
    app.setMessage("existing_tags",tmp)
    num_properties = min(math.ceil(len(tlist)/MAX_PROPSIZE),MAX_PROPS)
    #Calculates how many properties are needed
    app.clearAllProperties()
    for i in range(num_properties):
        start = i*MAX_PROPSIZE
        end = (i+1)*MAX_PROPSIZE
        for n in tlist[start:end]:
            tdict[n[0]] = False
        for t in TAG_TABLE_PREFIXES:
            curr_title = t+str(i)
            app.showProperties(curr_title)
            props = app.getProperties(curr_title)
            for p in props:
                app.deleteProperty(curr_title,p)
            app.setProperties(curr_title, tdict)
        tdict.clear()
        #Note: appJar makes a copy of tdict within Properties
    for i in range(num_properties,MAX_PROPS):
        for t in TAG_TABLE_PREFIXES:
            curr_title = t+str(i)
            app.hideProperties(curr_title)


def pop_upd_tab(btn):
    """Populates the Update file tab with data related to title
        supplied by user in the 'Same title' entry. Only updates
        other entries in tab if they are empty.
    """
    title = app.getEntry("Same title")
    if file_exists(session,title):
        prop_dict = {}
        file = get_file(session,title)
        if app.getEntry("New length") == "":
            app.setEntry("New length", file.length)
        if app.getEntry("New link") == "":
            app.setEntry("New link",file.link)
        for i in range(MAX_PROPS):
            prop_dict[i] = app.getProperties("New matched tags"+str(i))
        for tag in file.contains:
            for i in prop_dict:
                if tag.name in prop_dict[i]:
                    app.setProperty("New matched tags"+str(i),
                                    tag.name,value=True)
                    break
            

    
###Prep functions
#These functions are called by user events. They gather data and call
#SQL functions.

##Inspection

def lookup_file():
    """Uses listify_ticked and select_file to query the session
    database. Returns all file information for all files tagged
    with tags selected in Properties prefixed with
    'Tags to filter'.
    """
    if not session:
        no_session_warning()
        return None
    taglist = listify_ticked("Tags to filter")
    files = select_file(session,taglist)
    return files


##Insertion

def add_file(btn):
    """Inserts file and matches into session db. Takes data from
    GUI Entries and Properties based on btn.

    Parameters:
        btn (string): Title of button pushed by user.

    Side-effects:
        Inserts new entry into database. Updates GUI to show success
        or failure to user. Updates AutoEntries 'Remove file',
        "Same title" on success if btn == "Add file".
    """
    if not session:
        no_session_warning()
        return None
    add_dict = {
        "Length": "Length",
        "Title": "Title",
        "Link": "Link",
        "Label": "add_file_res",
        "Prefix": "Tags to match"
        }
    upd_dict = {
        "Length": "New length",
        "Title": "Same title",
        "Link": "New link",
        "Label": "upd_file_res",
        "Prefix": "New matched tags"
        }
    master_dict = {"Add file": add_dict,
                   "Update file": upd_dict}
    if btn in master_dict:
        curr_dict = master_dict[btn]
    else:
        raise Exception("Invalid argument to add_file: Value of btn "
                        "was: {}".format(btn))
    file_length = app.getEntry(curr_dict["Length"])
    if not file_length:
        file_length = 0
    file_title = app.getEntry(curr_dict["Title"])
    if not file_title:
        app.setLabel(curr_dict["Label"], "Please include a title.")
        return None
    file_link = app.getEntry(curr_dict["Link"])
    if not file_link:
        file_link = " "
    tags = listify_ticked(curr_dict["Prefix"])
    if tags == "":
        app.setLabel(curr_dict["Label"],
                     "Please ensure the file is tagged.")
    else:
        inserted = insert_file(session,
                               [file_length,file_title,file_link],
                               tags)
        if inserted: 
            app.clearEntry(curr_dict["Length"])
            app.clearEntry(curr_dict["Title"])
            app.clearEntry(curr_dict["Link"])
            for i in range (MAX_PROPS):
                app.clearProperties(curr_dict["Prefix"] + str(i))
            if btn == "Add file":
                update_auto_entries()
                app.setLabel(curr_dict["Label"], file_title +
                         " successfully added.")
            elif btn == "Update file":
                app.setLabel(curr_dict["Label"], file_title +
                             " successfully updated.")
        else:
            app.setLabel(curr_dict["Label"], "A file with that title "
                         "already exists. Please change the title.")
            #Note: Update will already have deleted entry.


def add_tag(btn):
    """Inserts tag(s) provided by user in Entry 'new_tags' into
    session database. Updates GUI Properties. Clears entry 'new_tags'.

    btn is not used; it is built-in appJar functionality.
    """
    if not session:
        no_session_warning()
        return None
    app.setLabel("add_tag_dupes", "")
    taglist = app.getEntry("new_tags")
    dupes = insert_tag(session,taglist)
    app.clearEntry("new_tags")
    app.setLabel("add_tag_result", "Tags added.")
    if dupes:
        dupeword =""
        for t in dupes:
            dupeword = dupeword + str(t) + ", "
        dupeword = dupeword[0:-2]
        app.setLabel("add_tag_dupes", "Tags skipped due to "
                     "duplication: "+dupeword)
    make_tag_tables()
    app.clearEntry("new_tags")



##Deletion

def del_file(btn):
    """Deletes entry in database with file.title == value in Entry
    decided by btn. Possibly updates 'Remove file'.
    """
    if not session:
        no_session_warning()
        return None
    del_dict = {"Action": "Delete",
                "Entry": "Remove file",
                "Box": "Delete file?",
                "Confirm": "Are you sure you want "
                "to delete the file ",
                "Update entries": True,
                "Res label": "del_file_res"}
    upd_dict = {"Action": "Update",
                "Entry": "Same title",
                "Box": "Update file?",
                "Confirm": "Are you sure you want "
                "to update the file ",
                "Update entries": False,}
    btn_dict = {"Delete file": del_dict,
                "Update file": upd_dict
                }
    if btn in btn_dict:
        curr_dict = btn_dict[btn]
    else:
        raise Exception("Invalid argument to del_file: Value of btn "
                        "was: {}".format(btn))
    title = app.getEntry(curr_dict["Entry"])
    confirm = app.yesNoBox(curr_dict["Box"], curr_dict["Confirm"]
                            + title + "?")
    if confirm:
        if curr_dict["Action"] == "Update":
            delete_file(session,title)
        else:
            if file_exists(session,title):
                delete_file(session,title)
                if "Update entries" in curr_dict:
                    update_auto_entries()
                    app.clearEntry(curr_dict["Entry"])
                    if "Res label" in curr_dict:
                        app.setLabel(curr_dict["Res label"], title+
                                     " deleted.")
            else:
                if "Res label" in curr_dict:
                    app.setLabel(curr_dict["Res label"], "No file with "
                                 "title "+title+" exists. Please use "
                                 "the autocomplete function.")
                #Note: Update will already have checked existence.

    
def del_tag(btn):
    """Deletes all db entries in table Tag where Tag.name is 'ticked'
    by user in Properties prefixed with 'Tags to delete'. Updates GUI.

    btn is not used; it is built-in appJar functionality.
    """
    if not session:
        no_session_warning()
        return None
    taglist = listify_ticked("Tags to delete")
    confirm = app.yesNoBox("Delete tags?", "Are you sure you want to "
                           "delete the tags " + taglist+"?")
    if confirm:
        delete_tag(session,taglist)
        make_tag_tables()
    else:
         for i in range(MAX_PROPS):
            app.clearProperties("Tags to delete"+str(i))

##Update
#Updates a file though destruction and creation
def update_file(btn):
    """Calls del_file and add_file to effectively update entry with
    file.title chosen by user in GUI.

    Parameters:
        btn(string): Button pushed by user. Not used.

    Side-effects:
        Deletes entries in file and match. Creates new entries in file
        and match.
    """
    if not session:
        no_session_warning()
        return None
    cmd = "Update file"
    title = app.getEntry("Same title")
    if file_exists(session,title):
        del_file(cmd)
        add_file(cmd)
        app.clearEntry("New length")
        app.clearEntry("Same title")
        app.clearEntry("New link")
    else:
        app.setLabel("upd_file_res", "No file named "+title+" exists. "
                     "Please use the autocomplete function, or 'Add "
                     "file' if that is what you want to do.")

##Database management
#These functions handle basic database management taks.
def cleanup(btn):
    """Deletes all files in db without matches.

    btn is not used; it is built-in appJar functionality.
    """
    if not session:
        no_session_warning()
        return None
    cleanup_files(session)
    update_auto_entries()


def create_db(btn):
    """Creates new db file with filename provided by user in Entry
    'Database name:'. Notifies user if file already exists.

    btn is not used; it is built-in appJar functionality.
    """
    title=app.getEntry("Database name:")
    if not title.endswith(".db"):
        title = title+".db"
    if os.path.isfile('./'+title):
        app.clearEntry("Database name:")
        app.setLabel("db_res", "A file named "+title+
                       " already exists. Please pick another title.")
    else:
        make_new_db(title)
        app.clearEntry("Database name:")
        app.setLabel("db_res", "Database "+title+" created.")

def close():
    """Performs all final cleanup before program terminates."""
    global session
    if session:
        session.close()
    return True
    #Expected by appJar to ensure completion

###Subwindows
#These functions manage subwindows

def play_window():
    """Empties, populates and opens a popup showing details of files
    matching user query using Properties prefixed by 'Tags to filter'.
    Button "Show results" temporarily disabled while function is 
    executing.
    """
    if not session:
        no_session_warning()
        return None
    global FILE_DICT
    global DISPLAY_OPTION
    app.disableButton("Show results")
    FILE_DICT.clear()
    app.openScrollPane("play_results")
    app.emptyCurrentContainer()
    app.setStretch('both')
    app.setSticky('nesw')
    fileinfo = lookup_file()
    if fileinfo:
        i = 2
        if DISPLAY_OPTION == "Overview":
            app.addLabel("pwLength", "Length",0,0)
            app.addLabel("pwTitle", "Title", 0,1)
            app.addLabel("pwTags","Tags",0,2)
            app.addHorizontalSeparator(1,0,3)
        elif DISPLAY_OPTION == "Speed":
            app.addLabel("pwTitle", "Title")
        for row in fileinfo:
            title = row.title
            FILE_DICT[title] = row
            #Used by open_file to prevent future SQL query
            if DISPLAY_OPTION == "Overview":
                app.addLabel(title+"L", row.length,i,0)
                app.addLink(title,open_file,i,1)
                tag_res = row.contains
                msg_title = "All "+title+" tags"
                app.addEmptyMessage(msg_title,i,2)
                msg_list = []
                for tag in tag_res:
                    msg_list.append(tag.name)
                    msg_list.append("\n")
                msg_list.pop()
                msg_string = ''.join(msg_list)
                app.setMessage(msg_title, msg_string)
                #Styling
                if i%2 == 0:
                    app.setLabelBg(title+"L", "NavajoWhite")
                    app.setLinkBg(title, "NavajoWhite")
                    app.setMessageBg(msg_title, "NavajoWhite")
                app.setMessageAlign(msg_title, "left")
                app.setLabelAlign(title+"L","right")
                app.setLabelWidth(title+"L",10)
                app.setLinkWidth(title,70)
                app.setMessageWidth(msg_title,200)
            elif DISPLAY_OPTION == "Speed":
                app.addLink(title,inspect_file)
            app.setLinkAlign(title, "left")
                
            i += 1
        app.addLabel("play_window_res",
                     "Files found: "+str(len(fileinfo)),
                     column=0)
    else:
        app.addLabel("no_result", "No files found!")
        app.setLabelFg("no_result", "red")
    app.stopScrollPane()
    app.enableButton("Show results")
    app.showSubWindow("Play file")


def file_select_window(btn):
    """Opens a file selection window. Updates Entries 'Title' and 'Link'
    with file information.
    """
    path = app.openBox("File to enter")
    if path:
        title = path_leaf(path)
        if btn == "Choose file":
            app.setEntry("Title",title)
            app.setEntry("Link",path)
        elif btn == "Get link from file":
            app.setEntry("New link",path)
        else:
            raise Exception("Invalid argument to file_select_window: "
                            "Value of btn was: {}".format(btn))


def no_session_warning():
    """Opens a window informing the user of the need to select a db."""
    app.errorBox("Select a .db file!", "Please use the 'File' menu to "
                 "open a database file. If you do not have one, you "
                 "can make one from the same menu.")

##Menu functions
#These functions respond to input via the menubar

def new_db(btn):
    """Shows subwindow allowing creation of new database."""
    app.showSubWindow("Create database")


def show_help(btn):
    """Shows subwindow providing usage information."""
    app.showSubWindow("Help")


def change_db(btn):
    """Prompts user to open .db file, creates a session, and populates
    GUI, preparing it for use.
    """
    global session
    if session:
        session.close()
    db = app.openBox("Select database",
                     fileTypes=[('databases','*.db')])
    engine = create_engine("sqlite:///"+db)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    make_tag_tables()
    update_auto_entries()
    filename = path_leaf(db)
    app.setTitle("Tagger: "+filename)

    
def menu_press(btn):
    """Handles user changes to display settings. Invoked from menu."""
    if btn == "Git":
        startfile("https://github.com/Jonas-Wennerstrom/Tagger")
    else:
        if not session:
            no_session_warning()
            return None
        if btn == "propsize":
            val = app.getMenuRadioButton("Propsize", "propsize")
            global MAX_PROPSIZE
            MAX_PROPSIZE = int(val)
            make_tag_tables()
        elif btn == "option":
            val = app.getMenuRadioButton("Display","option")
            global DISPLAY_OPTION
            DISPLAY_OPTION = val
        else:
            raise Exception("Invalid argument to menu_press: "
                            "Value of btn was: {}".format(btn))

##Creation of subwindows
#Initialization of various popups.

#Creation of window to show and play files
app.startSubWindow("Play file")
app.setBg("Honeydew")
app.startScrollPane("play_results",0,0,colspan=3,
                    sticky='nsew',disabled='horizontal')
app.stopScrollPane()
app.setScrollPaneWidth("play_results",900)
app.setScrollPaneHeight("play_results",600)
app.stopSubWindow()

#Creation of window to inspect single file
app.startSubWindow("Inspect file")
app.setSize("900x100")
app.setBg("Honeydew")
app.setStretch("none")
app.stopSubWindow()

#Creation of window to create new .db file
app.startSubWindow("Create database")
app.setBg("Honeydew")
app.setSticky("nw")
app.setStretch("none")
app.addMessage("db_exp", "Write title of the new database (no file "
             "extension required).\nIt will be saved in the working "
             "directory.", 0, 0, 2, 0)
app.setMessageWidth("db_exp", 400)
app.addLabelEntry("Database name:",1,0)
app.addButton("Make DB", create_db,1,1)
app.addLabel("db_res", " ",2,0,2)
app.stopSubWindow()


#####START OF BOOT SEQUENCE

app.setTitle("Tagger")
app.setSize(WINDOW_SIZE)


#Menu creation and population
app.createMenu("File")
app.addMenuItem("File", "New db", new_db)
app.addMenuItem("File", "Open db...",change_db)
app.addMenuSeparator("File")
app.addMenuItem("File", "Clean up db", cleanup)
app.createMenu("Config")
app.addSubMenu("Config", "Propsize")
for i in range(1,6):
    app.addMenuRadioButton("Propsize", "propsize", str(5*i), menu_press)
app.addSubMenu("Config", "Display")
app.addMenuRadioButton("Display", "option", "Speed", menu_press)
app.addMenuRadioButton("Display", "option", "Overview", menu_press)
app.createMenu("About")
app.addMenuItem("About", "Help", show_help)
app.addMenuItem("About", "Git", menu_press)

#Setting default values to preset global values
app.setMenuRadioButton("Propsize", "propsize", "10")
app.setMenuRadioButton("Display", "option", "Overview")

#Start of main window contents
app.startTabbedFrame("tabbed_frame")

#Tab: Lookup files
app.startTab("Find file")
for i in range (MAX_PROPS):
    app.addProperties("Tags to filter" + str(i), {}, 0, i)
app.addButton("Show results", play_window,1,BUTTON_POS)
app.stopTab()

#Tab: Insert files
app.startTab("Add file")
app.addLabelNumericEntry("Length", 0,0)
app.addLabelEntry("Title",0,1)
app.addLabelEntry("Link",0,2)
app.addButton("Choose file",file_select_window,2,0)
for i in range (MAX_PROPS):
    app.addProperties("Tags to match" + str(i), {}, 1,i)
app.addButton("Add file",add_file,2,BUTTON_POS)
app.addLabel("add_file_res", "", 3,0,4)
app.stopTab()

#Tab: Insert tags
app.startTab("Add tags")
app.setStretch("none")
app.addLabel("tag_exp", "Write all tags you want to add separated by"
             "',': Comedy,Drama",0,0)
app.addEntry("new_tags",1,0)
app.addButton("Add tags", add_tag,2,0)
app.addLabel("add_tag_result"," ",3,0)
app.addLabel("add_tag_dupes", " ", 4,0,4)
app.setSticky("ne")
app.addVerticalSeparator(0,3,1,6,colour="red")
app.addEmptyMessage("existing_tags",0,4,1,6)
app.setMessageAnchor("existing_tags","nw")
app.stopTab()

#Tab: Update file
app.startTab("Update file")
app.addLabelEntry("New length", 0,0)
app.addLabelAutoEntry("Same title",[""],0,1)
app.addLabelEntry("New link",0,2)
app.setEntrySubmitFunction("Same title", pop_upd_tab)
app.addButton("Get link from file",file_select_window,2,0)
for i in range (MAX_PROPS):
    app.addProperties("New matched tags" + str(i), {}, 1,i)
app.addButton("Update file",update_file,2,BUTTON_POS)
app.addLabel("upd_file_res", "", 3,0,4)
app.stopTab()

#Tab: Delete file
app.startTab("Remove file")
app.setStretch("none")
app.addLabel("delfileExp","Deletes selected file and all matches. "
             "Warning! Cannot be undone!")
app.addLabelAutoEntry("Remove file",[""],1,0)
app.setEntryWidth("Remove file",40)
app.addButton("Delete file",del_file,1,1)
app.addLabel("del_file_res", "")
app.stopTab()

#Tab: Delete tag
app.startTab("Remove tag")
for i in range (MAX_PROPS):
    app.addProperties("Tags to delete" + str(i), {}, 0, i)
app.addButton("Delete tags",del_tag,1,BUTTON_POS)
app.stopTab()

app.stopTabbedFrame()



###Start of help window
app.startSubWindow("Help")
app.setBg("Honeydew")
app.setSticky("nw")
app.startTabbedFrame("help_tabs")
app.startTab("General info")
app.setSticky("nw")
app.addMessage("general_1", "Tagger is a tool to create, maintain, and "
               "use a tag-based database for various media. While it "
               "was originally designed to keep track of video media, "
               "it works just as well keeping track of anything you "
               "might want to keep track of through a tag-based "
               "approach."
               "\n\n"
               "What does that mean? Well, let's say you're a movie "
               "buff, with a big collection of all kinds of movies. "
               "Keeping track of them all could be tedious. Using tags "
               "to split them into overlapping categories and Tagger "
               "to keep track of it all, you could now find all your "
               "80's crime rom-coms in just a few clicks. If they're "
               "digitized you could even launch the file straight from "
               "Tagger,saving you the trouble of looking through your "
               "folders.")
app.stopTab()

app.startTab("Database info")
app.setSticky("nw")
app.addMessage("databases_1", "Tagger automates and controls all the "
               "technical details involved in creating, maintaining, "
               "and changing your databases. All it needs from you, "
               "the user, is the name of the files. You can create new "
               "ones or open one you've worked on before from the "
               "menu.")
app.stopTab()

app.startTab("Finding files")
app.setSticky("nw")
app.addMessage("finding_1", "Searching your database is very simple: "
               "Once you've opened a file from the menu, this tab will "
               "present you with all the tags you've made. Simply click "
               "the ones you want and press 'Show results', and you'll "
               "be presented with all the media you've stored which "
               "have all the tags you checked. From this new window "
               "you can click a title to open the link or look at all "
               "the tags associated with each title.")
app.stopTab()

app.startTab("Adding files")
app.setSticky("nw")
app.addMessage("adding_files_1", "Adding files is quick and easy: "
               "Enter the length (or skip it, you don't have to), "
               "title, and a link (or you can skip that as well), "
               "check all the tags which apply, and press 'Add file'. "
               "That's it! Your new piece of media is ready to be "
               "found.")

app.stopTab()

app.startTab("Adding tags")
app.setSticky("nw")
app.addMessage("adding_tags_1", "Adding new tags can be a bit finicky "
               "at first, but there really isn't much to it. Write all "
               "new tags you want to add in the box separated by a "
               "single comma and no space, e.g. 'Comedy,Spaghetti "
               "Western,Noir' and press 'Add tags'. If you add a stray "
               "space it's not a problem - it's just that the tag "
               "might not show up in alphabetical order.")

app.stopTab()

app.startTab("Updating files")
app.setSticky("nw")
app.addMessage("updating_files_1", "Updating a file is done in much "
               "the same way as adding a file, only now you are given "
               "a list of all titles already in the database to choose "
               "from. Other than that, simply write the length, link, "
               "and pick the tags as normal.")
app.stopTab()

app.startTab("Deleting files")
app.setSticky("nw")
app.addMessage("deleting_files_1", "In order to make deleting files as "
               "painless as possible, Tagger proved an autocomplete "
               "function in the title box with every title listed. You "
               "won't have to remember the exact spelling: As long as "
               "you've got the first few letters, you'll find what "
               "you're looking for.")

app.stopTab()

app.startTab("Deleting tags")
app.setSticky("nw")
app.addMessage("deleting_tags_warn", "Warning! Deleting tags can have "
               "unforseen consequences, such as media titles 'lost' "
               "due to no longer having any tags. It is highly "
               "recommended not to delete tags in use!")
app.addMessage("deleting_tags_1", "Deleting tags is just as easy as "
               "finding media: Simply click the ones you want gone and "
               "press 'Delete tags'.")
app.stopTab()

app.stopTabbedFrame()

app.stopSubWindow()
###End of help window



#Styling, main window
app.setBg("Honeydew")
app.setTabbedFrameTabExpand("tabbed_frame")
app.setTabbedFrameInactiveBg("tabbed_frame","AntiqueWhite")
tab_names = ["Find file", "Add file", "Add tags", "Remove file",
             "Remove tag"]
entries = app.getAllEntries()
for i in tab_names:
    app.setTabBg("tabbed_frame", i, "Honeydew")
for i in entries:
    app.setEntryBg(i,"Snow")

#Styling, help window
help_tab_names = ["General info", "Database info", "Finding files",
                  "Adding files", "Adding tags", "Updating files",
                  "Deleting files","Deleting tags"]
for i in help_tab_names:
    app.setTabBg("help_tabs", i, "Honeydew")
app.setMessageFg("deleting_tags_warn", "red")
app_messgs = ["general_1","databases_1","finding_1","adding_files_1",
              "adding_tags_1","updating_files_1","deleting_files_1",
              "deleting_tags_warn","deleting_tags_1"]

for m in app_messgs:
    app.setMessageWidth(m, 800)

#GUI launch
app.go()
