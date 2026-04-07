from sqlalchemy import Column, String, Text
from app.db import Base


class IncidentRecord(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(String, nullable=False)
    status = Column(String, nullable=False)
    approval_state = Column(String, nullable=False)

    event_json = Column(Text, nullable=False)
    decision_json = Column(Text, nullable=False)
    response_json = Column(Text, nullable=False)

    review_result = Column(String, nullable=True)
    approved_action = Column(String, nullable=True)
