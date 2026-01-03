from sqlalchemy.orm import Session

from app.core.models import RiskAssessment, Explanation
from app.llm.prompts import PROMPT_V1


def generate_explanation(
    db: Session,
    assessment: RiskAssessment,
    llm_client,
):
    # Check cache (IMPORTANT)
    existing = (
        db.query(Explanation)
        .filter(Explanation.risk_assessment_id == assessment.id)
        .first()
    )
    if existing:
        return existing

    prompt = PROMPT_V1.format(
        risk_level=assessment.risk_level,
        magnitude=assessment.magnitude,
        components=assessment.drift_signal.components,
    )

    content = llm_client.generate(prompt)

    explanation = Explanation(
        risk_assessment_id=assessment.id,
        content=content,
        model=llm_client.model_name,
        prompt_version="v1",
    )

    db.add(explanation)
    db.commit()
    db.refresh(explanation)

    return explanation
