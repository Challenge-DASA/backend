"""create_initial_tables

Revision ID: 3bb8b41c0a04
Revises:
Create Date: 2025-05-25 12:56:14.161299

"""
import datetime
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import oracle
import uuid

# revision identifiers, used by Alembic.
revision: str = '3bb8b41c0a04'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_LAB_ID = uuid.UUID('12345678-1234-5678-1234-123456789012')
SECONDARY_LAB_ID = uuid.UUID('87654321-8765-4321-8765-876543218765')

MATERIAL_IDS = {
    # Kit 1 - Punção venosa simples
    'Luvas descartáveis': uuid.uuid4(),
    'Gaze estéril': uuid.uuid4(),
    'Seringa 5ml': uuid.uuid4(),
    'Agulha 25x7': uuid.uuid4(),
    'Agulha 25x8': uuid.uuid4(),
    'Álcool 70% sachê': uuid.uuid4(),

    # Kit 2 - Punção venosa com scalp
    'Scalp nº 21': uuid.uuid4(),
    'Scalp nº 23': uuid.uuid4(),

    # Kit 3 - Cateter venoso periférico
    'Cateter venoso periférico nº 20': uuid.uuid4(),
    'Cateter venoso periférico nº 22': uuid.uuid4(),
    'Seringa com solução salina': uuid.uuid4(),
    'Curativo transparente': uuid.uuid4(),
    'Micropore': uuid.uuid4(),

    # Kit 4 - Curativo simples
    'Soro fisiológico pequeno': uuid.uuid4(),
}

PROCEDURE_IDS = {
    'Punção venosa simples': uuid.uuid4(),
    'Punção venosa com scalp': uuid.uuid4(),
    'Cateter venoso periférico': uuid.uuid4(),
    'Curativo simples': uuid.uuid4(),
}

def upgrade() -> None:
    """Upgrade schema."""

    op.create_table('materials',
        sa.Column('material_id', oracle.RAW(16), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )

    op.create_table('procedures',
        sa.Column('procedure_id', oracle.RAW(16), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True)
    )

    op.create_table('laboratory_procedures',
        sa.Column('laboratory_id', oracle.RAW(16), nullable=False),
        sa.Column('procedure_id', oracle.RAW(16), nullable=False),
        sa.Column('slot', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('laboratory_id', 'procedure_id'),
        sa.ForeignKeyConstraint(['procedure_id'], ['procedures.procedure_id'])
    )

    op.create_table('procedure_usages',
        sa.Column('procedure_id', oracle.RAW(16), nullable=False),
        sa.Column('material_id', oracle.RAW(16), nullable=False),
        sa.Column('required_amount', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('procedure_id', 'material_id'),
        sa.ForeignKeyConstraint(['procedure_id'], ['procedures.procedure_id']),
        sa.ForeignKeyConstraint(['material_id'], ['materials.material_id'])
    )

    op.create_table('material_balances',
        sa.Column('material_id', oracle.RAW(16), nullable=False),
        sa.Column('laboratory_id', oracle.RAW(16), nullable=False),
        sa.Column('current_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reserved_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('material_id', 'laboratory_id'),
        sa.ForeignKeyConstraint(['material_id'], ['materials.material_id'])
    )

    op.create_table('transactions',
        sa.Column('transaction_id', oracle.RAW(16), primary_key=True),
        sa.Column('transaction_type', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('laboratory_id', oracle.RAW(16), nullable=False),
        sa.Column('user_id', oracle.RAW(16), nullable=False),
        sa.Column('procedure_id', oracle.RAW(16), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('authorized_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['procedure_id'], ['procedures.procedure_id'])
    )

    op.create_table('transaction_items',
        sa.Column('transaction_id', oracle.RAW(16), nullable=False),
        sa.Column('material_id', oracle.RAW(16), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('transaction_id', 'material_id'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id']),
        sa.ForeignKeyConstraint(['material_id'], ['materials.material_id'])
    )

    now = datetime.datetime.now(datetime.UTC)

    # Inserir materiais
    materials_data = [
        # Materiais comuns a vários kits
        ('Luvas descartáveis', 'Luvas descartáveis não estéreis para procedimentos'),
        ('Gaze estéril', 'Compressas de gaze estéril para curativos'),
        ('Seringa 5ml', 'Seringa descartável de 5ml com bico luer'),
        ('Agulha 25x7', 'Agulha descartável 25G x 7mm para aplicação subcutânea'),
        ('Agulha 25x8', 'Agulha descartável 25G x 8mm para aplicação subcutânea'),
        ('Álcool 70% sachê', 'Sachê ou pad com álcool 70% para antissepsia'),

        # Kit 2 específico
        ('Scalp nº 21', 'Scalp venoso calibre 21G para acesso venoso'),
        ('Scalp nº 23', 'Scalp venoso calibre 23G para acesso venoso'),

        # Kit 3 específico
        ('Cateter venoso periférico nº 20', 'Cateter venoso periférico calibre 20G'),
        ('Cateter venoso periférico nº 22', 'Cateter venoso periférico calibre 22G'),
        ('Seringa com solução salina', 'Seringa pré-carregada com soro fisiológico para flush'),
        ('Curativo transparente', 'Curativo transparente adesivo para fixação de cateter'),
        ('Micropore', 'Fita micropore para fixação de curativos'),

        # Kit 4 específico
        ('Soro fisiológico pequeno', 'Frasco pequeno ou ampola de soro fisiológico para limpeza'),
    ]

    for name, description in materials_data:
        op.execute(f"""
            INSERT INTO materials (material_id, name, description, created_at, updated_at)
            VALUES (HEXTORAW('{MATERIAL_IDS[name].hex}'), '{name}', '{description}', TIMESTAMP '{now}', TIMESTAMP '{now}')
        """)

    # Inserir procedures (kits)
    procedures_data = [
        ('Punção venosa simples', 'Kit para coleta de sangue e aplicação de medicação via punção venosa simples'),
        ('Punção venosa com scalp', 'Kit para medicação EV rápida ou coleta em pacientes com acesso difícil usando scalp'),
        ('Cateter venoso periférico', 'Kit para instalação de acesso venoso prolongado com cateter periférico'),
        ('Curativo simples', 'Kit para realização de curativo simples em feridas ou punções'),
    ]

    for name, description in procedures_data:
        op.execute(f"""
            INSERT INTO procedures (procedure_id, name, description, created_at, updated_at)
            VALUES (HEXTORAW('{PROCEDURE_IDS[name].hex}'), '{name}', '{description}', TIMESTAMP '{now}', TIMESTAMP '{now}')
        """)

    # Definir slots para cada kit no laboratório principal
    slots = {
        'Punção venosa simples': 1,
        'Punção venosa com scalp': 2,
        'Cateter venoso periférico': 3,
        'Curativo simples': 4
    }

    for proc_name in PROCEDURE_IDS.keys():
        op.execute(f"""
            INSERT INTO laboratory_procedures (laboratory_id, procedure_id, slot, created_at)
            VALUES (HEXTORAW('{DEFAULT_LAB_ID.hex}'), HEXTORAW('{PROCEDURE_IDS[proc_name].hex}'), {slots[proc_name]}, TIMESTAMP '{now}')
        """)

    # Definir slots para o laboratório secundário (todos os kits disponíveis)
    for proc_name in PROCEDURE_IDS.keys():
        op.execute(f"""
            INSERT INTO laboratory_procedures (laboratory_id, procedure_id, slot, created_at)
            VALUES (HEXTORAW('{SECONDARY_LAB_ID.hex}'), HEXTORAW('{PROCEDURE_IDS[proc_name].hex}'), {slots[proc_name]}, TIMESTAMP '{now}')
        """)

    # Definir uso de materiais por procedure
    procedure_usages = [
        # Punção venosa simples
        ('Punção venosa simples', 'Luvas descartáveis', 1),
        ('Punção venosa simples', 'Gaze estéril', 1),
        ('Punção venosa simples', 'Seringa 5ml', 1),
        ('Punção venosa simples', 'Agulha 25x7', 1),  # Opção padrão (ou 25x8)
        ('Punção venosa simples', 'Álcool 70% sachê', 1),

        # Punção venosa com scalp
        ('Punção venosa com scalp', 'Luvas descartáveis', 1),
        ('Punção venosa com scalp', 'Gaze estéril', 1),
        ('Punção venosa com scalp', 'Scalp nº 21', 1),  # Opção padrão (ou nº 23)
        ('Punção venosa com scalp', 'Seringa 5ml', 1),
        ('Punção venosa com scalp', 'Álcool 70% sachê', 1),

        # Cateter venoso periférico
        ('Cateter venoso periférico', 'Luvas descartáveis', 1),
        ('Cateter venoso periférico', 'Gaze estéril', 1),
        ('Cateter venoso periférico', 'Cateter venoso periférico nº 20', 1),  # Opção padrão (ou nº 22)
        ('Cateter venoso periférico', 'Seringa com solução salina', 1),
        ('Cateter venoso periférico', 'Curativo transparente', 1),  # Opção padrão (ou micropore)

        # Curativo simples
        ('Curativo simples', 'Luvas descartáveis', 1),
        ('Curativo simples', 'Gaze estéril', 1),
        ('Curativo simples', 'Soro fisiológico pequeno', 1),
        ('Curativo simples', 'Micropore', 1),
        ('Curativo simples', 'Álcool 70% sachê', 1),
    ]

    for proc_name, mat_name, amount in procedure_usages:
        op.execute(f"""
            INSERT INTO procedure_usages (procedure_id, material_id, required_amount)
            VALUES (HEXTORAW('{PROCEDURE_IDS[proc_name].hex}'), HEXTORAW('{MATERIAL_IDS[mat_name].hex}'), {amount})
        """)

    # Definir estoque inicial dos materiais no laboratório principal
    material_stocks = {
        'Luvas descartáveis': 1000,     # Muito usado
        'Gaze estéril': 500,            # Muito usado
        'Seringa 5ml': 300,
        'Agulha 25x7': 400,
        'Agulha 25x8': 300,
        'Álcool 70% sachê': 800,        # Muito usado

        'Scalp nº 21': 100,
        'Scalp nº 23': 80,

        'Cateter venoso periférico nº 20': 50,
        'Cateter venoso periférico nº 22': 40,
        'Seringa com solução salina': 100,
        'Curativo transparente': 80,
        'Micropore': 200,               # Muito usado

        'Soro fisiológico pequeno': 100,
    }

    for mat_name, stock in material_stocks.items():
        op.execute(f"""
            INSERT INTO material_balances (material_id, laboratory_id, current_stock, reserved_stock, last_updated)
            VALUES (HEXTORAW('{MATERIAL_IDS[mat_name].hex}'), HEXTORAW('{DEFAULT_LAB_ID.hex}'), {stock}, 0, TIMESTAMP '{now}')
        """)

    # Estoque reduzido para laboratório secundário
    secondary_materials = {
        'Luvas descartáveis': 200,
        'Gaze estéril': 100,
        'Seringa 5ml': 60,
        'Agulha 25x7': 80,
        'Agulha 25x8': 60,
        'Álcool 70% sachê': 160,

        'Scalp nº 21': 20,
        'Scalp nº 23': 15,

        'Cateter venoso periférico nº 20': 10,
        'Cateter venoso periférico nº 22': 8,
        'Seringa com solução salina': 20,
        'Curativo transparente': 15,
        'Micropore': 40,

        'Soro fisiológico pequeno': 20,
    }

    for mat_name, stock in secondary_materials.items():
        op.execute(f"""
            INSERT INTO material_balances (material_id, laboratory_id, current_stock, reserved_stock, last_updated)
            VALUES (HEXTORAW('{MATERIAL_IDS[mat_name].hex}'), HEXTORAW('{SECONDARY_LAB_ID.hex}'), {stock}, 0, TIMESTAMP '{now}')
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('transaction_items')
    op.drop_table('transactions')
    op.drop_table('material_balances')
    op.drop_table('procedure_usages')
    op.drop_table('laboratory_procedures')
    op.drop_table('procedures')
    op.drop_table('materials')