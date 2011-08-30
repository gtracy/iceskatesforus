from google.appengine.ext import db

   
class User(db.Model):
    user              = db.UserProperty()
    userID            = db.StringProperty()
    email             = db.StringProperty()
    preferredEmail    = db.StringProperty()
    nickname          = db.StringProperty()
    profilePhoto      = db.BlobProperty()
    status            = db.StringProperty()
    first             = db.StringProperty()
    last              = db.StringProperty()
    createDate        = db.DateTimeProperty(auto_now_add=True)
    karma             = db.IntegerProperty()
    fbProfile_url     = db.StringProperty()
    access_token      = db.StringProperty()

class Skate(db.Model):
    owner      = db.ReferenceProperty(User,collection_name="skate_owner")
    requester  = db.ReferenceProperty(User,collection_name="skate_borrower")
    size       = db.FloatProperty()
    color      = db.StringProperty()
    price      = db.IntegerProperty()
    picture    = db.BlobProperty()
    style      = db.StringProperty()
    dateAdded  = db.DateTimeProperty(auto_now_add=True)
    swapped    = db.BooleanProperty()
    status     = db.IntegerProperty()
    note       = db.StringProperty(multiline=True)
    hide       = db.BooleanProperty()
    
class Comment(db.Model):
    text          = db.StringProperty(multiline=True)
    userID        = db.StringProperty()
    commentAuthor = db.ReferenceProperty(User,collection_name="comment_commentauthor_set")
    pageOwner     = db.ReferenceProperty(User,collection_name="comment_pageowner_set")
    dateAdded     = db.DateTimeProperty(auto_now_add=True)
    
class UserEvent(db.Model):
    eventType = db.IntegerProperty()
    user      = db.ReferenceProperty(User,collection_name="event_user_set")
    skate     = db.ReferenceProperty(Skate,collection_name="event_skate_set")
    dateAdded = db.DateTimeProperty(auto_now_add=True)
    metaOne   = db.StringProperty(multiline=True)
    metaTwo   = db.StringProperty(multiline=True)
    