"""
사업계획서 생성 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict
import asyncpg
from datetime import datetime
from pydantic import BaseModel

from backend.core.database import get_db
from backend.services.ai.proposal_generator import ProposalGenerator


router = APIRouter()


class ProposalGenerateRequest(BaseModel):
    """사업계획서 생성 요청"""
    company_id: int
    project_id: str
    additional_info: Optional[Dict] = None
    sections: Optional[List[str]] = None  # 생성할 섹션 지정 (없으면 전체)


class ProposalUpdateRequest(BaseModel):
    """사업계획서 수정 요청"""
    title: Optional[str] = None
    content: Optional[str] = None
    sections: Optional[Dict] = None
    status: Optional[str] = None


@router.post("/generate", response_model=dict)
async def generate_proposal(
    request: ProposalGenerateRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    사업계획서 자동 생성

    기업 정보와 지원사업 정보를 바탕으로 AI가 사업계획서를 자동으로 생성합니다.
    """

    # 기업 정보 조회
    company_query = """
        SELECT *
        FROM companies
        WHERE id = $1
    """
    company = await conn.fetchrow(company_query, request.company_id)

    if not company:
        raise HTTPException(status_code=404, detail="기업 정보를 찾을 수 없습니다")

    # 지원사업 정보 조회
    project_query = """
        SELECT *
        FROM gov_support_projects
        WHERE id = $1
    """
    project = await conn.fetchrow(project_query, request.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="지원사업 정보를 찾을 수 없습니다")

    # 사업계획서 생성
    try:
        generator = ProposalGenerator()

        company_info = dict(company)
        project_info = dict(project)

        # 전체 생성 또는 특정 섹션만 생성
        if request.sections:
            # 특정 섹션만 생성
            sections = {}
            for section_name in request.sections:
                content = generator.generate_section(
                    section_name=section_name,
                    company_info=company_info,
                    project_info=project_info,
                    additional_info=request.additional_info
                )
                sections[section_name] = content
        else:
            # 전체 생성
            sections = generator.generate_proposal(
                company_info=company_info,
                project_info=project_info,
                additional_info=request.additional_info
            )

        # 데이터베이스에 저장
        insert_query = """
            INSERT INTO proposals (
                company_id, project_id, title, sections, status
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id, title, created_at
        """

        title = f"{company['company_name']} - {project['project_name']} 사업계획서"

        row = await conn.fetchrow(
            insert_query,
            request.company_id,
            request.project_id,
            title,
            sections,
            'draft'
        )

        result = dict(row)
        if result.get('created_at'):
            result['created_at'] = result['created_at'].isoformat()

        return {
            "message": "사업계획서가 성공적으로 생성되었습니다",
            "proposal": result,
            "sections": sections
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"사업계획서 생성 실패: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류: {str(e)}"
        )


@router.get("/{proposal_id}", response_model=dict)
async def get_proposal(
    proposal_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    사업계획서 조회

    특정 사업계획서의 상세 내용을 조회합니다.
    """

    query = """
        SELECT
            p.*,
            c.company_name,
            pr.project_name
        FROM proposals p
        JOIN companies c ON p.company_id = c.id
        JOIN gov_support_projects pr ON p.project_id = pr.id
        WHERE p.id = $1
    """

    row = await conn.fetchrow(query, proposal_id)

    if not row:
        raise HTTPException(status_code=404, detail="사업계획서를 찾을 수 없습니다")

    proposal = dict(row)

    # datetime을 문자열로 변환
    for key, value in proposal.items():
        if isinstance(value, datetime):
            proposal[key] = value.isoformat()

    return proposal


@router.get("/", response_model=List[dict])
async def get_proposals(
    company_id: Optional[int] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    사업계획서 목록 조회

    필터링 조건에 따라 사업계획서 목록을 조회합니다.
    """

    conditions = []
    params = []
    param_count = 0

    if company_id:
        param_count += 1
        conditions.append(f"p.company_id = ${param_count}")
        params.append(company_id)

    if project_id:
        param_count += 1
        conditions.append(f"p.project_id = ${param_count}")
        params.append(project_id)

    if status:
        param_count += 1
        conditions.append(f"p.status = ${param_count}")
        params.append(status)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            p.id, p.title, p.status, p.created_at, p.updated_at,
            c.company_name,
            pr.project_name
        FROM proposals p
        JOIN companies c ON p.company_id = c.id
        JOIN gov_support_projects pr ON p.project_id = pr.id
        {where_clause}
        ORDER BY p.created_at DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])

    rows = await conn.fetch(query, *params)

    proposals = []
    for row in rows:
        proposal = dict(row)
        # datetime을 문자열로 변환
        for key, value in proposal.items():
            if isinstance(value, datetime):
                proposal[key] = value.isoformat()
        proposals.append(proposal)

    return proposals


@router.put("/{proposal_id}", response_model=dict)
async def update_proposal(
    proposal_id: int,
    update_request: ProposalUpdateRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    사업계획서 수정

    생성된 사업계획서의 내용을 수정합니다.
    """

    # 기존 사업계획서 존재 확인
    existing = await conn.fetchrow(
        "SELECT id FROM proposals WHERE id = $1",
        proposal_id
    )

    if not existing:
        raise HTTPException(status_code=404, detail="사업계획서를 찾을 수 없습니다")

    # 업데이트할 필드 구성
    update_fields = []
    values = []
    param_count = 1

    for field, value in update_request.dict(exclude_unset=True).items():
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
        UPDATE proposals
        SET {', '.join(update_fields)}
        WHERE id = ${param_count}
        RETURNING id, title, status, updated_at
    """
    values.append(proposal_id)

    row = await conn.fetchrow(query, *values)

    result = dict(row)
    if result.get('updated_at'):
        result['updated_at'] = result['updated_at'].isoformat()

    return {
        "message": "사업계획서가 성공적으로 수정되었습니다",
        "proposal": result
    }


@router.delete("/{proposal_id}")
async def delete_proposal(
    proposal_id: int,
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    사업계획서 삭제

    사업계획서를 삭제합니다.
    """

    result = await conn.execute(
        "DELETE FROM proposals WHERE id = $1",
        proposal_id
    )

    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="사업계획서를 찾을 수 없습니다")

    return {
        "message": "사업계획서가 성공적으로 삭제되었습니다",
        "proposal_id": proposal_id
    }


@router.post("/{proposal_id}/regenerate-section")
async def regenerate_section(
    proposal_id: int,
    section_name: str = Body(..., embed=True),
    additional_info: Optional[Dict] = Body(None, embed=True),
    conn: asyncpg.Connection = Depends(get_db)
):
    """
    특정 섹션 재생성

    사업계획서의 특정 섹션만 다시 생성합니다.
    """

    # 사업계획서 조회
    proposal_query = """
        SELECT p.*, c.*, pr.*
        FROM proposals p
        JOIN companies c ON p.company_id = c.id
        JOIN gov_support_projects pr ON p.project_id = pr.id
        WHERE p.id = $1
    """

    proposal = await conn.fetchrow(proposal_query, proposal_id)

    if not proposal:
        raise HTTPException(status_code=404, detail="사업계획서를 찾을 수 없습니다")

    try:
        generator = ProposalGenerator()

        # 섹션 재생성
        new_content = generator.generate_section(
            section_name=section_name,
            company_info=dict(proposal),
            project_info=dict(proposal),
            additional_info=additional_info
        )

        # 기존 섹션 업데이트
        current_sections = proposal['sections'] or {}
        current_sections[section_name] = new_content

        # 데이터베이스 업데이트
        update_query = """
            UPDATE proposals
            SET sections = $1, updated_at = $2
            WHERE id = $3
            RETURNING id, title, updated_at
        """

        row = await conn.fetchrow(
            update_query,
            current_sections,
            datetime.now(),
            proposal_id
        )

        result = dict(row)
        if result.get('updated_at'):
            result['updated_at'] = result['updated_at'].isoformat()

        return {
            "message": f"'{section_name}' 섹션이 성공적으로 재생성되었습니다",
            "proposal": result,
            "section": {
                "name": section_name,
                "content": new_content
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"섹션 재생성 중 오류 발생: {str(e)}"
        )
