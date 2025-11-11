# app/api/employees.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut
import traceback

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=EmployeeOut)
async def create_employee(payload: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    try:
        employee = Employee(
            full_name=payload.full_name,
            phone=payload.phone,
            employee_code=payload.employee_code,
            hire_date=payload.hire_date,
            designation=payload.designation,
            is_active=True,
        )
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        return employee
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
