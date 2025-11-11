# app/schemas/employee.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class EmployeeCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    employee_code: str
    hire_date: Optional[date] = None
    designation: Optional[str] = None

class EmployeeOut(BaseModel):
    id: int
    full_name: str
    employee_code: str
    designation: Optional[str]

    class Config:
        orm_mode = True
