from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams,PointStruct

client = QdrantClient(host='localhost', port=6333)

def create_collections(shape,collection_name):
    try:
        client.get_collection(collection_name)
    except:
        client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=shape, distance=Distance.DOT) )
    print(f"Collection '{collection_name}' CREATED.")
  

  

def upsert_post_vector(points): 
    operation_Info= client.upsert(
        collection_name="posts",
        points=points
    )
    print(f'status :{ operation_Info}')


        
def upsert_user_profile(points):
    operation_Info= client.upsert(
        collection_name="user_profiles",
        points=points
    )

    print(f'status :{ operation_Info}')
