from quart import Quart
from quart_schema import QuartSchema

from application.config import get_config
from domain.entities.laboratory import LaboratoryId
from domain.entities.procedure import ProcedureId
from application.middleware.context import ContextMiddleware, get_context
from application.usecases.create_transaction import WithdrawTransaction

config = get_config()
app = Quart(__name__)
app.config.from_object(config)
QuartSchema(app)

context_middleware = ContextMiddleware(app)

create_transaction = WithdrawTransaction()


@app.post("/transaction/withdraw/<uuid:laboratory_id>/<uuid:medical_procedure_id>")
async def create_transaction_endpoint(laboratory_id: LaboratoryId, medical_procedure_id: ProcedureId):
    context = get_context()

    transaction_data = create_transaction.execute(context, laboratory_id, medical_procedure_id)

    return {
        "transaction": transaction_data,
        "context": {
            "request_id": context.request_id,
            "user_id": context.user_id,
            "timestamp": context.request_datetime.isoformat()
        }
    }


@app.get("/health")
async def health_check():
    context = get_context()

    return {
        "status": "healthy",
        "request_id": context.request_id,
        "timestamp": context.request_datetime.isoformat()
    }


if __name__ == "__main__":
    app.run(debug=config.DEBUG)