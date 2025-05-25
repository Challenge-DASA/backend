# app/migrations_manager/main.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command
import click

project_root = Path(__file__).parent.parent.parent
migrations_manager_dir = Path(__file__).parent

sys.path.append(str(project_root))
load_dotenv(migrations_manager_dir / ".env")


class MigrationsManager:

    def __init__(self):
        self.project_root = project_root
        self.alembic_cfg = self._setup_alembic_config()

    def _setup_alembic_config(self):
        alembic_ini_path = self.project_root / "alembic.ini"

        if not alembic_ini_path.exists():
            raise FileNotFoundError(f"alembic.ini não encontrado em {alembic_ini_path}")

        cfg = Config(str(alembic_ini_path))

        database_url = self._get_database_url()
        cfg.set_main_option("sqlalchemy.url", str(database_url))

        return cfg

    @staticmethod
    def _get_database_url() -> str:
        host = os.getenv('ORACLE_HOST', 'localhost')
        port = os.getenv('ORACLE_PORT', '1521')
        service_name = os.getenv('ORACLE_SERVICE_NAME', 'FREEPDB1')
        username = os.getenv('ORACLE_USERNAME')
        password = os.getenv('ORACLE_PASSWORD')

        if not username or not password:
            raise ValueError("ORACLE_USERNAME e ORACLE_PASSWORD devem estar definidos no .env")

        url = f"oracle+oracledb://{username}:{password}@{host}:{port}/?service_name={service_name}"
        return str(url)

    def create_migration(self, message: str):
        try:
            command.revision(self.alembic_cfg, autogenerate=True, message=message)
            click.echo(f"Migration '{message}' criada com sucesso!")
        except Exception as e:
            click.echo(f"Erro ao criar migration: {e}", err=True)

    def upgrade(self, revision: str = "head"):
        try:
            command.upgrade(self.alembic_cfg, revision)
            click.echo(f"Upgrade para '{revision}' executado com sucesso!")
        except Exception as e:
            click.echo(f"Erro no upgrade: {e}", err=True)

    def downgrade(self, revision: str):
        try:
            command.downgrade(self.alembic_cfg, revision)
            click.echo(f"Downgrade para '{revision}' executado com sucesso!")
        except Exception as e:
            click.echo(f"Erro no downgrade: {e}", err=True)

    def current(self):
        try:
            command.current(self.alembic_cfg, verbose=True)
        except Exception as e:
            click.echo(f"Erro ao verificar current: {e}", err=True)

    def history(self):
        try:
            command.history(self.alembic_cfg, verbose=True)
        except Exception as e:
            click.echo(f"Erro ao mostrar histórico: {e}", err=True)

    def show_config(self):
        try:
            database_url = self._get_database_url()
            env_path = migrations_manager_dir / ".env"
            alembic_ini = self.project_root / "alembic.ini"

            click.echo("Configurações atuais:")
            click.echo(f"   Project Root: {self.project_root}")
            click.echo(f"   .env Path: {env_path}")
            click.echo(f"   alembic.ini: {alembic_ini}")
            click.echo(f"   Database URL: {database_url}")
            click.echo(f"   ORACLE_HOST: {os.getenv('ORACLE_HOST')}")
            click.echo(f"   ORACLE_PORT: {os.getenv('ORACLE_PORT')}")
            click.echo(f"   ORACLE_SERVICE_NAME: {os.getenv('ORACLE_SERVICE_NAME')}")
            click.echo(f"   ORACLE_USERNAME: {os.getenv('ORACLE_USERNAME')}")
        except Exception as e:
            click.echo(f"Erro na configuração: {e}", err=True)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('message')
def create(message: str):
    manager = MigrationsManager()
    manager.create_migration(message)


@cli.command()
@click.argument('revision', default='head')
def upgrade(revision: str):
    manager = MigrationsManager()
    manager.upgrade(revision)


@cli.command()
@click.argument('revision')
def downgrade(revision: str):
    manager = MigrationsManager()
    manager.downgrade(revision)


@cli.command()
def current():
    manager = MigrationsManager()
    manager.current()


@cli.command()
def history():
    manager = MigrationsManager()
    manager.history()


@cli.command()
def config():
    manager = MigrationsManager()
    manager.show_config()


if __name__ == '__main__':
    cli()