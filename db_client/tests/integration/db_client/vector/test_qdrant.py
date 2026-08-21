from typing import List

from db_client.vector.qdrant import VectorDBAccessor
from qdrant_client.models import Filter, FieldCondition, MatchValue


class TestVectorDBAccessor:
    def __init__(self):
        self.vectordb = VectorDBAccessor(
            collection_name_list=["test_collection"],
            collection_dim=5,
            meta_indexing_field="payload_id",
            recreate=True
        )
    
    def _test_upsert(self):
        assert self.vectordb.count("test_collection") == 0
        vector_list = [list(range(i, i + 5)) for i in range(3)]
        payload_list = [{"payload_id": f"abc_{i}"} for i in range(3)]
        self.vectordb.upsert("test_collection", vector_list, payload_list)
        assert self.vectordb.count("test_collection") == 3

    def _test_search_by_vector(self):
        out = self.vectordb.search("test_collection", vector=list(range(1, 6)), limit=1)
        assert isinstance(out, List) and len(out) == 1
        assert out[0].payload == {"payload_id": "abc_1"}
    
    def _test_search_by_meta(self):
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="payload_id",
                    match=MatchValue(value="abc_1")
                )
            ]
        )  # use should=... for 'or'; Range(gt, lt) for range search
        out = self.vectordb.search("test_collection", query_filter=query_filter, limit=1)
        assert isinstance(out, List) and len(out) == 1
        assert out[0].payload == {"payload_id": "abc_1"}

    def _test_delete_by_id(self):
        out = self.vectordb.search("test_collection", vector=[1] * 5, limit=1)
        delete_id = out[0].vector_id
        self.vectordb.delete_by_id("test_collection", [delete_id])
        assert self.vectordb.count("test_collection") == 2

    def _test_delete_by_meta(self):
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="payload_id",
                    match=MatchValue(value="abc_0")
                )
            ]
        )
        self.vectordb.delete_by_meta("test_collection", query_filter=query_filter)
        assert self.vectordb.count("test_collection") == 1

    def test_run(self):
        test._test_upsert()
        test._test_search_by_vector()
        test._test_search_by_meta()
        test._test_delete_by_id()
        test._test_delete_by_meta()
        self.vectordb.client.delete_collection("test_collection")


if __name__ == "__main__":
    test = TestVectorDBAccessor()
    test.test_run()
