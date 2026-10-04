from sqlalchemy import select
from sqlalchemy.orm import Session

from models.estudiante import Estudiante
from models.medicion import Medicion
from schemas.medicion import MedicionCreate, MedicionUpdate


def get_all(db: Session) -> list[Medicion]:
    return list(
        db.scalars(
            select(Medicion).order_by(Medicion.id)
        ).all()
    )


def get(db: Session, medicion_id: int) -> Medicion | None:
    return db.get(Medicion, medicion_id)


def create(db: Session, data: MedicionCreate) -> Medicion | None:
    estudiante = db.get(Estudiante, data.estudiante_id)

    if estudiante is None:
        return None

    medicion = Medicion(**data.model_dump())
    db.add(medicion)
    db.commit()
    db.refresh(medicion)

    return medicion


def update(
    db: Session,
    medicion: Medicion,
    data: MedicionUpdate,
) -> Medicion | None:
    values = data.model_dump(exclude_unset=True)

    if "estudiante_id" in values:
        estudiante = db.get(Estudiante, values["estudiante_id"])

        if estudiante is None:
            return None

    for field, value in values.items():
        setattr(medicion, field, value)

    db.commit()
    db.refresh(medicion)

    return medicion


def delete(db: Session, medicion: Medicion) -> None:
    db.delete(medicion)
    db.commit()
