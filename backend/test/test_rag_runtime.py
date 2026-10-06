from backend.common.RagRuntime import RagRuntime


class TestRagRuntime:
    def test_holds_vector_store(self, vector_store):
        runtime = RagRuntime(vector_store=vector_store)

        assert runtime.vector_store is vector_store
        assert runtime.rerank_model is None
        assert runtime.db_session is None

    def test_holds_optional_deps(self, vector_store):
        rerank_model = object()
        db_session = object()
        runtime = RagRuntime(
            vector_store=vector_store,
            rerank_model=rerank_model,
            db_session=db_session,
        )

        assert runtime.rerank_model is rerank_model
        assert runtime.db_session is db_session
