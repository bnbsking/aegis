from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from db_client.vector.qdrant import Point, VectorDBAccessor


class TestVectorDBAccessor:
    COLLECTION = "test_vector_db_accessor_coll"
    DIM = 4

    def __init__(self):
        # recreate=True both connects and (re)builds the collection, so no separate setup() is needed
        self.vba = VectorDBAccessor(
            collection_name_list=[self.COLLECTION],
            collection_dim=self.DIM,
            meta_indexing_field="category",
            host="172.17.0.1",
            recreate=True,
        )

    def teardown(self):
        self.vba.client.delete_collection(self.COLLECTION)
        self.vba.close()

    def test_count_empty(self):
        assert self.vba.count(self.COLLECTION) == 0
        assert self.vba.count_all()[self.COLLECTION] == 0

    def test_upsert_generates_ids_and_updates_count(self):
        vectors = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]
        payloads = [{"category": "a"}, {"category": "b"}, {"category": "a"}]
        self.ids = self.vba.upsert(self.COLLECTION, vectors, payloads)
        assert len(self.ids) == 3
        assert len(set(self.ids)) == 3
        assert self.vba.count(self.COLLECTION) == 3

    def test_upsert_with_explicit_id_updates_in_place(self):
        # re-upsert the first point reusing its id with a new payload - point count must not grow
        returned_ids = self.vba.upsert(
            self.COLLECTION, [[1.0, 0.0, 0.0, 0.0]], [{"category": "c"}], vector_id_list=[self.ids[0]]
        )
        assert returned_ids == [self.ids[0]]
        assert self.vba.count(self.COLLECTION) == 3

        results = self.vba.search(self.COLLECTION, vector=[1.0, 0.0, 0.0, 0.0], limit=1)
        assert results[0].vector_id == self.ids[0]
        assert results[0].payload == {"category": "c"}

        # restore payload so later category-based tests see the original data
        self.vba.upsert(self.COLLECTION, [[1.0, 0.0, 0.0, 0.0]], [{"category": "a"}], vector_id_list=[self.ids[0]])

    def test_search_by_vector_returns_nearest_first(self):
        results = self.vba.search(self.COLLECTION, vector=[1.0, 0.0, 0.0, 0.0], limit=3)
        assert all(isinstance(r, Point) for r in results)
        assert results[0].vector_id == self.ids[0]
        assert results[0].score >= results[1].score >= results[2].score

    def test_search_with_query_filter(self):
        query_filter = Filter(must=[FieldCondition(key="category", match=MatchValue(value="a"))])
        results = self.vba.search(self.COLLECTION, vector=[1.0, 0.0, 0.0, 0.0], query_filter=query_filter, limit=10)
        assert {r.vector_id for r in results} == {self.ids[0], self.ids[2]}

    def test_delete_by_id(self):
        self.vba.delete_by_id(self.COLLECTION, [self.ids[1]])
        assert self.vba.count(self.COLLECTION) == 2

    def test_delete_by_meta(self):
        query_filter = Filter(must=[FieldCondition(key="category", match=MatchValue(value="a"))])
        self.vba.delete_by_meta(self.COLLECTION, query_filter)
        assert self.vba.count(self.COLLECTION) == 0

    def test_upsert_rejects_mismatched_lengths(self):
        try:
            self.vba.upsert(self.COLLECTION, [[1.0, 0.0, 0.0, 0.0]], [{"a": 1}, {"b": 2}])
        except AssertionError:
            return
        raise AssertionError("expected upsert to reject mismatched vector_list/payload_list lengths")

    def test_upsert_rejects_out_of_range_length(self):
        assert self.vba.upsert(self.COLLECTION, [], []) == []


if __name__ == "__main__":
    obj = TestVectorDBAccessor()
    try:
        obj.test_count_empty()
        obj.test_upsert_generates_ids_and_updates_count()
        obj.test_upsert_with_explicit_id_updates_in_place()
        obj.test_search_by_vector_returns_nearest_first()
        obj.test_search_with_query_filter()
        obj.test_delete_by_id()
        obj.test_delete_by_meta()
        obj.test_upsert_rejects_mismatched_lengths()
        obj.test_upsert_rejects_out_of_range_length()
    finally:
        obj.teardown()

    print("all tests passed")
