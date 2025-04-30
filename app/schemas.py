from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class CustomerBase(BaseModel):
    document_type: str
    document_number: str
    first_name: str
    last_name: str
    birth_date: date
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerRead(CustomerBase):
    id: int

    class Config:
        orm_mode = True

class CreditInfoBase(BaseModel):
    experian_score: Optional[float] = None
    transunion_score: Optional[float] = None
    active_obligations: Optional[int] = None
    total_debt: Optional[float] = None
    payment_history: Optional[str] = None
    recent_inquiries: Optional[int] = None

class CreditInfoCreate(CreditInfoBase):
    pass

class CreditInfoRead(CreditInfoBase):
    id: int
    customer_id: int

    class Config:
        orm_mode = True

class SocioeconomicInfoBase(BaseModel):
    monthly_income: Optional[float] = None
    occupation: Optional[str] = None
    economic_sector: Optional[str] = None
    employment_duration_years: Optional[int] = None
    education_level: Optional[str] = None
    marital_status: Optional[str] = None
    dependents: Optional[int] = None
    housing_type: Optional[str] = None

class SocioeconomicInfoCreate(SocioeconomicInfoBase):
    pass

class SocioeconomicInfoRead(SocioeconomicInfoBase):
    id: int
    customer_id: int

    class Config:
        orm_mode = True

class CreditRequestBase(BaseModel):
    amount_requested: float
    term_months: int
    interest_rate: float
    credit_purpose: Optional[str] = None
    collateral: Optional[str] = None

class CreditRequestCreate(CreditRequestBase):
    customer: CustomerCreate
    credit_info: Optional[CreditInfoCreate] = None
    socioeconomic_info: Optional[SocioeconomicInfoCreate] = None

class CreditRequestRead(CreditRequestBase):
    id: int
    customer: CustomerRead
    credit_info: Optional[CreditInfoRead] = None
    socioeconomic_info: Optional[SocioeconomicInfoRead] = None
    request_date: datetime

    class Config:
        orm_mode = True

class CreditEvaluationBase(BaseModel):
    decision: str
    score: float
    population_percentile: Optional[float] = None
    decision_factors: Optional[str] = None
    max_recommended_amount: Optional[float] = None
    recommended_term_months: Optional[int] = None
    model_version: str

class CreditEvaluationCreate(CreditEvaluationBase):
    pass

class CreditEvaluationRead(CreditEvaluationBase):
    id: int
    evaluation_date: datetime

    class Config:
        orm_mode = True

class CreditScoringRequest(BaseModel):
    customer: CustomerCreate
    credit_request: CreditRequestBase
    credit_info: Optional[CreditInfoCreate] = None
    socioeconomic_info: Optional[SocioeconomicInfoCreate] = None
    evaluation_params: Optional[dict] = None  # For optional thresholds or custom params

class CreditScoringResponse(BaseModel):
    decision: str
    score: float
    population_percentile: Optional[float] = None
    decision_factors: Optional[str] = None
    max_recommended_amount: Optional[float] = None
    recommended_term_months: Optional[int] = None
    evaluation_id: int
    evaluation_date: datetime
    model_version: str
