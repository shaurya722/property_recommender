import os
import google.genai as genai
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# === Init clients ===
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "property-recommendation"

# Get list of indexes
indexes = pc.list_indexes()
if indexes and INDEX_NAME not in indexes.names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

# === Utils ===
def get_embedding(text: str):
    response = client.models.embed_content(
        model='text-embedding-004',
        contents=text,
    )
    return response.embeddings[0].values

def add_property_to_index(prop):
    emb = get_embedding(prop["description"])
    index.upsert([(str(prop["id"]), emb, prop)])

def search_properties_in_index(query, filters=None):
    try:
        print(f"Searching with query: {query}")
        emb = get_embedding(query)
        print(f"Got embedding: {emb[:5]}...")  # Print first few values of embedding
        results = index.query(vector=emb, top_k=5, include_metadata=True, filter=filters or {})
        print(f"Raw results: {results}")
        
        if not results:
            print("No results returned from Pinecone")
            return {"matches": []}
            
        if not results.get('matches'):
            print("No matches found in results")
            return {"matches": []}
            
        # Clean up the matches to include metadata and score
        cleaned_matches = []
        for match in results['matches']:
            if match and match.get('metadata'):
                # Add the similarity score to the metadata
                match_data = match['metadata'].copy()
                match_data['similarity_score'] = match['score']
                cleaned_matches.append(match_data)
        
        return {"matches": cleaned_matches}
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        print(f"Exception type: {type(e)}")
        return {"matches": []}

def recommend_from_profile(profile):
    try:
        print(f"Generating recommendation for profile: {profile}")
        profile_text = f"{profile['married_status']} user with salary {profile['salary']}, prefers {profile['bhk']}BHK in {profile['location']}"
        print(f"Profile text: {profile_text}")
        emb = get_embedding(profile_text)
        
        results = index.query(vector=emb, top_k=5, include_metadata=True)
        print(f"Recommendation results: {results}")
        
        if not results:
            print("No recommendations returned from Pinecone")
            return {"matches": []}
            
        if not results.get('matches'):
            print("No matches found in recommendations")
            return {"matches": []}
            
        # Clean up the matches to include metadata and score
        cleaned_matches = []
        for match in results['matches']:
            if match and match.get('metadata'):
                match_data = match['metadata'].copy()
                match_data['similarity_score'] = match['score']
                cleaned_matches.append(match_data)
        
        return {"matches": cleaned_matches}
        
    except Exception as e:
        print(f"Error in recommendation: {str(e)}")
        print(f"Exception type: {type(e)}")
        return {"matches": []}
