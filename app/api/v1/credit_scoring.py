from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select
from app.schemas import CreditScoringRequest, CreditScoringResponse
from app.db import get_session
from app.models import Customer, CreditInfo, SocioeconomicInfo, CreditRequest, CreditEvaluation
from datetime import datetime
from typing import Optional

router = APIRouter()

MODEL_VERSION = "1.0.0"

def calculate_score(credit_info: Optional[CreditInfo], socioeconomic_info: Optional[SocioeconomicInfo]) -> float:
    # Simplified scoring logic based on weights from the task description
    score = 0.0
    if credit_info:
        # Weights: payment history 35%, debt 30%, history length 15%, mix 10%, new credits 10%
        # Since we don't have all data, simulate with available fields
        if credit_info.experian_score:
            score += credit_info.experian_score * 0.35
        if credit_info.total_debt:
            # Lower debt better, invert scale (assuming max debt 1000000 for scaling)
            debt_score = max(0, 1000000 - credit_info.total_debt) / 1000000 * 30
            score += debt_score
        if credit_info.active_obligations:
            obligations_score = max(0, 10 - credit_info.active_obligations) / 10 * 15
            score += obligations_score
        if credit_info.recent_inquiries:
            inquiries_score = max(0, 10 - credit_info.recent_inquiries) / 10 * 10
            score += inquiries_score
    if socioeconomic_info:
        # Add socioeconomic factors (simplified)
        if socioeconomic_info.monthly_income:
            income_score = min(socioeconomic_info.monthly_income / 1000000, 1) * 10
            score += income_score
    return round(score, 2)

def determine_decision(score: float, amount_requested: float) -> str:
    # Simplified thresholds
    if score >= 70:
        return "APROBADO"
    elif 50 <= score < 70:
        return "APROBADO_CON_AJUSTE"
    else:
        return "RECHAZADO"

@router.post("/evaluation", response_model=CreditScoringResponse, status_code=status.HTTP_201_CREATED)
def evaluate_credit_scoring(
    request: CreditScoringRequest,
    session: Session = Depends(get_session)
):
    try:
        # Check if customer exists, else create
        customer = session.exec(
            select(Customer).where(
                (Customer.document_type == request.customer.document_type) &
                (Customer.document_number == request.customer.document_number)
            )
        ).first()
        if not customer:
            customer = Customer(
                document_type=request.customer.document_type,
                document_number=request.customer.document_number,
                first_name=request.customer.first_name,
                last_name=request.customer.last_name,
                birth_date=request.customer.birth_date,
                phone=request.customer.phone,
                email=request.customer.email
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)

        # Create or update credit info
        credit_info = None
        if request.credit_info:
            credit_info = session.exec(
                select(CreditInfo).where(CreditInfo.customer_id == customer.id)
            ).first()
            if not credit_info:
                credit_info = CreditInfo(
                    customer_id=customer.id,
                    experian_score=request.credit_info.experian_score,
                    transunion_score=request.credit_info.transunion_score,
                    active_obligations=request.credit_info.active_obligations,
                    total_debt=request.credit_info.total_debt,
                    payment_history=request.credit_info.payment_history,
                    recent_inquiries=request.credit_info.recent_inquiries
                )
                session.add(credit_info)
            else:
                credit_info.experian_score = request.credit_info.experian_score
                credit_info.transunion_score = request.credit_info.transunion_score
                credit_info.active_obligations = request.credit_info.active_obligations
                credit_info.total_debt = request.credit_info.total_debt
                credit_info.payment_history = request.credit_info.payment_history
                credit_info.recent_inquiries = request.credit_info.recent_inquiries
            session.commit()
            session.refresh(credit_info)

        # Create or update socioeconomic info
        socioeconomic_info = None
        if request.socioeconomic_info:
            socioeconomic_info = session.exec(
                select(SocioeconomicInfo).where(SocioeconomicInfo.customer_id == customer.id)
            ).first()
            if not socioeconomic_info:
                socioeconomic_info = SocioeconomicInfo(
                    customer_id=customer.id,
                    monthly_income=request.socioeconomic_info.monthly_income,
                    occupation=request.socioeconomic_info.occupation,
                    economic_sector=request.socioeconomic_info.economic_sector,
                    employment_duration_years=request.socioeconomic_info.employment_duration_years,
                    education_level=request.socioeconomic_info.education_level,
                    marital_status=request.socioeconomic_info.marital_status,
                    dependents=request.socioeconomic_info.dependents,
                    housing_type=request.socioeconomic_info.housing_type
                )
                session.add(socioeconomic_info)
            else:
                socioeconomic_info.monthly_income = request.socioeconomic_info.monthly_income
                socioeconomic_info.occupation = request.socioeconomic_info.occupation
                socioeconomic_info.economic_sector = request.socioeconomic_info.economic_sector
                socioeconomic_info.employment_duration_years = request.socioeconomic_info.employment_duration_years
                socioeconomic_info.education_level = request.socioeconomic_info.education_level
                socioeconomic_info.marital_status = request.socioeconomic_info.marital_status
                socioeconomic_info.dependents = request.socioeconomic_info.dependents
                socioeconomic_info.housing_type = request.socioeconomic_info.housing_type
            session.commit()
            session.refresh(socioeconomic_info)

        # Create credit request
        credit_request = CreditRequest(
            customer_id=customer.id,
            amount_requested=request.credit_request.amount_requested,
            term_months=request.credit_request.term_months,
            interest_rate=request.credit_request.interest_rate,
            credit_purpose=request.credit_request.credit_purpose,
            collateral=request.credit_request.collateral,
            request_date=datetime.utcnow()
        )
        session.add(credit_request)
        session.commit()
        session.refresh(credit_request)

        # Calculate score
        score = calculate_score(credit_info, socioeconomic_info)

        # Determine decision
        decision = determine_decision(score, credit_request.amount_requested)

        # Create evaluation record
        evaluation = CreditEvaluation(
            credit_request_id=credit_request.id,
            decision=decision,
            score=score,
            population_percentile=round(score, 2),  # Simplified
            decision_factors="Simulated factors based on input data",
            max_recommended_amount=credit_request.amount_requested if decision != "RECHAZADO" else 0,
            recommended_term_months=credit_request.term_months if decision != "RECHAZADO" else 0,
            evaluation_date=datetime.utcnow(),
            model_version=MODEL_VERSION
        )
        session.add(evaluation)
        session.commit()
        session.refresh(evaluation)

        response = CreditScoringResponse(
            decision=evaluation.decision,
            score=evaluation.score,
            population_percentile=evaluation.population_percentile,
            decision_factors=evaluation.decision_factors,
            max_recommended_amount=evaluation.max_recommended_amount,
            recommended_term_months=evaluation.recommended_term_months,
            evaluation_id=evaluation.id,
            evaluation_date=evaluation.evaluation_date,
            model_version=evaluation.model_version
        )
        return response

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
