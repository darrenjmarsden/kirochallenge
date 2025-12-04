"""Custom exceptions for the registration system"""


class RegistrationSystemError(Exception):
    """Base exception for all registration system errors"""
    pass


class ValidationError(RegistrationSystemError):
    """Raised when input validation fails"""
    pass


class DuplicateError(RegistrationSystemError):
    """Raised when attempting to create a duplicate resource"""
    pass


class NotFoundError(RegistrationSystemError):
    """Raised when a requested resource doesn't exist"""
    pass


class CapacityError(RegistrationSystemError):
    """Raised when event capacity constraints are violated"""
    pass


class RegistrationError(RegistrationSystemError):
    """Raised when registration operations fail"""
    pass
