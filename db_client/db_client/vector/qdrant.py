from dataclasses import dataclass
import logging
from typing import Dict, List
import os
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointIdsList, VectorParams
from qdrant_client.models import FilterSelector


logger = logging.getLogger(__name__)


@dataclass
class Point:
    vector_id: str
    score: float
    payload: Dict


class VectorDBAccessor:
    def __init__(
            self,
            collection_name_list: List[str] = None,
            collection_dim: int = int(os.environ.get("QDRANT_DIM", 2560)),
            meta_indexing_field: str = "",
            host: str = "172.17.0.1",
            port: int = 6333,
            recreate: bool = False
        ):
        self.client = QdrantClient(host=host, port=port)
        current_collections = [coll.name for coll in self.client.get_collections().collections]
        for collection_name in collection_name_list or []:
            # delete
            if recreate and collection_name in current_collections:
                self.client.delete_collection(collection_name)
            # create
            if recreate or collection_name not in current_collections:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=collection_dim, distance="Cosine")
                )
                if meta_indexing_field:
                    self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name=meta_indexing_field,
                        field_schema="keyword",
                    )
    
    def count_all(self) -> Dict[str, int]:
        collection_list = [coll.name for coll in self.client.get_collections().collections]
        return {collection_name: self.client.get_collection(collection_name).points_count for collection_name in collection_list}

    def count(self, collection_name: str) -> int:
        return self.client.get_collection(collection_name).points_count

    def upsert(
            self,
            collection_name: str,
            vector_list: List[List[float]],
            payload_list: List[Dict],
            vector_id_list: List[str] = None
        ) -> List[str]:
        if not (1 <= len(vector_list) <= 10000):
            logger.error(f"Upsert length {len(vector_list)} not within 1 and 10000")
            return []
        assert len(vector_list) == len(payload_list), \
            f"len(vector_list) and len(payload_list) must have the same length, got {len(vector_list)} and {len(payload_list)}"

        if vector_id_list is None:
            vector_id_list = [str(uuid.uuid4()) for _ in vector_list]
        else:
            assert len(vector_list) == len(vector_id_list), \
                f"len(vector_list) and len(vector_id_list) must have the same length, got {len(vector_list)} and {len(vector_id_list)}"
        
        self.client.upsert(
            collection_name=collection_name,
            points=[
                {
                    "id": vector_id,
                    "vector": vector,
                    "payload": payload
                }
                for vector_id, vector, payload in zip(vector_id_list, vector_list, payload_list)
            ]
        )
        return vector_id_list

    def search(self, collection_name: str, vector: List[float] = None, query_filter = None, limit: int = 10) -> List[Point]:
        """Can use vecotr or query_filter or both"""
        outs = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            query_filter=query_filter,
            limit=limit
        ).points
        return [Point(vector_id=out.id, score=out.score, payload=out.payload) for out in outs]

    def delete_by_id(self, collection_name: str, vector_id_list: List[str]):
        """Vector id Must exist"""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=vector_id_list),
            )
        except:
            logger.error("Delete vector ID not found")
    
    def delete_by_meta(self, collection_name: str, query_filter):
        self.client.delete(
            collection_name=collection_name,
            points_selector=FilterSelector(filter=query_filter)
        )

    def close(self):
        self.client.close()
    