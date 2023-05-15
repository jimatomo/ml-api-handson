from pydantic import BaseModel
from typing import List

# request
class Text(BaseModel):
    PassengerId: int
    Pclass: int
    Name: str
    Sex: str
    Age: float
    SibSp: int
    Parch: int
    Ticket: int
    Fare: float
    Cabin: str
    Embarked: str

class Data(BaseModel):
    data: List[Text]

# response
class Output(BaseModel):
    PassengerId: int
    Pclass: int
    Sex: int
    Age: float
    SibSp: int
    Parch: int
    Fare: float
    Embarked: int
    FamilySize: int
    Prediction: float

class Pred(BaseModel):
    prediction: List[Output]
