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

    # NEW POLICY / EXPLANATION FIELDS
    policy_name = Column(String, nullable=True)
    policy_version = Column(String, nullable=True)
    decision_reasons = Column(Text, nullable=True)
    matched_rules = Column(Text, nullable=True)
    safety_blocks = Column(Text, nullable=True)
    response_profile = Column(Text, nullable=True)
