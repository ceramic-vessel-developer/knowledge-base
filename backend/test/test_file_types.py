from backend.common.FileTypes import FileTypes


class TestFileTypes:
    def test_members(self):
        assert FileTypes.PDF.value == 1
        assert FileTypes.TXT.value == 2
        assert FileTypes.OTHER.value == 3

    def test_is_unique(self):
        values = [member.value for member in FileTypes]
        assert len(values) == len(set(values))
