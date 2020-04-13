from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://localhost/ashok')
db = engine.connect()

base = declarative_base()

class Userinfo(base):
    __tablename__ = "userinfo"

    username = Column(String)
    gameid = Column(Integer)
    userrating = Column(Float)
    own = Column(Integer)
    pre = Column(Integer)
    prevowned = Column(Integer)
    fortrade = Column(Integer)
    want = Column(Integer)
    wanttoplay = Column(Integer)
    wanttobuy = Column(Integer)
    wishlistc = Column(Integer)
    wishlistpriority = Column(Integer)
    preordered = Column(Integer)
    numplays = Column(Integer)
    lastmodified = Column(String)

Session = sessionmaker(db)  
session = Session()

base.metadata.create_all(db)

# Create 
doctor_strange = Film(
    title="Doctor Strange", 
    director="Scott Derrickson", 
    year="2016"
)  
session.add(doctor_strange)  
session.commit()

# Read
films = session.query(Film)  
for film in films:  
    print(film.title)

# Update
doctor_strange.title = "Some2016Film"  
session.commit()

# Delete
session.delete(doctor_strange)  
session.commit()  


userinfofile = "../../data/userinfo.csv"

with open(userinfofile, "r") as f:
    for i, line in enumerate(f):
        
        if i == 5:
            break
