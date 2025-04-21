# Mock knowledge base - in a real implementation, this would come from files
mock_knowledge_base = {
    "middle_school_math_geometry": "Middle school geometry focuses on the properties and calculations of plane figures. Key topics include: properties of triangles and quadrilaterals, similar triangles, the Pythagorean theorem, etc.",
    "high_school_physics_mechanics": "High school mechanics includes Newton's laws of motion, work and energy, momentum, etc. Important formulas include F=ma, W=FS, E=mc², etc.",
    "elementary_literature_poetry": "Elementary poetry education focuses on understanding and reciting classical poems, including works by famous poets."
}

# Mock question database
mock_question_db = {
    "middle_school_math_geometry": {
        "easy": [
            {"question": "In a right triangle, if the two acute angles are complementary, what special type of triangle is it?", 
             "answer": "Isosceles right triangle"},
            {"question": "Do the diagonals of a parallelogram bisect each other?", 
             "answer": "Yes, the diagonals of a parallelogram bisect each other"},
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
    }
} 