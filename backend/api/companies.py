"""
기업 정보 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
import asyncpg
from datetime import datetime
from pydantic import BaseModel

from backend.core.database import get_db


router = APIRouter()


class CompanyCreate(BaseModel):
    """기업 생성 요청"""
    company_name: str
    business_number: Optional[str] = None
    company_type: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    region: Optional[str] = None
    establishment_date: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[int] = None
    certifications: Optional[dict] = None
    technology_fields: Optional[list] = None
    funding_needs: Optional[str] = None
    preferred_support_types: Optional[list] = None


class CompanyUpdate(BaseModel):
    """기업 정보 수정 요청"""
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    industry_code: Optional[str] = None
    industry_name: Optional[str] = None
    region: Optional[str] = None
    establishment_date: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[int] = None
    certifications: Optional[dict] = None
    technology_fields: Optional[list] = None
    funding_needs: Optional[str] = None
    preferred_support_types: Optional[list] = None


@router.post("/", response_model=dict)
async def create_company(
    company: CompanyCreate,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업 정보 등록

    새로운 기업 정보를 등록합니다.
    """

    # 사업자등록번호 중복 확인
    if company.business_number:
        existing = await conn.fetchval(
            "SELECT id FROM companies WHERE business_number = $1",
            company.business_number
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="이미 등록된 사업자등록번호입니다"
            )

    query = """
        INSERT INTO companies (
            company_name, business_number, company_type,
            industry_code, industry_name, region,
            establishment_date, employee_count, annual_revenue,
            certifications, technology_fields, funding_needs,
            preferred_support_types
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING id, company_name, business_number, created_at
    """

    row = await conn.fetchrow(
        query,
        company.company_name,
        company.business_number,
        company.company_type,
        company.industry_code,
        company.industry_name,
        company.region,
        company.establishment_date,
        company.employee_count,
        company.annual_revenue,
        company.certifications,
        company.technology_fields,
        company.funding_needs,
        company.preferred_support_types
    )

    result = dict(row)
    if result.get('created_at'):
        result['created_at'] = result['created_at'].isoformat()

    return {
        "message": "기업 정보가 성공적으로 등록되었습니다",
        "company": result
    }


@router.get("/{company_id}", response_model=dict)
async def get_company(
    company_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업 정보 조회

    특정 기업의 상세 정보를 조회합니다.
    """

    query = """
        SELECT *
        FROM companies
        WHERE id = $1
    """

    row = await conn.fetchrow(query, company_id)

    if not row:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    company = dict(row)

    # datetime을 문자열로 변환
    for key, value in company.items():
        if isinstance(value, datetime):
            company[key] = value.isoformat()

    return company


@router.put("/{company_id}", response_model=dict)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업 정보 수정

    기업 정보를 업데이트합니다.
    """

    # 기존 기업 존재 확인
    existing = await conn.fetchrow(
        "SELECT id FROM companies WHERE id = $1",
        company_id
    )

    if not existing:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    # 업데이트할 필드 구성
    update_fields = []
    values = []
    param_count = 1

    for field, value in company_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1

    if not update_fields:
        raise HTTPException(status_code=400, detail="수정할 내용이 없습니다")

    # updated_at 추가
    update_fields.append(f"updated_at = ${param_count}")
    values.append(datetime.now())
    param_count += 1

    # 쿼리 실행
    query = f"""
        UPDATE companies
        SET {', '.join(update_fields)}
        WHERE id = ${param_count}
        RETURNING id, company_name, updated_at
    """
    values.append(company_id)

    row = await conn.fetchrow(query, *values)

    result = dict(row)
    if result.get('updated_at'):
        result['updated_at'] = result['updated_at'].isoformat()

    return {
        "message": "기업 정보가 성공적으로 수정되었습니다",
        "company": result
    }


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업 정보 삭제

    기업 정보를 삭제합니다.
    """

    result = await conn.execute(
        "DELETE FROM companies WHERE id = $1",
        company_id
    )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    return {
        "message": "기업 정보가 성공적으로 삭제되었습니다",
        "company_id": company_id
    }


@router.get("/{company_id}/recommendations")
async def get_company_recommendations(
    company_id: int,
    limit: int = 20,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    기업 맞춤 추천 공고

    기업 정보를 기반으로 적합한 정부지원사업을 추천합니다.
    """

    # 기업 정보 조회
    company_query = """
        SELECT *
        FROM companies
        WHERE id = $1
    """
    company = await conn.fetchrow(company_query, company_id)

    if not company:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    # 매칭 점수와 함께 공고 조회
    query = """
        SELECT
            p.*,
            COALESCE(m.match_score, 0) as match_score,
            m.match_reasons
        FROM gov_support_projects p
        LEFT JOIN matching_history m
            ON p.id = m.project_id AND m.company_id = $1
        WHERE p.status = 'active'
        ORDER BY m.match_score DESC NULLS LAST, p.application_end_date ASC
        LIMIT $2
    """

    rows = await conn.fetch(query, company_id, limit)

    recommendations = []
    for row in rows:
        project = dict(row)
        # datetime을 문자열로 변환
        for key, value in project.items():
            if isinstance(value, datetime):
                project[key] = value.isoformat()
        recommendations.append(project)

    return {
        "company_id": company_id,
        "company_name": company['company_name'],
        "total": len(recommendations),
        "recommendations": recommendations
    }
