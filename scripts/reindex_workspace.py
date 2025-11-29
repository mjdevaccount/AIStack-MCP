#!/usr/bin/env python3
"""
Quick workspace re-indexer for AIStack-MCP.
Run this to refresh the Qdrant vector index.
"""

import sys
from pathlib import Path
import requests
import uuid

# Configuration
WORKSPACE_PATH = Path(__file__).parent.parent.resolve()
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = f"workspace_{WORKSPACE_PATH.name.lower().replace(' ', '_')}"

print(f"=" * 60)
print("AIStack-MCP Workspace Reindexer")
print(f"=" * 60)
print(f"Workspace: {WORKSPACE_PATH}")
print(f"Collection: {COLLECTION_NAME}")
print(f"Ollama: {OLLAMA_URL}")
print(f"Qdrant: {QDRANT_URL}")
print()

# Check Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    
    qdrant = QdrantClient(url=QDRANT_URL)
    print(f"[OK] Connected to Qdrant")
except Exception as e:
    print(f"[FAIL] Qdrant connection failed: {e}")
    sys.exit(1)

# Ensure collection exists (recreate for clean index)
try:
    collections = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME in collections:
        qdrant.delete_collection(COLLECTION_NAME)
        print(f"[OK] Deleted existing collection: {COLLECTION_NAME}")
    
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )
    print(f"[OK] Created fresh collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"[FAIL] Collection setup error: {e}")
    sys.exit(1)

# Find files
extensions = [".py", ".js", ".ts", ".cs", ".md", ".ps1", ".json"]
ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "qdrant_storage", "test_env", ".cursor"}
files = []

for ext in extensions:
    for f in WORKSPACE_PATH.rglob(f"*{ext}"):
        if not any(p in f.parts for p in ignore_dirs):
            files.append(f)

files = files[:500]  # Limit for speed
print(f"[OK] Found {len(files)} files to index")
print()

# Embedding function
def embed_text(text: str) -> list:
    """Generate embedding using Ollama."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": "mxbai-embed-large", "prompt": text[:4000]},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"  Warning: Embedding failed - {e}")
        return [0.0] * 1024

# Index files
print("Indexing files...")
points = []
for i, file_path in enumerate(files):
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        rel_path = file_path.relative_to(WORKSPACE_PATH)
        
        # Chunk into 2000-char segments (max 5 chunks per file)
        chunks = []
        for j in range(0, min(len(content), 10000), 2000):
            chunk = content[j:j+2000]
            if chunk.strip():
                chunks.append(chunk)
        
        for idx, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "path": str(rel_path),
                    "chunk_index": idx,
                    "text": chunk[:500]
                }
            ))
        
        if (i + 1) % 25 == 0:
            print(f"  Processed {i + 1}/{len(files)} files ({len(points)} chunks)")
            
    except Exception as e:
        pass  # Skip files that can't be read

print(f"  Processed {len(files)}/{len(files)} files ({len(points)} chunks)")
print()

# Upload in batches
print(f"Uploading {len(points)} chunks to Qdrant...")
batch_size = 50
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=batch, wait=True)
    if (i + batch_size) % 200 == 0:
        print(f"  Uploaded {min(i + batch_size, len(points))}/{len(points)} chunks")

# Verify
info = qdrant.get_collection(COLLECTION_NAME)
print()
print(f"=" * 60)
print(f"[OK] INDEXING COMPLETE")
print(f"=" * 60)
print(f"Collection: {COLLECTION_NAME}")
print(f"Total vectors: {info.points_count}")
print(f"Files indexed: {len(files)}")
print()
print("You can now use semantic_search and other tools!")

