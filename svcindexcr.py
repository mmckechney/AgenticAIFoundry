import json
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from openai import AzureOpenAI

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration (replace with your own values)
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_API_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = "svcindex"
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_DEPLOYMENT_NAME = "text-embedding-3-large"

# Initialize Azure OpenAI client
openai_client = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version="2024-02-01"  # Use appropriate API version
)

# Generate embeddings using Azure OpenAI text-embedding-3-large
def generate_embedding(text):
    try:
        response = openai_client.embeddings.create(
            model=OPENAI_DEPLOYMENT_NAME,
            input=text
        )
        return response.data[0].embedding  # Returns 3072-dimensional vector
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 3072  # Fallback vector in case of error

# Read JSON file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['incidents']

# Transform JSON data into Azure AI Search documents
def transform_to_search_documents(incidents):
    documents = []
    for incident in incidents:
        # Combine fields for content
        interactions_text = ' '.join([interaction['comment'] for interaction in incident['interactions']])
        content = (
            f"{incident['short_description']} {incident['long_description']} "
            f"{incident['solution'] if incident['solution'] else ''} {interactions_text}"
        ).strip()

        # Create meta_json_string with additional fields
        meta_data = {
            "priority": incident['priority'],
            "status": incident['status'],
            "start_time": incident['start_time'],
            "end_time": incident['end_time'] if incident['end_time'] else "",
            "documents_used": incident['documents_used'],
            "interactions": incident['interactions']
        }
        meta_json_string = json.dumps(meta_data)

        # Prepare document
        document = {
            "id": incident['incident_id'],
            "content": content,
            "url": incident['documents_used'][0] if incident['documents_used'] else "",
            "filepath": "servicenow_incidents_full.json",
            "title": incident['short_description'],
            "meta_json_string": meta_json_string,
            "contentVector": generate_embedding(content)  # Generate vector for content
        }
        documents.append(document)
    return documents

# Define the search index schema with specified fields
def create_index_schema():
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="url", type=SearchFieldDataType.String),
        SimpleField(name="filepath", type=SearchFieldDataType.String),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SimpleField(name="meta_json_string", type=SearchFieldDataType.String),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=3072,  # text-embedding-3-large produces 3072-dimensional vectors
            vector_search_profile_name="my-vector-profile"
        )
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="my-hnsw",
                kind="hnsw",
                parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"}
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-hnsw"
            )
        ]
    )

    return SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)

# Create or update the index
def create_or_update_index(index_client):
    index = create_index_schema()
    index_client.create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' created or updated successfully.")

# Upload documents to the index
def upload_documents(search_client, documents):
    result = search_client.upload_documents(documents)
    print(f"Uploaded {len(result)} documents to the index.")

def main():
    # Initialize clients
    credential = AzureKeyCredential(SEARCH_API_KEY)
    index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)
    search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=credential)

    # Create or update index
    create_or_update_index(index_client)

    # Load and transform JSON data
    incidents = load_json_data("servicenow_incidents_full.json")
    documents = transform_to_search_documents(incidents)

    # Upload documents
    upload_documents(search_client, documents)

if __name__ == "__main__":
    main()