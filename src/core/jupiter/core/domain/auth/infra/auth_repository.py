"""A repository for auth information."""
from jupiter.core.domain.auth.auth import Auth
from jupiter.core.framework.repository import StubEntityRepository
from jupiter.core.framework.secure import secure_class


@secure_class
class AuthRepository(StubEntityRepository[Auth]):
    """A repository for auth information."""
