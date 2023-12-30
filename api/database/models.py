from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

directory_path = "data/database"
if not os.path.exists(directory_path):
    os.makedirs(directory_path)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine(f"sqlite:///{directory_path}/mission_database.db")

Base = declarative_base()


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True)
    mission_title = Column(String)
    involved_pups = Column(String)  # Store as a comma-separated string
    main_location = Column(String)
    mission_script = Column(Text)
    translation = Column(Text)
    is_requested = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"<Mission(title='{self.mission_title}', location='{self.main_location}')>"
        )


# Create all tables in the engine
Base.metadata.create_all(engine)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
