from fastapi import HTTPException


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class IdNotValidException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Id not valid")


class PasswordNotMatchException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Password not match")


class IncorrectCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Incorrect username or password")


class ForbiddenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Forbidden")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="User already exists")


class ContestNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Contest not found")


class ContestAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Contest already exists")
