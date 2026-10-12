"""
Interview preparation service.
Provides practice questions and feedback structures.
"""

from typing import List, Dict


INTERVIEW_QUESTIONS: Dict[str, Dict[str, List[str]]] = {
    'python': {
        'beginner': [
            "What is Python and why is it popular for software development?",
            "Explain the difference between a list and a tuple in Python.",
            "What is a function? Write a simple function that adds two numbers.",
            "What does the 'if __name__ == \"__main__\"' idiom mean in Python?",
            "What is the difference between '==' and 'is' in Python?",
            "Explain what a dictionary is and give an example of its use.",
            "What is a Python virtual environment and why is it useful?",
        ],
        'intermediate': [
            "Explain list comprehensions with an example.",
            "What are decorators in Python? Provide a practical example.",
            "Describe the difference between shallow and deep copy in Python.",
            "What is the Global Interpreter Lock (GIL) and how does it affect concurrency?",
            "Explain generators and the 'yield' keyword with an example.",
            "What are *args and **kwargs? When would you use them?",
            "Describe how exception handling works in Python. What is the difference between Exception and BaseException?",
        ],
        'advanced': [
            "Explain Python's memory management and garbage collection.",
            "Describe metaclasses in Python and a use case for them.",
            "What is the difference between multiprocessing and multithreading in Python?",
            "Explain context managers and the 'with' statement. How do you create a custom one?",
            "Describe common design patterns used in Python applications.",
            "What is asyncio and when should you use async/await?",
        ],
    },
    'sql': {
        'beginner': [
            "What is SQL and what is it used for?",
            "Explain the difference between SELECT, INSERT, UPDATE, and DELETE.",
            "What is a primary key? What is a foreign key?",
            "How do you filter results using the WHERE clause?",
            "What is the difference between INNER JOIN and LEFT JOIN?",
            "Explain what NULL means in SQL.",
        ],
        'intermediate': [
            "Explain GROUP BY and HAVING clauses with examples.",
            "What are subqueries? Provide an example.",
            "What is database normalisation and why is it important?",
            "Explain indexes in SQL. How do they improve performance?",
            "What is a transaction? Explain ACID properties.",
            "Describe the difference between UNION and UNION ALL.",
        ],
        'advanced': [
            "Explain window functions (ROW_NUMBER, RANK, LEAD, LAG) with examples.",
            "What are CTEs (Common Table Expressions) and how do they differ from subqueries?",
            "Describe query optimisation strategies.",
            "What is the difference between a clustered and non-clustered index?",
        ],
    },
    'data_structures': {
        'beginner': [
            "What is an array? How does it differ from a linked list?",
            "Explain what a stack is and describe a real-world use case.",
            "What is a queue? Describe the FIFO principle.",
            "What is Big O notation? Why is it important?",
            "Explain the difference between linear and binary search.",
        ],
        'intermediate': [
            "Explain binary trees and binary search trees.",
            "What is hashing? How do hash tables work?",
            "Describe the difference between a graph and a tree.",
            "Explain BFS and DFS traversal algorithms.",
            "What is dynamic programming? Give a simple example.",
        ],
        'advanced': [
            "Describe AVL trees and why they are self-balancing.",
            "Explain Dijkstra's algorithm for shortest path.",
            "What is the time complexity of common sorting algorithms?",
            "Describe the Floyd-Warshall algorithm.",
        ],
    },
    'web_development': {
        'beginner': [
            "What is the difference between HTML, CSS, and JavaScript?",
            "Explain the difference between GET and POST HTTP methods.",
            "What is responsive design? Why is it important?",
            "What is the DOM? How does JavaScript interact with it?",
            "What is CSS Flexbox? Give a practical example.",
        ],
        'intermediate': [
            "What is the difference between synchronous and asynchronous JavaScript?",
            "Explain REST APIs. What makes an API RESTful?",
            "What is CORS and why does it exist?",
            "Describe the difference between cookies, localStorage, and sessionStorage.",
            "What are HTTP status codes? Explain 200, 400, 401, 403, 404, 500.",
        ],
        'advanced': [
            "Explain the critical rendering path in web browsers.",
            "Describe common web security vulnerabilities (XSS, CSRF, SQL injection) and mitigations.",
            "What is WebSockets and how does it differ from HTTP?",
            "Describe microservices architecture versus monolithic architecture.",
        ],
    },
    'artificial_intelligence': {
        'beginner': [
            "What is artificial intelligence? How does it differ from traditional programming?",
            "Explain the difference between supervised and unsupervised learning.",
            "What is a neural network? Describe its basic components.",
            "What is overfitting? How can it be prevented?",
            "What is a training dataset and a test dataset?",
        ],
        'intermediate': [
            "Explain the bias-variance trade-off.",
            "What is gradient descent and how does it work?",
            "Describe convolutional neural networks (CNNs) and their typical use cases.",
            "What is transfer learning? When is it useful?",
            "Explain precision, recall, and F1 score in model evaluation.",
        ],
        'advanced': [
            "Describe transformer architecture and self-attention mechanisms.",
            "What is reinforcement learning? Explain the key components.",
            "Explain regularisation techniques (L1, L2, Dropout).",
            "What are generative adversarial networks (GANs)?",
        ],
    },
    'communication_skills': {
        'beginner': [
            "Tell me about yourself and your background.",
            "Why are you interested in this career field?",
            "Describe a challenge you faced and how you overcame it.",
            "What are your greatest strengths? Give an example for each.",
            "Where do you see yourself in three to five years?",
        ],
        'intermediate': [
            "Describe a time when you worked in a team to solve a difficult problem.",
            "How do you handle constructive criticism or negative feedback?",
            "Describe a situation where you had to explain a technical concept to a non-technical audience.",
            "How do you prioritise your work when managing multiple deadlines?",
            "Tell me about a project you are proud of and what you learned from it.",
        ],
        'advanced': [
            "How would you approach convincing senior stakeholders to adopt a new technology?",
            "Describe a time you led a team through an uncertain or difficult situation.",
            "How do you stay current with developments in your field?",
            "Describe a situation where you had to make a difficult decision with incomplete information.",
        ],
    },
}


def get_questions(topic: str, difficulty: str, career_role: str = '') -> List[str]:
    """Return practice interview questions for the given topic and difficulty."""
    topic_key = topic.lower().replace(' ', '_')
    diff_key = difficulty.lower()

    topic_questions = INTERVIEW_QUESTIONS.get(topic_key, {})
    questions = topic_questions.get(diff_key, topic_questions.get('beginner', []))

    if not questions:
        # Generic fallback
        questions = [
            f"Describe your experience with {topic}.",
            f"What do you consider the most important concept in {topic}?",
            f"How have you applied {topic} in a practical project or study?",
        ]

    return questions


def get_available_topics() -> List[str]:
    return list(INTERVIEW_QUESTIONS.keys())


def get_available_careers() -> List[str]:
    return [
        'Software Developer',
        'Data Analyst',
        'AI/ML Engineer',
        'Web Developer',
        'Cybersecurity Analyst',
        'Cloud Engineer',
        'UI/UX Designer',
        'Digital Marketing Specialist',
    ]
