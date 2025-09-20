import quart_schema
from quart import Blueprint
from quart_schema import tag_blueprint

from application.dto.input.transaction import WithdrawTransactionInput
from application.dto.output.procedure import ListProceduresOutput
from application.dto.output.transaction import WithdrawTransactionOutput
from application.usecases.list_laboratory_balance import ListLaboratoryBalanceOutput, ListLaboratoryBalanceInput
from application.usecases.list_procedures import ListProceduresInput
from application.middleware.context import get_context
from application.container import container

laboratory_bp = Blueprint('laboratory', __name__, url_prefix='/laboratory')
tag_blueprint(laboratory_bp, ["Laboratory"])

@laboratory_bp.get("/<string:laboratory_id>/procedures")
@quart_schema.validate_response(ListProceduresOutput)
async def list_procedures(laboratory_id: str):
    async with container.get_session():
        input_data = ListProceduresInput(laboratory_id=laboratory_id)
        return await container.list_procedures_use_case.execute(input_data)

@laboratory_bp.get("/<string:laboratory_id>/balance")
@quart_schema.validate_response(ListLaboratoryBalanceOutput)
async def list_balance(laboratory_id: str):
    async with container.get_session():
        input_data = ListLaboratoryBalanceInput(laboratory_id=laboratory_id)
        return await container.list_laboratory_balance_use_case.execute(input_data)


@laboratory_bp.post("/<string:laboratory_id>/withdraw/<string:procedure_id>")
@quart_schema.validate_response(WithdrawTransactionOutput)
async def withdraw(laboratory_id: str, procedure_id: str):
    from quart import request

    context = get_context()

    user_id = request.headers.get('Authorization')
    if not user_id:
        return {"error": "Authorization header required"}, 401

    context.user_id = user_id

    async with container.get_session():
        input_data = WithdrawTransactionInput(
            laboratory_id=laboratory_id,
            procedure_id=procedure_id,
        )
        return await container.withdraw_transaction_use_case.execute(context, input_data)