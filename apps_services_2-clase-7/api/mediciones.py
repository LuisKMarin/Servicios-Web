from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud import medicion as crud
from database import get_db
from schemas.medicion import (
    MedicionCreate,
    MedicionResponse,
    MedicionUpdate,
)


router = APIRouter(
    prefix="/mediciones",
    tags=["Mediciones"],
)


@router.get("", response_model=list[MedicionResponse])
def listar_mediciones(db: Session = Depends(get_db)):
    return crud.get_all(db)


@router.get("/{medicion_id}", response_model=MedicionResponse)
def obtener_medicion(
    medicion_id: int,
    db: Session = Depends(get_db),
):
    medicion = crud.get(db, medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=404,
            detail="La medición no existe",
        )

    return medicion


@router.post(
    "",
    response_model=MedicionResponse,
    status_code=status.HTTP_201_CREATED,
)
def agregar_medicion(
    data: MedicionCreate,
    db: Session = Depends(get_db),
):
    medicion = crud.create(db, data)

    if medicion is None:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe",
        )

    return medicion


@router.put(
    "/{medicion_id}",
    response_model=MedicionResponse,
)
def reemplazar_medicion(
    medicion_id: int,
    data: MedicionCreate,
    db: Session = Depends(get_db),
):
    medicion = crud.get(db, medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=404,
            detail="La medición no existe",
        )

    updated = crud.update(
        db,
        medicion,
        MedicionUpdate(**data.model_dump()),
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe",
        )

    return updated


@router.patch(
    "/{medicion_id}",
    response_model=MedicionResponse,
)
def actualizar_medicion(
    medicion_id: int,
    data: MedicionUpdate,
    db: Session = Depends(get_db),
):
    medicion = crud.get(db, medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=404,
            detail="La medición no existe",
        )

    updated = crud.update(db, medicion, data)

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe",
        )

    return updated


@router.delete(
    "/{medicion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_medicion(
    medicion_id: int,
    db: Session = Depends(get_db),
):
    medicion = crud.get(db, medicion_id)

    if medicion is None:
        raise HTTPException(
            status_code=404,
            detail="La medición no existe",
        )

    crud.delete(db, medicion)
