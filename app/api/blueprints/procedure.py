from quart import Blueprint, jsonify
from quart_schema import tag_blueprint

from application.dto.input.procedure import ListProcedureMaterialsInput
from application.dto.output.procedure import ListProcedureMaterialsOutput
from application.container import container

procedures_bp = Blueprint('procedures', __name__, url_prefix='/procedures')
tag_blueprint(procedures_bp, ["Procedures"])

@procedures_bp.get("/<string:procedure_id>/materials")
async def list_materials(procedure_id: str):
    async with container.get_session():
        input_data = ListProcedureMaterialsInput(procedure_id=procedure_id)
        result = await container.list_procedure_materials_use_case.execute(input_data)
        return jsonify(result.model_dump() if hasattr(result, 'model_dump') else result)