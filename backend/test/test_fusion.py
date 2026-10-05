from langchain_core.documents import Document

from backend.common.RetrieverConfigs import FusionConfig, FusionTypes
from backend.rag.Fusion import FusionFactory, RRFFusion, document_key


def _doc(content: str, document_id: str, chunk_index: int) -> Document:
    return Document(
        page_content=content,
        metadata={"document_id": document_id, "chunk_index": chunk_index},
    )


class TestDocumentKey:
    def test_prefers_document_id(self):
        doc = Document(id="abc", page_content="text", metadata={})

        assert document_key(doc) == "abc"

    def test_uses_document_id_and_chunk_index(self):
        doc = _doc("text", "doc-1", 2)

        assert document_key(doc) == "doc-1:2"

    def test_falls_back_to_truncated_page_content(self):
        content = "x" * 80
        doc = Document(page_content=content, metadata={})

        assert document_key(doc) == content[:50]
        assert len(document_key(doc)) == 50


class TestRRFFusion:
    def test_empty_lists_return_empty(self):
        assert RRFFusion().fuse([]) == []
        assert RRFFusion().fuse([[], []]) == []

    def test_single_list_preserves_order(self):
        docs = [_doc("a", "d1", 0), _doc("b", "d1", 1)]

        result = RRFFusion().fuse([docs])

        assert result == docs

    def test_merges_overlapping_lists_by_rrf_score(self):
        # Doc A ranks high in both lists → should win over B and C.
        doc_a = _doc("A", "d1", 0)
        doc_b = _doc("B", "d1", 1)
        doc_c = _doc("C", "d1", 2)

        list_1 = [doc_a, doc_b]
        list_2 = [doc_a, doc_c]

        result = RRFFusion(rrf_k=60).fuse([list_1, list_2])

        assert result[0].page_content == "A"
        assert {doc.page_content for doc in result} == {"A", "B", "C"}

    def test_deduplicates_by_metadata_key(self):
        first = _doc("first version", "d1", 0)
        second = _doc("second version", "d1", 0)

        result = RRFFusion().fuse([[first], [second]])

        assert len(result) == 1
        assert result[0] is first


class TestFusionFactory:
    def test_creates_rrf_fusion(self):
        config = FusionConfig(type=FusionTypes.RRF, rrf_k=40)

        fusion = FusionFactory.create_fusion(config)

        assert isinstance(fusion, RRFFusion)
        assert fusion.rrf_k == 40

    def test_default_config_uses_rrf(self):
        fusion = FusionFactory.create_fusion(FusionConfig())

        assert isinstance(fusion, RRFFusion)
        assert fusion.rrf_k == 60
