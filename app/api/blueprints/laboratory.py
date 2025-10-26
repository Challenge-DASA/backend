import random

from quart import Blueprint, jsonify
from quart_schema import tag_blueprint

from application.dto.input.transaction import WithdrawTransactionInput
from application.usecases.list_laboratory_balance import ListLaboratoryBalanceInput
from application.usecases.list_procedures import ListProceduresInput
from application.middleware.context import get_context
from application.container import container

laboratory_bp = Blueprint('laboratory', __name__, url_prefix='/laboratory')
tag_blueprint(laboratory_bp, ["Laboratory"])

@laboratory_bp.get("/<string:laboratory_id>/procedures")
async def list_procedures(laboratory_id: str):
    async with container.get_session():
        input_data = ListProceduresInput(laboratory_id=laboratory_id)
        result = await container.list_procedures_use_case.execute(input_data)
        return jsonify(result.model_dump() if hasattr(result, 'model_dump') else result)

@laboratory_bp.get("/<string:laboratory_id>/balance")
async def list_balance(laboratory_id: str):
    async with container.get_session():
        input_data = ListLaboratoryBalanceInput(laboratory_id=laboratory_id)
        result = await container.list_laboratory_balance_use_case.execute(input_data)
        return jsonify(result.model_dump() if hasattr(result, 'model_dump') else result)


@laboratory_bp.post("/<string:laboratory_id>/withdraw/<string:procedure_id>")
async def withdraw(laboratory_id: str, procedure_id: str):
    from quart import request

    context = get_context()

    user_id = request.headers.get('Authorization')
    if not user_id:
        return jsonify({"error": "Authorization header required"}), 401

    context.user_id = user_id

    async with container.get_session():
        input_data = WithdrawTransactionInput(
            laboratory_id=laboratory_id,
            procedure_id=procedure_id,
        )
        result = await container.withdraw_transaction_use_case.execute(context, input_data)
        return jsonify(result.model_dump() if hasattr(result, 'model_dump') else result)


@laboratory_bp.get("/monitoring")
async def get_monitoring():
    temperature_value = round(random.uniform(20.0, 25.0), 1)

    humidity_value = random.randint(40, 60)

    return jsonify({
        "temperature": {
            "value": temperature_value,
            "unit": "°C",
            "status": "Normal"
        },
        "humidity": {
            "value": humidity_value,
            "unit": "%",
            "status": "Normal"
        },
        "operationalStatus": "Operacional"
    })