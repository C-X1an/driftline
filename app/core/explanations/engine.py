from sqlalchemy.orm import Session

from app.core.models import Explanation, RiskAssessment


def generate_explanation(
    db: Session,
    assessment: RiskAssessment | None,
    content: str,
    model: str,
    prompt_version: str,
    explanation_key: str,
    version: int,
    incident_id: str | None = None,
) -> Explanation:
    """
    Create a new explanation row.
    Idempotency and versioning are handled by caller + DB constraints.
    """

    explanation = Explanation(
        risk_assessment_id=assessment.id if assessment else None,
        content=content,
        model=model,
        prompt_version=prompt_version,
        explanation_key=explanation_key,
        version=version,
        incident_id=incident_id,
    )

    db.add(explanation)
    db.commit()
    db.refresh(explanation)

    return explanation
