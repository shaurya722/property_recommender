import os
import google.genai as genai
import pinecone
from dotenv import load_dotenv

load_dotenv()

# === Setup ===
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# , environment=os.getenv("PINECONE_ENV")
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "property-recommendation"

# Adjust the cloud and region as per your Pinecone project setup
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
       spec=ServerlessSpec(
    cloud="aws",
    region="us-east-1"
)
    )

index = pc.Index(INDEX_NAME)

# === Embedding ===
def get_embedding(text):
    response = client.models.embed_content(
        model='text-embedding-004',
        contents=text,
    )
    return response.embeddings[0].values

# === Dynamic Property Indexing ===
def add_property(prop):
    emb = get_embedding(prop["description"])
    index.upsert([(prop["id"], emb, prop)])
    print(f"✅ Indexed: {prop['id']} - {prop['description']}")

# === Initial Properties ===
initial_properties = [
    {
        "id": "prop1",
        "description": "2BHK flat in Bangalore near IT park, 35k rent, gym and parking included",
        "location": "Bangalore", "bhk": 2, "price": 35000
    },
    {
        "id": "prop2",
        "description": "1BHK apartment in Pune for working professionals, 20k monthly rent",
        "location": "Pune", "bhk": 1, "price": 20000
    },
    {
        "id": "prop3",
        "description": "3BHK luxurious flat in Hyderabad with swimming pool, 65k rent",
        "location": "Hyderabad", "bhk": 3, "price": 65000
    },
    {
        "id": "prop4",
        "description": "Affordable 2BHK in Delhi, 25k monthly, family-friendly area with park",
        "location": "Delhi", "bhk": 2, "price": 25000
    },
    {
        "id": "prop5",
        "description": "Studio apartment in Mumbai near beach, 30k rent, best for bachelors",
        "location": "Mumbai", "bhk": 1, "price": 30000
    },
    {
        "id": "prop6",
        "description": "Fully furnished 2BHK in Noida with gym and balcony, 28k",
        "location": "Noida", "bhk": 2, "price": 28000
    },
    {
        "id": "prop7",
        "description": "1RK in Bangalore for students, near metro station, rent 12k",
        "location": "Bangalore", "bhk": 1, "price": 12000
    },
]

def index_all_properties():
    for prop in initial_properties:
        add_property(prop)

# === Smart Search ===
def search_properties(query, filters=None):
    query_emb = get_embedding(query)
    results = index.query(vector=query_emb, top_k=5, include_metadata=True, filter=filters or {})
    print("\n🔍 Search Results:")
    for match in results['matches']:
        print(f"- {match['metadata']['description']} (Score: {match['score']:.4f})")

# === Recommendations ===
def recommend_properties(user_profile):
    profile_text = f"{user_profile['married_status']} user with salary {user_profile['salary']}, prefers {user_profile['bhk']}BHK in {user_profile['location']}"
    profile_emb = get_embedding(profile_text)
    results = index.query(vector=profile_emb, top_k=5, include_metadata=True)
    print("\n🤖 Recommended Properties:")
    for match in results['matches']:
        print(f"- {match['metadata']['description']} (Score: {match['score']:.4f})")

# === Main ===
if __name__ == "__main__":
    print("🏗️ Indexing properties...")
    index_all_properties()

    # 🔍 Test 1: User query search
    user_query = "cheap 2BHK in Bangalore "
    search_properties(user_query)

    # 🤖 Test 2: Recommendation based on profile
    user_info = {
        "salary": 30000,
        "married_status": "unmarried",
        "bhk": 2,
        "location": "Bangalore"
    }
    recommend_properties(user_info)

    # 🆕 Add new property dynamically
    new_prop = {
        "id": "prop8",
        "description": "Budget 2BHK in Bangalore Whitefield, 29k, balcony and park nearby",
        "location": "Bangalore", "bhk": 2, "price": 29000
    }
    add_property(new_prop)

    # 🔁 Re-run search after dynamic insert
    print("\n🔁 Rechecking search after adding new property:")
    search_properties(user_query)
