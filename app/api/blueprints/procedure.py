from quart import Blueprint, jsonify, request
from quart_schema import tag_blueprint, validate_querystring
from typing import Optional
from datetime import datetime
from dataclasses import dataclass

from application.dto.input.procedure import ListProcedureMaterialsInput
from application.dto.input.transaction import ListTransactionsInput
from application.container import container
from application.middleware.context import get_context
from domain.context import Context

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')
tag_blueprint(transactions_bp, ["Transactions"])


@dataclass
class ListTransactionsQueryParams:
    """Query parameters para listagem de transações"""
    laboratory_id: Optional[str] = None
    user_id: Optional[str] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None  # ISO 8601 format
    end_date: Optional[str] = None  # ISO 8601 format


@transactions_bp.get("/")
async def list_transactions():
    args = request.args

    start_date = None
    end_date = None

    if args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(args.get('start_date').replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use ISO 8601"}), 400

    if args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(args.get('end_date').replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use ISO 8601"}), 400

    # Monta input
    input_data = ListTransactionsInput(
        laboratory_id=args.get('laboratory_id'),
        user_id=args.get('user_id'),
        transaction_type=args.get('transaction_type'),
        status=args.get('status'),
        start_date=start_date,
        end_date=end_date
    )

    context = get_context()

    async with container.get_session():
        result = await container.list_transactions_use_case.execute(context, input_data)

        response = [
            {
                "employeeId": transaction.employee_id,
                "procedure": {
                    "id": transaction.procedure.id,
                    "name": transaction.procedure.name,
                    "items": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "quantity": item.quantity
                        }
                        for item in transaction.procedure.items
                    ]
                } if transaction.procedure else None,
                "timestamp": transaction.timestamp.isoformat()
            }
            for transaction in result.transactions
        ]

        return jsonify(response)


@transactions_bp.get("/recent")
async def list_recent_transactions():
    from datetime import timedelta

    now = datetime.now()
    yesterday = now - timedelta(days=1)

    input_data = ListTransactionsInput(
        start_date=yesterday,
        end_date=now
    )

    context = get_context()

    async with container.get_session():
        result = await container.list_transactions_use_case.execute(context, input_data)

        response = [
            {
                "employeeId": transaction.employee_id,
                "procedure": {
                    "id": transaction.procedure.id,
                    "name": transaction.procedure.name,
                    "items": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "quantity": item.quantity
                        }
                        for item in transaction.procedure.items
                    ]
                } if transaction.procedure else None,
                "timestamp": transaction.timestamp.isoformat()
            }
            for transaction in result.transactions
        ]

        return jsonify(response)


@transactions_bp.get("/laboratory/<string:laboratory_id>")
async def list_laboratory_transactions(laboratory_id: str):
    input_data = ListTransactionsInput(
        laboratory_id=laboratory_id
    )

    context = get_context()

    async with container.get_session():
        result = await container.list_transactions_use_case.execute(context, input_data)

        response = [
            {
                "employeeId": transaction.employee_id,
                "procedure": {
                    "id": transaction.procedure.id,
                    "name": transaction.procedure.name,
                    "items": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "quantity": item.quantity
                        }
                        for item in transaction.procedure.items
                    ]
                } if transaction.procedure else None,
                "timestamp": transaction.timestamp.isoformat()
            }
            for transaction in result.transactions
        ]

        return jsonify(response)

procedures_bp = Blueprint('procedures', __name__, url_prefix='/procedures')
tag_blueprint(procedures_bp, ["Procedures"])

@procedures_bp.get("/<string:procedure_id>/materials")
async def list_materials(procedure_id: str):
    async with container.get_session():
        input_data = ListProcedureMaterialsInput(procedure_id=procedure_id)
        result = await container.list_procedure_materials_use_case.execute(input_data)
        return jsonify(result.model_dump() if hasattr(result, 'model_dump') else result)