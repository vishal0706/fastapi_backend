from enum import Enum


class TokenType(str, Enum):
    BEARER = 'bearer'
    RESET_PASSWORD = 'reset_password'
    REFRESH = 'refresh'


class Role(str, Enum):
    SUPER_ADMIN = 'SUPER_ADMIN'
    TALENT = 'TALENT'
    CLIENT = 'CLIENT'


class AccountType(str, Enum):
    INDIVIDUAL = 'INDIVIDUAL'
    ORGANIZATION = 'ORGANIZATION'


class AccountStatus(str, Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class Relationship(str, Enum):
    FATHER = 'FATHER'
    MOTHER = 'MOTHER'
    OTHER = 'OTHER'


class Gender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class AssignmentStatus(str, Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
