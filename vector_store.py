import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema.document import Document
from logger import logger
from config import VECTOR_STORE_DIR, EMBEDDING_MODEL

# Initialize embedding function
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

class VectorStore:
    """Vector store implementation using ChromaDB."""
    
    def __init__(self):
        """Initialize the vector store."""
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        self.vector_store = Chroma(
            collection_name="education_content", 
            embedding_function=embeddings,
            persist_directory=VECTOR_STORE_DIR
        )
        logger.info(f"Vector store initialized with persistence directory: {VECTOR_STORE_DIR}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
        """
        logger.debug(f"Adding {len(documents)} documents to vector store")
        self.vector_store.add_documents(documents)
        self.vector_store.persist()
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        Search for documents similar to the query.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        logger.debug(f"Searching vector store for: {query}")
        results = self.vector_store.similarity_search(query, k=k)
        logger.debug(f"Found {len(results)} results for query: {query}")
        return results
    
    def search_by_metadata(self, 
                          grade: Optional[str] = None, 
                          subject: Optional[str] = None, 
                          topic: Optional[str] = None,
                          k: int = 3) -> List[Document]:
        """
        Search for documents by metadata filters.
        
        Args:
            grade: Grade level filter
            subject: Subject filter
            topic: Topic filter
            k: Number of results to return
            
        Returns:
            List of matching documents
        """
        # Create a dictionary for the filter
        filter_conditions = {}
        
        if grade:
            filter_conditions["grade"] = grade.lower()
        if subject:
            filter_conditions["subject"] = subject.lower()
        if topic:
            filter_conditions["topic"] = topic.lower()
        
        if filter_conditions:
            # Revert to using $and for multiple equality conditions if needed by the backend
            # Although Langchain docs often show simple dicts, the error suggests $and might be required.
            if len(filter_conditions) > 1:
                final_filter = {"$and": [{k: v} for k, v in filter_conditions.items()]}
            elif len(filter_conditions) == 1:
                # If only one condition, use a simple dictionary
                key, value = list(filter_conditions.items())[0]
                final_filter = {key: value}
            else: # Should not happen based on the if condition, but for safety
                final_filter = None 
                
            if final_filter:
                logger.debug(f"Searching vector store with metadata filter: {final_filter}")
            else:
                logger.warning("Filter conditions were present but final filter is None")
                # Fallback or handle error? For now, proceed to general search
                metadata_filter = None # Set to None to trigger else block below
                final_filter = None # Ensure it's None
        else:
            final_filter = None
        
        if final_filter:
            
            try:
                # Langchain Chroma's similarity_search uses the 'filter' argument
                results = self.vector_store.similarity_search(
                    query="",  # Empty query to match based on filters
                    k=k,
                    filter=final_filter
                )
                logger.debug(f"Found {len(results)} results with metadata filters")
                return results
            except Exception as e:
                logger.error(f"Error searching with metadata filter: {str(e)}")
                logger.info("Falling back to semantic search")
                # Fallback to regular search
                query = f"{grade or ''} {subject or ''} {topic or ''}".strip()
                return self.search(query, k=k)
        else:
            # If no filters, just return top documents
            logger.debug("No metadata filters provided, using general search")
            results = self.vector_store.similarity_search("education content", k=k)
            logger.debug(f"Found {len(results)} results with general search")
            return results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            count = self.vector_store._collection.count()
            return {"document_count": count}
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"document_count": 0, "error": str(e)}

# Create a singleton instance
vector_store = VectorStore() 