app.startSubWindow("Help")
app.startTabbedFrame("Help tabs")
app.startTab("General info")
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
app.addMessage("databases_1", "Tagger automates and controls all the "
               "technical details involved in creating, maintaining, "
               "and changing your databases. All it needs from you, "
               "the user, is the name of the files. You can create new "
               "ones or open one you've worked on before from the "
               "menu.")

app.startTab("Finding files")
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
app.addMessage("adding__files_1", "Adding files is quick and easy: "
               "Enter the length (or skip it, you don't have to), "
               "title, and a link (or you can skip that as well), "
               "check all the tags which apply, and press 'Add file'. "
               "That's it! Your new piece of media is ready to be "
               "found.")

app.stopTab()

app.startTab("Adding tags")
app.addMessage("adding_tags_1", "Adding new tags can be a bit finicky "
               "at first, but there really isn't much to it. Write all "
               "new tags you want to add in the box separated by a "
               "single comma and no space, e.g. 'Comedy,Spaghetti "
               "Western,Noir' and press 'Add tags'. If you add a stray "
               "space it's not a problem - it's just that the tag "
               "might not show up in alphabetical order.")

app.stopTab()

app.startTab("Deleting files")
app.addMessage("deleting_files_1", "In order to make deleting files as "
               "painless as possible, Tagger proved an autocomplete "
               "function in the title box with every title listed. You "
               "won't have to remember the exact spelling: As long as "
               "you've got the first few letters, you'll find what "
               "you're looking for.")

app.stopTab()

app.startTab("Deleting tags")
app.addMessage("deleting_tags_warn", "Warning! Deleting tags can have "
               "unforseen consequences, such as media titles 'lost' "
               "due to no longer having any tags. It is highly "
               "recommended not to delete tags in use!")
app.addMessage("deleting_tags_1", "Deleting tags is just as easy as "
               "finding media: Simply click the ones you want gone and "
               "press 'Delete tags'.")
app.stopTab()

app.stopTabbedFrame()

app.setMessageFg("deleting_tags_warn", "red")
