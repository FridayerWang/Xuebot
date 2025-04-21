from langchain.schema.document import Document
from logger import logger
import os
from config import USE_VECTOR_STORE

# Mock knowledge base - in a real implementation, this would come from files
mock_knowledge_base = {
    "middle_school_math_geometry": "Middle school geometry focuses on the properties and calculations of plane figures. Key topics include: properties of triangles and quadrilaterals, similar triangles, the Pythagorean theorem, etc.",
    "high_school_physics_mechanics": "High school mechanics includes Newton's laws of motion, work and energy, momentum, etc. Important formulas include F=ma, W=FS, E=mc², etc.",
    "elementary_literature_poetry": "Elementary poetry education focuses on understanding and reciting classical poems, including works by famous poets.",
    
    # New entries
    "elementary_math_addition": "Elementary addition focuses on combining numbers to find their sum. Key concepts include place value, carrying digits, and number bonds. Students learn to add single and multi-digit numbers using methods like counting on, making tens, and column addition.",
    
    "elementary_math_subtraction": "Elementary subtraction covers taking away or finding the difference between numbers. Important concepts include borrowing, place value, and inverse operations. Students learn strategies like counting back, using number lines, and the column method.",
    
    "middle_school_science_cells": "Middle school cell biology introduces the basic unit of life. Topics include cell structure, differences between plant and animal cells, cell functions, and organelles such as the nucleus, mitochondria, and chloroplasts. Students learn about cell division and how cells work together in tissues.",
    
    "middle_school_english_grammar": "Middle school grammar covers sentence structure, parts of speech, and proper usage. Students learn about subjects, predicates, clauses, phrases, and the eight parts of speech: nouns, pronouns, verbs, adjectives, adverbs, prepositions, conjunctions, and interjections.",
    
    "high_school_biology_genetics": "High school genetics explores inheritance patterns and DNA. Topics include Mendelian genetics, dominant and recessive traits, punnett squares, DNA structure and replication, protein synthesis, genetic mutations, and genetic engineering applications.",
    
    "high_school_chemistry_periodic_table": "High school chemistry covers the periodic table organization and element properties. Students learn about atomic number, mass number, electron configuration, periodic trends including electronegativity, atomic radius, and ionization energy, and how these properties influence chemical behavior.",
    
    "high_school_math_algebra": "High school algebra focuses on using variables to represent unknown quantities and solve equations. Topics include linear equations, quadratic equations, functions, inequalities, polynomials, rational expressions, exponents, radicals, and systems of equations.",
    
    "high_school_literature_shakespeare": "High school Shakespeare studies examine the works of William Shakespeare, including his plays and sonnets. Students analyze his language, themes, character development, historical context, and cultural significance. Common plays studied include Romeo and Juliet, Macbeth, Hamlet, and A Midsummer Night's Dream.",
    
    "college_calculus_limits": "College calculus on limits explores the behavior of functions as they approach specific values. Students learn about one-sided limits, continuity, infinite limits, indeterminate forms, and using limits to define derivatives. Key concepts include the epsilon-delta definition and techniques for evaluating various types of limits.",
    
    "college_physics_electromagnetism": "College electromagnetism covers electric and magnetic fields and their interactions. Key topics include Coulomb's law, Gauss's law, electric potential, capacitance, current, resistance, magnetic fields, Ampere's law, Faraday's law of induction, and Maxwell's equations."
}

# Mock question database
mock_question_db = {
    "middle_school_math_geometry": {
        "easy": [
            {"question": "In a right triangle, if the two acute angles are complementary, what special type of triangle is it?", 
             "answer": "Isosceles right triangle"},
            {"question": "Do the diagonals of a parallelogram bisect each other?", 
             "answer": "Yes, the diagonals of a parallelogram bisect each other"},
            {"question": "What is the name for a polygon with 5 sides?",
             "answer": "A pentagon"},
            {"question": "What is the sum of the interior angles of a triangle?",
             "answer": "180 degrees"},
            {"question": "What do you call two lines in the same plane that never intersect?",
             "answer": "Parallel lines"},
            {"question": "What is the formula for the area of a rectangle?",
             "answer": "Area = length × width"},
            {"question": "How many degrees are in a right angle?",
             "answer": "90 degrees"}
        ],
        "medium": [
            {"question": "If the diagonals of a quadrilateral perpendicularly bisect each other, what is this quadrilateral?", 
             "answer": "Rhombus"},
            {"question": "In triangle ABC, angle C=90°, AB=5, AC=3, find the length of BC.", 
             "answer": "4, using the Pythagorean theorem BC²=AB²-AC²=25-9=16, so BC=4"},
        ],
        "hard": [
            {"question": "Prove: The distances from the incenter of a triangle to its sides are proportional to the sides.", 
             "answer": "This can be proven using the area formula S=1/2×perimeter×inradius"},
        ]
    },
    
    # Adding more questions for existing and new topics
    "high_school_math_algebra": {
        "easy": [
            {"question": "Solve for x: 2x + 3 = 11", 
             "answer": "x = 4, because 2x + 3 = 11 implies 2x = 8, which gives x = 4"},
            {"question": "Factor the expression: x² - 9", 
             "answer": "(x + 3)(x - 3), which is a difference of squares"},
        ],
        "medium": [
            {"question": "Solve the quadratic equation: x² - 5x + 6 = 0", 
             "answer": "x = 2 or x = 3, using factoring: (x - 2)(x - 3) = 0"},
            {"question": "Find the domain of f(x) = √(x - 2)", 
             "answer": "The domain is x ≥ 2, because the expression under the square root must be non-negative"},
        ],
        "hard": [
            {"question": "Solve the system of equations: 2x + y = 5 and 3x - 2y = 4", 
             "answer": "x = 2, y = 1. Multiply the first equation by 2 to get 4x + 2y = 10, then add to the second equation to get 7x = 14, so x = 2. Substitute back to find y = 1."},
        ]
    },
    
    "high_school_biology_genetics": {
        "easy": [
            {"question": "What are the four nitrogenous bases in DNA?", 
             "answer": "Adenine (A), Thymine (T), Guanine (G), and Cytosine (C)"},
            {"question": "What is a genotype?", 
             "answer": "A genotype is the genetic makeup of an organism, represented by the combination of alleles it possesses for a particular trait."},
        ],
        "medium": [
            {"question": "If a homozygous dominant parent (BB) is crossed with a heterozygous parent (Bb), what percentage of offspring will show the dominant phenotype?", 
             "answer": "100% of offspring will show the dominant phenotype, because all offspring will have at least one dominant allele (either BB or Bb)."},
            {"question": "Explain the difference between incomplete dominance and codominance.", 
             "answer": "In incomplete dominance, the heterozygous phenotype is an intermediate blend of both homozygous phenotypes. In codominance, both alleles are fully expressed in the heterozygote, resulting in a phenotype that shows both traits distinctly rather than a blend."},
        ],
        "hard": [
            {"question": "A man with type A blood and a woman with type B blood have a child with type O blood. Explain how this is possible genetically.", 
             "answer": "This is possible if both parents are heterozygous (AO and BO). The man has genotype AO (phenotype A), the woman has genotype BO (phenotype B), and their child inherited the O allele from each parent, resulting in genotype OO (phenotype O)."},
        ]
    },
    
    "elementary_math_addition": {
        "easy": [
            {"question": "What is 25 + 13?", 
             "answer": "38"},
            {"question": "If you have 7 apples and get 5 more, how many do you have in total?", 
             "answer": "12 apples"},
        ],
        "medium": [
            {"question": "Add: 167 + 285", 
             "answer": "452"},
            {"question": "What is the sum of 1/4 and 2/4?", 
             "answer": "3/4 or 0.75"},
        ],
        "hard": [
            {"question": "A store sold 128 toys on Saturday and 157 toys on Sunday. How many toys did they sell altogether over the weekend?", 
             "answer": "285 toys (128 + 157 = 285)"},
        ]
    }
}

def initialize_vector_store():
    """
    Initialize the vector store with documents from the mock knowledge base
    AND the mock question database.
    This operation converts the mock data to Document objects
    and adds them to the Chroma vector store.
    """
    try:
        from vector_store import vector_store
        from langchain.schema.document import Document
        
        documents = []
        logger.info("Processing mock knowledge base for vector store")
        content_count = 0
        for key, content in mock_knowledge_base.items():
            # Parse the key to extract grade, subject, and topic
            parts = key.split('_')
            if len(parts) >= 3:
                grade = parts[0]
                subject = parts[1]
                topic = '_'.join(parts[2:])  # In case topic has underscores
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "grade": grade,
                        "subject": subject,
                        "topic": topic,
                        "source": "mock_data",
                        "type": "content" # Mark as content type
                    }
                )
                documents.append(doc)
                content_count += 1
                logger.debug(f"Created content document for {key} with metadata: {doc.metadata}")
            else:
                logger.warning(f"Skipping invalid key format for content: {key}")
        logger.info(f"Created {content_count} content documents")

        # Convert mock question database to Document objects
        logger.info("Processing mock question database for vector store")
        question_count = 0
        for topic_key, difficulties in mock_question_db.items():
            # Try to parse grade/subject from topic_key for questions too
            topic_parts = topic_key.split('_')
            q_grade, q_subject, q_topic = None, None, topic_key # Defaults
            if len(topic_parts) >= 3:
                q_grade = topic_parts[0]
                q_subject = topic_parts[1]
                q_topic = '_'.join(topic_parts[2:])
            
            for difficulty, questions in difficulties.items():
                for question_data in questions:
                    question_text = question_data.get("question")
                    answer_text = question_data.get("answer")
                    
                    if question_text and answer_text:
                        metadata = {
                            "type": "question", # Mark as question type
                            "topic": q_topic, 
                            "difficulty": difficulty.lower(), # Ensure lowercase
                            "answer": answer_text,
                            "source": "mock_questions"
                        }
                        if q_grade:
                             metadata["grade"] = q_grade
                        if q_subject:
                             metadata["subject"] = q_subject
                        
                        doc = Document(
                            page_content=question_text,
                            metadata=metadata
                        )
                        documents.append(doc)
                        question_count += 1
                        # Limit logging verbosity for questions
                        # logger.debug(f"Created question document for {topic_key}/{difficulty} with metadata: {doc.metadata}")
                    else:
                        logger.warning(f"Skipping question due to missing text or answer in {topic_key}/{difficulty}")
        logger.info(f"Created {question_count} question documents")

        # Check if the total number of documents matches existing count to avoid re-adding
        # This simple check might not be robust if only partial updates are desired
        stats = vector_store.get_collection_stats()
        if stats.get("document_count", 0) == len(documents):
            logger.info(f"Vector store already contains {stats['document_count']} documents. Skipping initialization.")
            return True
        elif stats.get("document_count", 0) > 0:
             logger.warning(f"Vector store contains {stats['document_count']} documents, but expected {len(documents)}. Consider running reinitialize script to clear first.")
             # Decide whether to proceed or stop. For now, let's proceed to add.
             pass # Or return False if strict matching is required

        # Add documents to vector store
        if documents:
            try:
                # We should clear the store before adding if the counts don't match
                # or if re-initialization is explicitly desired. 
                # The reinitialize_vector_store.py script handles clearing.
                logger.info(f"Adding {len(documents)} total documents (content & questions) to vector store")
                vector_store.add_documents(documents)
                logger.info(f"Successfully added/updated documents in vector store")
                
                # Verify documents were added
                new_stats = vector_store.get_collection_stats()
                logger.info(f"Vector store now contains {new_stats.get('document_count', 0)} documents")
            except Exception as e:
                logger.error(f"Error adding documents to vector store: {str(e)}")
                return False
        else:
            logger.warning("No documents created for vector store")
            
        return True
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        return False

# Initialize the vector store when this module is imported
# This will only happen if the vector_store module is available
# Note: Re-running the app might not re-trigger this if store already exists.
# Use reinitialize_vector_store.py for a clean update.
if USE_VECTOR_STORE:
    try:
        # Attempt to initialize the vector store
        logger.info("Attempting to initialize vector store with data")
        initialize_vector_store()
    except ImportError:
        logger.warning("Vector store module not available, using mock data only") 