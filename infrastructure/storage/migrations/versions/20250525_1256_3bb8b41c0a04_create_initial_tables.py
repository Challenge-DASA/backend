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
    # Materiais básicos de coleta
    'Seringa 5ml': uuid.uuid4(),
    'Seringa 10ml': uuid.uuid4(),
    'Agulha 21G': uuid.uuid4(),
    'Agulha 23G': uuid.uuid4(),
    'Tubo EDTA': uuid.uuid4(),
    'Tubo Citrato': uuid.uuid4(),
    'Álcool Swab': uuid.uuid4(),
    'Curativo': uuid.uuid4(),

    # Materiais para urinálise
    'Frasco Urina Estéril': uuid.uuid4(),
    'Fita Reagente Urina': uuid.uuid4(),
    'Pipeta Pasteur': uuid.uuid4(),
    'Lâmina Microscopia': uuid.uuid4(),
    'Lamínula': uuid.uuid4(),

    # Materiais para cultura microbiológica
    'Placa Ágar Sangue': uuid.uuid4(),
    'Placa Ágar MacConkey': uuid.uuid4(),
    'Placa Ágar Chocolate': uuid.uuid4(),
    'Swab Estéril': uuid.uuid4(),
    'Meio BHI': uuid.uuid4(),
    'Disco Antibiótico': uuid.uuid4(),
    'Alça Bacteriológica': uuid.uuid4(),
    'Tubo Ensaio Estéril': uuid.uuid4(),

    # Materiais para biópsia
    'Agulha Biópsia 14G': uuid.uuid4(),
    'Pistola Biópsia': uuid.uuid4(),
    'Campo Cirúrgico': uuid.uuid4(),
    'Anestésico Local': uuid.uuid4(),
    'Formol 10%': uuid.uuid4(),
    'Frasco Histologia': uuid.uuid4(),
    'Compressa Cirúrgica': uuid.uuid4(),
    'Sutura': uuid.uuid4(),

    # Materiais para parasitologia
    'Frasco Fezes': uuid.uuid4(),
    'Solução Lugol': uuid.uuid4(),
    'Solução Fisiológica': uuid.uuid4(),
    'Centrífuga Tubo': uuid.uuid4(),
    'Kit Parasitológico': uuid.uuid4(),
}

PROCEDURE_IDS = {
    'Hemograma Completo': uuid.uuid4(),
    'Urinálise Completa': uuid.uuid4(),
    'Cultura de Escarro': uuid.uuid4(),
    'Biópsia por Punção': uuid.uuid4(),
    'Parasitológico de Fezes': uuid.uuid4(),
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

    materials_data = [
        # Materiais básicos
        ('Seringa 5ml', 'Seringa descartável de 5ml com agulha'),
        ('Seringa 10ml', 'Seringa descartável de 10ml com agulha'),
        ('Agulha 21G', 'Agulha descartável calibre 21G'),
        ('Agulha 23G', 'Agulha descartável calibre 23G'),
        ('Tubo EDTA', 'Tubo de coleta com anticoagulante EDTA'),
        ('Tubo Citrato', 'Tubo de coleta com citrato de sódio'),
        ('Álcool Swab', 'Algodão embebido em álcool 70%'),
        ('Curativo', 'Curativo adesivo para punção'),

        # Materiais para urinálise
        ('Frasco Urina Estéril', 'Frasco estéril para coleta de urina'),
        ('Fita Reagente Urina', 'Fita reagente para análise química da urina'),
        ('Pipeta Pasteur', 'Pipeta descartável para transferência de líquidos'),
        ('Lâmina Microscopia', 'Lâmina de vidro para microscopia'),
        ('Lamínula', 'Lamínula de vidro para cobertura'),

        # Materiais para cultura microbiológica
        ('Placa Ágar Sangue', 'Placa de Petri com ágar sangue'),
        ('Placa Ágar MacConkey', 'Placa de Petri com ágar MacConkey'),
        ('Placa Ágar Chocolate', 'Placa de Petri com ágar chocolate'),
        ('Swab Estéril', 'Swab estéril para coleta de material'),
        ('Meio BHI', 'Meio de cultura Brain Heart Infusion'),
        ('Disco Antibiótico', 'Disco impregnado com antibiótico'),
        ('Alça Bacteriológica', 'Alça de platina para semeadura'),
        ('Tubo Ensaio Estéril', 'Tubo de ensaio estéril para cultura'),

        # Materiais para biópsia
        ('Agulha Biópsia 14G', 'Agulha específica para biópsia calibre 14G'),
        ('Pistola Biópsia', 'Dispositivo automático para biópsia'),
        ('Campo Cirúrgico', 'Campo estéril descartável'),
        ('Anestésico Local', 'Anestésico local para infiltração'),
        ('Formol 10%', 'Solução de formol para fixação'),
        ('Frasco Histologia', 'Frasco para conservação de tecidos'),
        ('Compressa Cirúrgica', 'Compressa estéril para hemostasia'),
        ('Sutura', 'Fio de sutura para fechamento'),

        ('Frasco Fezes', 'Frasco para coleta de material fecal'),
        ('Solução Lugol', 'Solução de lugol para coloração'),
        ('Solução Fisiológica', 'Solução fisiológica estéril'),
        ('Centrífuga Tubo', 'Tubo para centrífuga'),
        ('Kit Parasitológico', 'Kit completo para pesquisa de parasitas'),
    ]

    for name, description in materials_data:
        op.execute(f"""
            INSERT INTO materials (material_id, name, description, created_at, updated_at)
            VALUES (HEXTORAW('{MATERIAL_IDS[name].hex}'), '{name}', '{description}', TIMESTAMP '{now}', TIMESTAMP '{now}')
        """)

    procedures_data = [
        ('Hemograma Completo', 'Exame de sangue para avaliar células sanguíneas'),
        ('Urinálise Completa', 'Análise física, química e microscópica da urina'),
        ('Cultura de Escarro', 'Cultura microbiológica para identificação de patógenos respiratórios'),
        ('Biópsia por Punção', 'Procedimento para coleta de tecido por punção guiada'),
        ('Parasitológico de Fezes', 'Pesquisa de parasitas intestinais em material fecal'),
    ]

    for name, description in procedures_data:
        op.execute(f"""
            INSERT INTO procedures (procedure_id, name, description, created_at, updated_at)
            VALUES (HEXTORAW('{PROCEDURE_IDS[name].hex}'), '{name}', '{description}', TIMESTAMP '{now}', TIMESTAMP '{now}')
        """)

    # Definir slots para cada procedimento no laboratório principal
    slots = {
        'Hemograma Completo': 1,
        'Urinálise Completa': 2,
        'Cultura de Escarro': 3,
        'Biópsia por Punção': 4,
        'Parasitológico de Fezes': 5
    }

    for proc_name in PROCEDURE_IDS.keys():
        op.execute(f"""
            INSERT INTO laboratory_procedures (laboratory_id, procedure_id, slot, created_at)
            VALUES (HEXTORAW('{DEFAULT_LAB_ID.hex}'), HEXTORAW('{PROCEDURE_IDS[proc_name].hex}'), {slots[proc_name]}, TIMESTAMP '{now}')
        """)

    # Definir slots para o laboratório secundário
    secondary_procedures = ['Hemograma Completo', 'Urinálise Completa', 'Parasitológico de Fezes']
    secondary_slots = {
        'Hemograma Completo': 1,
        'Urinálise Completa': 2,
        'Parasitológico de Fezes': 3
    }

    for proc_name in secondary_procedures:
        op.execute(f"""
            INSERT INTO laboratory_procedures (laboratory_id, procedure_id, slot, created_at)
            VALUES (HEXTORAW('{SECONDARY_LAB_ID.hex}'), HEXTORAW('{PROCEDURE_IDS[proc_name].hex}'), {secondary_slots[proc_name]}, TIMESTAMP '{now}')
        """)

    procedure_usages = [
        ('Hemograma Completo', 'Seringa 5ml', 1),
        ('Hemograma Completo', 'Agulha 21G', 1),
        ('Hemograma Completo', 'Tubo EDTA', 1),
        ('Hemograma Completo', 'Álcool Swab', 2),
        ('Hemograma Completo', 'Curativo', 1),

        ('Urinálise Completa', 'Frasco Urina Estéril', 1),
        ('Urinálise Completa', 'Fita Reagente Urina', 1),
        ('Urinálise Completa', 'Pipeta Pasteur', 2),
        ('Urinálise Completa', 'Lâmina Microscopia', 2),
        ('Urinálise Completa', 'Lamínula', 2),
        ('Urinálise Completa', 'Centrífuga Tubo', 1),
        ('Urinálise Completa', 'Solução Fisiológica', 1),

        ('Cultura de Escarro', 'Frasco Urina Estéril', 1),
        ('Cultura de Escarro', 'Swab Estéril', 2),
        ('Cultura de Escarro', 'Placa Ágar Sangue', 2),
        ('Cultura de Escarro', 'Placa Ágar MacConkey', 1),
        ('Cultura de Escarro', 'Placa Ágar Chocolate', 2),
        ('Cultura de Escarro', 'Meio BHI', 1),
        ('Cultura de Escarro', 'Disco Antibiótico', 8),
        ('Cultura de Escarro', 'Alça Bacteriológica', 1),
        ('Cultura de Escarro', 'Tubo Ensaio Estéril', 3),
        ('Cultura de Escarro', 'Pipeta Pasteur', 5),
        ('Cultura de Escarro', 'Lâmina Microscopia', 3),
        ('Cultura de Escarro', 'Lamínula', 3),

        ('Biópsia por Punção', 'Agulha Biópsia 14G', 2),
        ('Biópsia por Punção', 'Pistola Biópsia', 1),
        ('Biópsia por Punção', 'Campo Cirúrgico', 2),
        ('Biópsia por Punção', 'Anestésico Local', 1),
        ('Biópsia por Punção', 'Seringa 10ml', 2),
        ('Biópsia por Punção', 'Agulha 21G', 1),
        ('Biópsia por Punção', 'Álcool Swab', 10),
        ('Biópsia por Punção', 'Formol 10%', 1),
        ('Biópsia por Punção', 'Frasco Histologia', 2),
        ('Biópsia por Punção', 'Compressa Cirúrgica', 5),
        ('Biópsia por Punção', 'Sutura', 1),
        ('Biópsia por Punção', 'Curativo', 3),
        ('Biópsia por Punção', 'Lâmina Microscopia', 5),
        ('Biópsia por Punção', 'Lamínula', 5),
        ('Biópsia por Punção', 'Pipeta Pasteur', 3),

        ('Parasitológico de Fezes', 'Frasco Fezes', 1),
        ('Parasitológico de Fezes', 'Kit Parasitológico', 1),
        ('Parasitológico de Fezes', 'Solução Lugol', 1),
        ('Parasitológico de Fezes', 'Solução Fisiológica', 1),
        ('Parasitológico de Fezes', 'Centrífuga Tubo', 2),
        ('Parasitológico de Fezes', 'Lâmina Microscopia', 4),
        ('Parasitológico de Fezes', 'Lamínula', 4),
        ('Parasitológico de Fezes', 'Pipeta Pasteur', 3),
    ]

    for proc_name, mat_name, amount in procedure_usages:
        op.execute(f"""
            INSERT INTO procedure_usages (procedure_id, material_id, required_amount)
            VALUES (HEXTORAW('{PROCEDURE_IDS[proc_name].hex}'), HEXTORAW('{MATERIAL_IDS[mat_name].hex}'), {amount})
        """)

    material_stocks = {
        'Seringa 5ml': 500,
        'Seringa 10ml': 300,
        'Agulha 21G': 1000,
        'Agulha 23G': 800,
        'Tubo EDTA': 600,
        'Tubo Citrato': 200,
        'Álcool Swab': 2000,
        'Curativo': 1000,

        'Frasco Urina Estéril': 300,
        'Fita Reagente Urina': 100,
        'Pipeta Pasteur': 1000,
        'Lâmina Microscopia': 500,
        'Lamínula': 500,

        'Placa Ágar Sangue': 50,
        'Placa Ágar MacConkey': 30,
        'Placa Ágar Chocolate': 40,
        'Swab Estéril': 200,
        'Meio BHI': 25,
        'Disco Antibiótico': 500,
        'Alça Bacteriológica': 10,
        'Tubo Ensaio Estéril': 100,

        'Agulha Biópsia 14G': 20,
        'Pistola Biópsia': 5,
        'Campo Cirúrgico': 50,
        'Anestésico Local': 10,
        'Formol 10%': 5,
        'Frasco Histologia': 50,
        'Compressa Cirúrgica': 100,
        'Sutura': 30,

        'Frasco Fezes': 200,
        'Solução Lugol': 15,
        'Solução Fisiológica': 50,
        'Centrífuga Tubo': 300,
        'Kit Parasitológico': 25,
    }

    for mat_name, stock in material_stocks.items():
        op.execute(f"""
            INSERT INTO material_balances (material_id, laboratory_id, current_stock, reserved_stock, last_updated)
            VALUES (HEXTORAW('{MATERIAL_IDS[mat_name].hex}'), HEXTORAW('{DEFAULT_LAB_ID.hex}'), {stock}, 0, TIMESTAMP '{now}')
        """)

    secondary_materials = {
        # Para Hemograma
        'Seringa 5ml': 100,
        'Agulha 21G': 200,
        'Tubo EDTA': 150,
        'Álcool Swab': 400,
        'Curativo': 200,

        # Para Urinálise
        'Frasco Urina Estéril': 100,
        'Fita Reagente Urina': 30,
        'Pipeta Pasteur': 200,
        'Lâmina Microscopia': 100,
        'Lamínula': 100,
        'Centrífuga Tubo': 50,
        'Solução Fisiológica': 10,

        # Para Parasitológico
        'Frasco Fezes': 50,
        'Kit Parasitológico': 10,
        'Solução Lugol': 5,
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