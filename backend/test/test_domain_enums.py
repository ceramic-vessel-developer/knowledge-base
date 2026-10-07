from backend.common.message_author import MessageAuthor
from backend.common.role import UserRole
from backend.common.workspace_type import WorkspaceType


class TestUserRole:
    def test_values(self):
        assert UserRole.USER == "user"
        assert UserRole.ADMIN == "admin"


class TestWorkspaceType:
    def test_values(self):
        assert WorkspaceType.BASIC == "basic"


class TestMessageAuthor:
    def test_values(self):
        assert MessageAuthor.USER == "user"
        assert MessageAuthor.AI == "ai"
