from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from sentence_transformers import SentenceTransformer
from books.models import Book

# from milvus import default_server
model=SentenceTransformer('sentence-transformers/msmarco-distilbert-base-dot-prod-v3')

def connect():
    connections.connect("default", host="127.0.0.1", port="19530")
    print(f"\n -- connected successfully")


def connect_collection():
    collection = Collection("books")
    return collection


def create_collection():
    fields = [
        FieldSchema(name="book_id", dtype=DataType.INT64, is_primary=True),
        FieldSchema(name="text_embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    ]

    schema = CollectionSchema(
        fields=fields,
        primary_field="book_id",
        description="A collection for storing book embeddings",
    )

    collection = Collection(name="books", schema=schema)

    print(f"\n -- Collection created")
    return collection


def drop_collection():
    connect()
    utility.drop_collection("books")
    print(f"\n -- Collection dropped")


def add_data(entities):
    connect()
    try:
        collection = Collection("books")
    except:
        create_collection()
        collection = Collection("books")
    print(entities)
    collection.insert(entities)
    collection.flush()
    print(f"\n -- New data added to collection")


def create_index():
    """
    Create an index for a collection in Milvus.

    Parameters:
    - collection (Collection): The collection object.

    Returns:
    - None
    """
    
    collection = Collection("books")
    collection.release()
    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128},
    }
    collection.create_index("text_embedding", index)
    print(f"\n -- Index created ")

    
def delete_rows(book_ids):
    connect()
    create_index("books")
    collection = Collection("books")
    collection.load()

    # Find the document IDs for the given book_ids
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }
    document_ids = []
    for book_id in book_ids:
        results = collection.search([book_id], "book_id", search_params, limit=1)
        if results and results[0].hits:
            document_ids.append(results[0].hits[0].id)

    # Delete the documents by their IDs
    expr = f"id in {document_ids}"
    status = collection.delete(expr)

    if status:
        print("Documents deleted successfully.")
    else:
        print(f"Failed to delete documents. Error: {status.message}")
        
        
def add_book_to_milvus(book):
    print(f"\n --Creating embeddings \n")
    que_embeddings = generate_bert_embeddings([book.description])[0]

    print(f"\n --Embeddings generated successfully \n")

    data = [
        [book.id],  # book_id
        [que_embeddings]  # text_embedding
    ]
    add_data(data)
    
    
def delete_book_from_milvus(book):
    delete_rows([book.id])
    
def generate_bert_embeddings(sentences):
    embeddings = []
    for sentence in sentences:
        embedding = model.encode(sentence).tolist()
        embeddings.append(embedding)
    return embeddings


def recommend_books(favorite_books, num_recommendations=5):
    connect()
    create_index()
    collection = connect_collection()

    # Load the collection
    collection.load()

    # Define the book_ids you want to skip
    skip_book_ids = [favorite_book for favorite_book in favorite_books]

    # Create the expression to filter out the skip_book_ids
    expr = f"book_id not in {skip_book_ids}"

    book_descriptions = Book.objects.filter(id__in=favorite_books).values_list('description', flat=True)
    search_vector = generate_bert_embeddings(book_descriptions)

    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }

    # Perform the search with a higher limit to ensure we have enough results to filter
    results = collection.search(
        data=search_vector,
        anns_field="text_embedding",
        param=search_params,
        limit=num_recommendations * 2,  # Increase the limit to get more results
        expr=expr,
        output_fields=["book_id"],
        consistency_level="Strong"
    )

    book_scores = {}

    # Aggregate results based on book_id
    for hits in results:
        for hit in hits:
            book_id = hit.entity.get('book_id')
            if book_id not in book_scores:
                book_scores[book_id] = hit.distance
            else:
                book_scores[book_id] = min(book_scores[book_id], hit.distance)  # Choose the closest match

    # Sort the books by their score (distance) and pick the top `num_recommendations`
    sorted_books = sorted(book_scores.items(), key=lambda item: item[1])[:num_recommendations]

    recommended_books = []
    for book_id, score in sorted_books:
        try:
            instance = Book.objects.get(id=book_id)
            recommended_books.append(instance)
        except Book.DoesNotExist:
            continue

    # Release the collection
    collection.release()
    return recommended_books
