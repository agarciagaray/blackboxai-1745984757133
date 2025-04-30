from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime

class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_type: str
    document_number: str
    first_name: str
    last_name: str
    birth_date: date
    phone: Optional[str] = None
    email: Optional[str] = None

    credit_info: Optional["CreditInfo"] = Relationship(back_populates="customer")
    socioeconomic_info: Optional["SocioeconomicInfo"] = Relationship(back_populates="customer")
    credit_requests: List["CreditRequest"] = Relationship(back_populates="customer")

class CreditInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    experian_score: Optional[float] = None
    transunion_score: Optional[float] = None
    active_obligations: Optional[int] = None
    total_debt: Optional[float] = None
    payment_history: Optional[str] = None  # Could be JSON string or separate table
    recent_inquiries: Optional[int] = None  # Number of inquiries in last 60 days

    customer: Customer = Relationship(back_populates="credit_info")

class SocioeconomicInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    monthly_income: Optional[float] = None
    occupation: Optional[str] = None
    economic_sector: Optional[str] = None
    employment_duration_years: Optional[int] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    dependents: Optional[int] = None
    housing_type: Optional[str] = None

    customer: Customer = Relationship(back_populates="socioeconomic_info")

class CreditRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    amount_requested: float
    term_months: int
    interest_rate: float
    credit_purpose: Optional[str] = None
    collateral: Optional[str] = None
    request_date: datetime = Field(default_factory=datetime.utcnow)

    customer: Customer = Relationship(back_populates="credit_requests")
    evaluation: Optional["CreditEvaluation"] = Relationship(back_populates="credit_request")

class CreditEvaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    credit_request_id: int = Field(foreign_key="creditrequest.id")
    decision: str  # APPROVED, APPROVED_WITH_ADJUSTMENT, REJECTED
    score: float
    population_percentile: Optional[float] = None
    decision_factors: Optional[str] = None  # JSON string or text explanation
    max_recommended_amount: Optional[float] = None
    recommended_term_months: Optional[int] = None
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    model_version: str

    credit_request: CreditRequest = Relationship(back_populates="evaluation")
