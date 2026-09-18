import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    DATA_STEWARD = "DataSteward"