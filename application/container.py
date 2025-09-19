from contextlib import asynccontextmanager

from application.usecases.list_laboratory_balance import ListLaboratoryBalanceUseCase
from application.usecases.list_procedure_materials import ListProcedureMaterialsUseCase
from application.usecases.withdraw import WithdrawTransactionUseCase
from infrastructure.storage.oracle.database import async_session_factory
from infrastructure.storage.repositories.material_balance_repository import MaterialBalanceRepositoryImpl
from infrastructure.storage.repositories.material_repository import MaterialRepositoryImpl
from infrastructure.storage.repositories.procedure_repository import ProcedureRepositoryImpl
from application.usecases.list_procedures import ListProceduresUseCase
from infrastructure.storage.repositories.transaction_repository import TransactionRepositoryImpl


class Container:
    def __init__(self):
        self._session = None
        self._procedure_repository = None
        self._material_repository = None
        self._material_balance_repository = None
        self._transaction_repository = None

        self._list_procedures_use_case = None
        self._list_procedure_materials_use_case = None
        self._list_laboratory_balance_use_case = None
        self._withdraw_transaction_use_case = None


    @asynccontextmanager
    async def get_session(self):
        async with async_session_factory() as session:
            self._session = session
            try:
                yield session
            finally:
                self._session = None
                self._procedure_repository = None
                self._list_procedures_use_case = None

    @property
    def procedure_repository(self) -> ProcedureRepositoryImpl:
        if self._procedure_repository is None:
            if self._session is None:
                raise RuntimeError("Session not initialized. Use get_session() context manager.")
            self._procedure_repository = ProcedureRepositoryImpl(self._session)
        return self._procedure_repository

    @property
    def material_repository(self) -> MaterialRepositoryImpl:
        if self._material_repository is None:
            if self._session is None:
                raise RuntimeError("Session not initialized. Use get_session() context manager.")
            self._material_repository = MaterialRepositoryImpl(self._session)
        return self._material_repository

    @property
    def material_balance_repository(self):
        if self._material_balance_repository is None:
            if self._session is None:
                raise RuntimeError("Session not initialized. Use get_session() context manager.")
            self._material_balance_repository = MaterialBalanceRepositoryImpl(self._session)
        return self._material_balance_repository

    @property
    def transaction_repository(self):
        if self._transaction_repository is None:
            if self._session is None:
                raise RuntimeError("Session not initialized. Use get_session() context manager.")
            self._transaction_repository = TransactionRepositoryImpl(self._session)
        return self._transaction_repository

    @property
    def list_procedures_use_case(self) -> ListProceduresUseCase:
        if self._list_procedures_use_case is None:
            self._list_procedures_use_case = ListProceduresUseCase(self.procedure_repository)
        return self._list_procedures_use_case

    @property
    def list_procedure_materials_use_case(self) -> ListProcedureMaterialsUseCase:
        if self._list_procedures_use_case is None:
            self._list_procedures_use_case = ListProcedureMaterialsUseCase(self.procedure_repository, self.material_repository)
        return self._list_procedures_use_case

    @property
    def list_laboratory_balance_use_case(self):
        if self._list_laboratory_balance_use_case is None:
            self._list_laboratory_balance_use_case = ListLaboratoryBalanceUseCase(self.material_balance_repository, self.material_repository)
        return self._list_laboratory_balance_use_case

    @property
    def withdraw_transaction_use_case(self):
        if self._withdraw_transaction_use_case is None:
            self._withdraw_transaction_use_case = WithdrawTransactionUseCase(
                self.transaction_repository,
                self.procedure_repository,
                self.material_balance_repository,
                self.material_repository
            )
        return self._withdraw_transaction_use_case

container = Container()