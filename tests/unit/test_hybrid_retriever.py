"""Tests for hybrid.py — hybrid retrieval scoring behavior."""

from unittest.mock import MagicMock, patch

import pytest

from rag.retriever.hybrid import HybridRetriever


@pytest.mark.unit
class TestHybridRetriever:
    """Test suite for HybridRetriever scoring and ranking."""

    @pytest.fixture
    def vector_store(self):
        return MagicMock()

    @pytest.fixture
    def keyword_searcher(self):
        return MagicMock()

    @pytest.fixture
    def retriever(self, vector_store, keyword_searcher):
        return HybridRetriever(vector_store, keyword_searcher)

    def test_default_weights(self, retriever):
        """Default blend weights match architecture docs (0.7 vector, 0.3 keyword)."""
        assert retriever.vector_weight == 0.7
        assert retriever.keyword_weight == 0.3

    def test_blended_score_formula(self, retriever, vector_store, keyword_searcher):
        """Blended score uses normalized channel scores and default weights."""
        vector_store.query.return_value = [
            {"id": "a", "text": "chunk a", "metadata": {}, "score": 0.80},
            {"id": "b", "text": "chunk b", "metadata": {}, "score": 0.40},
        ]
        keyword_searcher.search.return_value = [
            {"id": "a", "text": "chunk a", "metadata": {}, "bm25_score": 2.0},
            {"id": "b", "text": "chunk b", "metadata": {}, "bm25_score": 6.0},
        ]
        vector_store.get_collection.return_value.get.return_value = {
            "ids": ["a", "b"],
            "documents": ["chunk a", "chunk b"],
            "metadatas": [{}, {}],
        }

        results = retriever.retrieve(
            query="test",
            profile_id="123",
            query_embedding=[0.1, 0.2],
            max_chunks=10,
            min_score=0.0,
        )

        by_id = {r["id"]: r for r in results}
        assert by_id["a"]["vector_score"] == pytest.approx(1.0)
        assert by_id["a"]["keyword_score"] == pytest.approx(2.0 / 6.0)
        assert by_id["a"]["score"] == pytest.approx(0.7 * 1.0 + 0.3 * (2.0 / 6.0))
        assert by_id["b"]["score"] == pytest.approx(0.7 * 0.5 + 0.3 * 1.0)
        assert results[0]["id"] == "a"

    def test_min_score_filters_low_results(self, retriever, vector_store, keyword_searcher):
        """Chunks below min_score are excluded from final results."""
        vector_store.query.return_value = [
            {"id": "low", "text": "weak match", "metadata": {}, "score": 0.10},
            {"id": "high", "text": "strong match", "metadata": {}, "score": 0.90},
        ]
        keyword_searcher.search.return_value = [
            {"id": "low", "text": "weak match", "metadata": {}, "bm25_score": 0.5},
            {"id": "high", "text": "strong match", "metadata": {}, "bm25_score": 5.0},
        ]
        vector_store.get_collection.return_value.get.return_value = {
            "ids": ["low", "high"],
            "documents": ["weak match", "strong match"],
            "metadatas": [{}, {}],
        }

        results = retriever.retrieve(
            query="test",
            profile_id="123",
            query_embedding=[0.1],
            min_score=0.3,
        )

        assert len(results) == 1
        assert results[0]["id"] == "high"

    def test_single_channel_chunk_gets_zero_for_missing_channel(
        self, retriever, vector_store, keyword_searcher
    ):
        """Chunk in only one channel contributes 0 for the missing channel."""
        vector_store.query.return_value = [
            {"id": "vec-only", "text": "vector hit", "metadata": {}, "score": 0.60},
        ]
        keyword_searcher.search.return_value = [
            {"id": "kw-only", "text": "keyword hit", "metadata": {}, "bm25_score": 4.0},
        ]
        vector_store.get_collection.return_value.get.return_value = {
            "ids": ["vec-only", "kw-only"],
            "documents": ["vector hit", "keyword hit"],
            "metadatas": [{}, {}],
        }

        results = retriever.retrieve(
            query="test",
            profile_id="123",
            query_embedding=[0.1],
            min_score=0.0,
        )

        by_id = {r["id"]: r for r in results}
        assert by_id["vec-only"]["keyword_score"] == 0.0
        assert by_id["kw-only"]["vector_score"] == 0.0

    def test_respects_max_chunks(self, retriever, vector_store, keyword_searcher):
        """Final result count is capped at max_chunks."""
        chunks = [
            {
                "id": f"c{i}",
                "text": f"chunk {i}",
                "metadata": {},
                "score": 1.0 - i * 0.1,
                "bm25_score": float(i + 1),
            }
            for i in range(5)
        ]
        vector_store.query.return_value = chunks
        keyword_searcher.search.return_value = chunks
        vector_store.get_collection.return_value.get.return_value = {
            "ids": [c["id"] for c in chunks],
            "documents": [c["text"] for c in chunks],
            "metadatas": [{} for _ in chunks],
        }

        results = retriever.retrieve(
            query="test",
            profile_id="123",
            query_embedding=[0.1],
            max_chunks=2,
            min_score=0.0,
        )

        assert len(results) == 2

    @patch.object(HybridRetriever, "_get_all_chunks", return_value=[])
    def test_empty_results_when_both_channels_empty(
        self, _mock_get_chunks, retriever, vector_store, keyword_searcher
    ):
        """Empty vector and keyword result sets yield no blended results."""
        vector_store.query.return_value = []
        keyword_searcher.search.return_value = []

        results = retriever.retrieve(
            query="test",
            profile_id="123",
            query_embedding=[0.1],
        )

        assert results == []
