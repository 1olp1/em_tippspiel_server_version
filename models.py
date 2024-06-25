from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    hash = Column(String(255), nullable=False)
    total_points = Column(Integer, default=0)
    correct_result = Column(Integer, default=0)
    correct_goal_diff = Column(Integer, default=0)
    correct_tendency = Column(Integer, default=0)
    predictions = relationship("Prediction", back_populates="user")

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    matchday = Column(Integer)
    team1_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team2_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    team1_score = Column(Integer)
    team2_score = Column(Integer)
    matchDateTime = Column(DateTime)
    matchIsFinished = Column(Integer)
    location = Column(String(255))
    lastUpdateDateTime = Column(DateTime)
    predictions_evaluated = Column(Integer, default=0)
    evaluation_Date = Column(DateTime)

    # Define explicit relationship names
    team1 = relationship("Team", foreign_keys=[team1_id], backref="matches_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], backref="matches_as_team2")

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    teamName = Column(String(255))
    shortName = Column(String(255))
    teamIconUrl = Column(String(255))
    teamIconPath = Column(String(255))
    teamGroupName = Column(String, default='None')
    points = Column(Integer, default=0)
    opponentGoals = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    matches = Column(Integer, default=0)
    won = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    draw = Column(Integer, default=0)
    goalDiff = Column(Integer, default=0)
    teamRank = Column(Integer)
    lastUpdateTime = Column(DateTime)

class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    matchday = Column(Integer, nullable=False)
    match_id = Column(Integer, nullable=False)
    team1_score = Column(Integer, nullable=False)
    team2_score = Column(Integer, nullable=False)
    goal_diff = Column(Integer, nullable=False)
    winner = Column(Integer, nullable=False)
    prediction_date = Column(DateTime)
    points = Column(Integer, default=0)
    user = relationship("User", back_populates="predictions")
