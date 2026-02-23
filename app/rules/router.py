import uuid

from fastapi import APIRouter, Depends

from app.rules.dao import RulesDAO
from app.rules.dependencies import CheckUserPermission

router = APIRouter(prefix='/rules',
                   tags=['Правила доступа'])


@router.get('')
async def get_all_rules(
    current_user=Depends(CheckUserPermission("RULES", "read_all_p"))
):
    rules = await RulesDAO.find_all()
    return rules


@router.patch('/{rule_id}')
async def update_rule(
    rule_id: uuid.UUID,
    rule_data: dict,
    current_user=Depends(CheckUserPermission("RULES", "update_all_p"))
):
    rule = await RulesDAO.update_by_id(id=rule_id, **rule_data)
    return rule
