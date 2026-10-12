"""
Learning roadmap service.
Generates structured learning roadmaps for each career.
"""

from typing import List, Dict


ROADMAPS: Dict[str, List[Dict]] = {
    'software_developer': [
        {'step': 1, 'topic': 'Python Fundamentals', 'explanation': 'Learn variables, data types, loops, functions, and error handling.', 'resource_type': 'Online course or textbook', 'duration': '3–4 weeks'},
        {'step': 2, 'topic': 'Data Structures & Algorithms', 'explanation': 'Study arrays, linked lists, stacks, queues, trees, and basic sorting algorithms.', 'resource_type': 'Online course + practice problems', 'duration': '4–6 weeks'},
        {'step': 3, 'topic': 'Object-Oriented Programming', 'explanation': 'Understand classes, inheritance, encapsulation, and polymorphism.', 'resource_type': 'Tutorial + mini-project', 'duration': '2–3 weeks'},
        {'step': 4, 'topic': 'SQL and Databases', 'explanation': 'Learn to design, query, and manage relational databases using SQL.', 'resource_type': 'Online course', 'duration': '2–3 weeks'},
        {'step': 5, 'topic': 'Git and GitHub', 'explanation': 'Learn version control, branching, pull requests, and collaborative workflows.', 'resource_type': 'Interactive tutorial', 'duration': '1–2 weeks'},
        {'step': 6, 'topic': 'REST API Development', 'explanation': 'Build and consume RESTful APIs using Flask or FastAPI.', 'resource_type': 'Project-based tutorial', 'duration': '3–4 weeks'},
        {'step': 7, 'topic': 'Testing and Debugging', 'explanation': 'Write unit tests, use debugging tools, and learn test-driven development basics.', 'resource_type': 'Documentation + practice', 'duration': '2 weeks'},
        {'step': 8, 'topic': 'Practical Projects', 'explanation': 'Build two or three portfolio projects that demonstrate your skills to employers.', 'resource_type': 'Self-directed projects', 'duration': '6–8 weeks'},
        {'step': 9, 'topic': 'Resume Preparation', 'explanation': 'Create a professional resume highlighting your projects and skills.', 'resource_type': 'Resume template + feedback', 'duration': '1 week'},
        {'step': 10, 'topic': 'Interview Practice', 'explanation': 'Practise common technical interview questions and coding challenges.', 'resource_type': 'Mock interviews + LeetCode', 'duration': 'Ongoing'},
    ],
    'data_analyst': [
        {'step': 1, 'topic': 'Python for Data Analysis', 'explanation': 'Learn Python basics with a focus on data manipulation using Pandas and NumPy.', 'resource_type': 'Online course', 'duration': '4–5 weeks'},
        {'step': 2, 'topic': 'SQL Fundamentals', 'explanation': 'Master SELECT queries, JOINs, aggregations, and subqueries.', 'resource_type': 'Interactive SQL course', 'duration': '2–3 weeks'},
        {'step': 3, 'topic': 'Statistics for Data Analysis', 'explanation': 'Study descriptive statistics, probability, distributions, and hypothesis testing.', 'resource_type': 'Textbook + online course', 'duration': '3–4 weeks'},
        {'step': 4, 'topic': 'Data Visualisation', 'explanation': 'Create effective charts and dashboards using Matplotlib, Seaborn, and Tableau or Power BI.', 'resource_type': 'Tutorial + projects', 'duration': '2–3 weeks'},
        {'step': 5, 'topic': 'Data Cleaning & Wrangling', 'explanation': 'Learn to handle missing data, outliers, and messy datasets systematically.', 'resource_type': 'Practice datasets', 'duration': '2 weeks'},
        {'step': 6, 'topic': 'Excel for Data Analysis', 'explanation': 'Master pivot tables, VLOOKUP, and advanced Excel functions used in business.', 'resource_type': 'Online course', 'duration': '1–2 weeks'},
        {'step': 7, 'topic': 'Analysis Projects', 'explanation': 'Complete two or three end-to-end data analysis projects using real datasets.', 'resource_type': 'Kaggle datasets + self-directed', 'duration': '6–8 weeks'},
        {'step': 8, 'topic': 'Resume and Portfolio', 'explanation': 'Document your analyses and build a professional data portfolio.', 'resource_type': 'Portfolio website + GitHub', 'duration': '1–2 weeks'},
        {'step': 9, 'topic': 'Interview Preparation', 'explanation': 'Practise SQL interview questions, case studies, and analytical reasoning problems.', 'resource_type': 'Mock interviews + practice problems', 'duration': 'Ongoing'},
    ],
    'ai_ml_engineer': [
        {'step': 1, 'topic': 'Python & Scientific Libraries', 'explanation': 'Master Python, NumPy, Pandas, and Matplotlib as the foundation for ML work.', 'resource_type': 'Online course', 'duration': '4–5 weeks'},
        {'step': 2, 'topic': 'Mathematics for ML', 'explanation': 'Study linear algebra, calculus, probability, and statistics relevant to machine learning.', 'resource_type': 'Textbook + online course', 'duration': '4–6 weeks'},
        {'step': 3, 'topic': 'Machine Learning Fundamentals', 'explanation': 'Learn supervised, unsupervised, and reinforcement learning concepts and algorithms.', 'resource_type': 'Online course (Andrew Ng recommended)', 'duration': '6–8 weeks'},
        {'step': 4, 'topic': 'Scikit-learn in Practice', 'explanation': 'Apply ML algorithms using Scikit-learn with real datasets and cross-validation.', 'resource_type': 'Project-based learning', 'duration': '3–4 weeks'},
        {'step': 5, 'topic': 'Deep Learning Fundamentals', 'explanation': 'Understand neural networks, backpropagation, CNNs, and RNNs.', 'resource_type': 'Deep learning course', 'duration': '6–8 weeks'},
        {'step': 6, 'topic': 'TensorFlow or PyTorch', 'explanation': 'Build and train deep learning models using a major framework.', 'resource_type': 'Framework tutorial + projects', 'duration': '4–5 weeks'},
        {'step': 7, 'topic': 'ML Projects', 'explanation': 'Build and document three or four ML projects for your portfolio.', 'resource_type': 'Kaggle competitions + self-directed', 'duration': '8–10 weeks'},
        {'step': 8, 'topic': 'MLOps Basics', 'explanation': 'Learn to deploy, monitor, and maintain ML models in production environments.', 'resource_type': 'Online course', 'duration': '3–4 weeks'},
        {'step': 9, 'topic': 'Interview Preparation', 'explanation': 'Practise ML theory questions, coding challenges, and case studies.', 'resource_type': 'Mock interviews + LeetCode ML track', 'duration': 'Ongoing'},
    ],
    'web_developer': [
        {'step': 1, 'topic': 'HTML5 & CSS3', 'explanation': 'Learn semantic HTML, CSS layout techniques (Flexbox, Grid), and responsive design.', 'resource_type': 'Interactive course', 'duration': '3–4 weeks'},
        {'step': 2, 'topic': 'JavaScript Fundamentals', 'explanation': 'Master variables, functions, DOM manipulation, events, and asynchronous JS.', 'resource_type': 'Online course', 'duration': '4–6 weeks'},
        {'step': 3, 'topic': 'Frontend Framework (React or Vue)', 'explanation': 'Learn component-based development with a modern JavaScript framework.', 'resource_type': 'Official docs + tutorial', 'duration': '5–6 weeks'},
        {'step': 4, 'topic': 'Backend Development (Flask or Node)', 'explanation': 'Build server-side applications, REST APIs, and handle authentication.', 'resource_type': 'Project-based course', 'duration': '4–5 weeks'},
        {'step': 5, 'topic': 'Databases (SQL & NoSQL)', 'explanation': 'Learn relational databases with SQL and an introduction to NoSQL options.', 'resource_type': 'Online course', 'duration': '2–3 weeks'},
        {'step': 6, 'topic': 'Git & Deployment', 'explanation': 'Use Git for version control and deploy applications to cloud platforms.', 'resource_type': 'Tutorial + practice', 'duration': '1–2 weeks'},
        {'step': 7, 'topic': 'Web Security Basics', 'explanation': 'Understand OWASP top 10, HTTPS, CSRF, XSS, and SQL injection prevention.', 'resource_type': 'Reading + practice', 'duration': '2 weeks'},
        {'step': 8, 'topic': 'Portfolio Projects', 'explanation': 'Build two or three full-stack web projects to showcase your abilities.', 'resource_type': 'Self-directed projects', 'duration': '6–8 weeks'},
        {'step': 9, 'topic': 'Interview Preparation', 'explanation': 'Practise HTML/CSS/JS interview questions and frontend coding challenges.', 'resource_type': 'Mock interviews + Frontend Mentor', 'duration': 'Ongoing'},
    ],
    'cybersecurity_analyst': [
        {'step': 1, 'topic': 'Networking Fundamentals', 'explanation': 'Learn TCP/IP, DNS, HTTP, firewalls, and network architecture.', 'resource_type': 'CompTIA Network+ study guide', 'duration': '4–6 weeks'},
        {'step': 2, 'topic': 'Linux Essentials', 'explanation': 'Develop competency in Linux command line, file systems, and system administration.', 'resource_type': 'Linux course + practice lab', 'duration': '3–4 weeks'},
        {'step': 3, 'topic': 'Python for Security', 'explanation': 'Use Python for scripting, automation, and basic security tools.', 'resource_type': 'Online course', 'duration': '3–4 weeks'},
        {'step': 4, 'topic': 'Security Fundamentals', 'explanation': 'Study CIA triad, cryptography, authentication, and common attack types.', 'resource_type': 'CompTIA Security+ materials', 'duration': '4–5 weeks'},
        {'step': 5, 'topic': 'Ethical Hacking Basics', 'explanation': 'Learn penetration testing methodology, vulnerability scanning, and tools like Nmap, Burp Suite.', 'resource_type': 'Ethical hacking course (TryHackMe, HackTheBox)', 'duration': '6–8 weeks'},
        {'step': 6, 'topic': 'SIEM & Incident Response', 'explanation': 'Understand security monitoring, log analysis, and incident response procedures.', 'resource_type': 'Online course + lab', 'duration': '3–4 weeks'},
        {'step': 7, 'topic': 'Security Certifications', 'explanation': 'Prepare for CompTIA Security+, CEH, or equivalent entry-level certification.', 'resource_type': 'Certification study guide', 'duration': '6–8 weeks'},
        {'step': 8, 'topic': 'Interview Preparation', 'explanation': 'Practise security scenario questions, explain your lab experience, and review CVE examples.', 'resource_type': 'Mock interviews + security forums', 'duration': 'Ongoing'},
    ],
    'cloud_engineer': [
        {'step': 1, 'topic': 'Cloud Fundamentals', 'explanation': 'Understand cloud computing concepts, service models (IaaS/PaaS/SaaS), and major providers.', 'resource_type': 'AWS Cloud Practitioner or Azure Fundamentals course', 'duration': '3–4 weeks'},
        {'step': 2, 'topic': 'Linux & Bash Scripting', 'explanation': 'Develop solid Linux skills and automate tasks with Bash scripts.', 'resource_type': 'Linux course + practice', 'duration': '3–4 weeks'},
        {'step': 3, 'topic': 'Networking for Cloud', 'explanation': 'Study VPCs, subnets, security groups, load balancers, and DNS.', 'resource_type': 'Cloud networking module', 'duration': '2–3 weeks'},
        {'step': 4, 'topic': 'Docker & Containers', 'explanation': 'Learn containerisation with Docker: images, containers, Dockerfile, and Docker Compose.', 'resource_type': 'Docker official docs + tutorial', 'duration': '2–3 weeks'},
        {'step': 5, 'topic': 'Kubernetes Orchestration', 'explanation': 'Deploy, scale, and manage containerised applications with Kubernetes.', 'resource_type': 'Kubernetes course', 'duration': '4–5 weeks'},
        {'step': 6, 'topic': 'Infrastructure as Code', 'explanation': 'Automate infrastructure provisioning with Terraform or AWS CloudFormation.', 'resource_type': 'IaC course + projects', 'duration': '3–4 weeks'},
        {'step': 7, 'topic': 'CI/CD Pipelines', 'explanation': 'Set up automated build, test, and deployment pipelines using GitHub Actions or Jenkins.', 'resource_type': 'Tutorial + practice', 'duration': '2–3 weeks'},
        {'step': 8, 'topic': 'Cloud Certification', 'explanation': 'Prepare for AWS Solutions Architect, Azure Administrator, or GCP Associate certification.', 'resource_type': 'Official certification course', 'duration': '6–8 weeks'},
        {'step': 9, 'topic': 'Interview Preparation', 'explanation': 'Practise cloud scenario questions, review architecture diagrams, and explain your projects.', 'resource_type': 'Mock interviews', 'duration': 'Ongoing'},
    ],
    'ui_ux_designer': [
        {'step': 1, 'topic': 'Design Principles', 'explanation': 'Study colour theory, typography, layout, visual hierarchy, and Gestalt principles.', 'resource_type': 'Online course + reading', 'duration': '2–3 weeks'},
        {'step': 2, 'topic': 'Figma or Adobe XD', 'explanation': 'Learn the industry-standard design tool for wireframing, prototyping, and collaboration.', 'resource_type': 'Official tutorial + practice', 'duration': '3–4 weeks'},
        {'step': 3, 'topic': 'User Research Methods', 'explanation': 'Conduct interviews, surveys, and usability tests to understand user needs.', 'resource_type': 'UX research course', 'duration': '2–3 weeks'},
        {'step': 4, 'topic': 'Wireframing & Information Architecture', 'explanation': 'Create low-fidelity wireframes and organise information logically.', 'resource_type': 'Project-based learning', 'duration': '2 weeks'},
        {'step': 5, 'topic': 'Prototyping & Usability Testing', 'explanation': 'Build interactive prototypes and test them with real users.', 'resource_type': 'Tutorial + user testing sessions', 'duration': '3–4 weeks'},
        {'step': 6, 'topic': 'HTML & CSS Basics', 'explanation': 'Learn enough front-end code to communicate effectively with developers.', 'resource_type': 'Basic web development course', 'duration': '2–3 weeks'},
        {'step': 7, 'topic': 'Design Portfolio', 'explanation': 'Create three to five case studies documenting your design process and outcomes.', 'resource_type': 'Portfolio website (Behance, personal site)', 'duration': '4–6 weeks'},
        {'step': 8, 'topic': 'Interview Preparation', 'explanation': 'Prepare to present your portfolio, discuss your design decisions, and critique existing products.', 'resource_type': 'Mock interviews + portfolio review', 'duration': 'Ongoing'},
    ],
    'digital_marketing': [
        {'step': 1, 'topic': 'Digital Marketing Fundamentals', 'explanation': 'Understand the digital marketing landscape: SEO, SEM, social media, email, and content.', 'resource_type': 'Google Digital Garage course (free)', 'duration': '2–3 weeks'},
        {'step': 2, 'topic': 'Search Engine Optimisation (SEO)', 'explanation': 'Learn on-page, off-page, and technical SEO to improve website visibility.', 'resource_type': 'SEO course + practice', 'duration': '3–4 weeks'},
        {'step': 3, 'topic': 'Google Analytics & Data', 'explanation': 'Set up and interpret web analytics to measure campaign performance.', 'resource_type': 'Google Analytics Academy (free)', 'duration': '2 weeks'},
        {'step': 4, 'topic': 'Social Media Marketing', 'explanation': 'Plan and execute organic and paid social media campaigns.', 'resource_type': 'Platform-specific courses', 'duration': '2–3 weeks'},
        {'step': 5, 'topic': 'Content Marketing', 'explanation': 'Create compelling content strategies and write effective copy.', 'resource_type': 'Content marketing course + practice', 'duration': '2–3 weeks'},
        {'step': 6, 'topic': 'Email Marketing', 'explanation': 'Design and run email campaigns using tools like Mailchimp.', 'resource_type': 'Email marketing course + practical project', 'duration': '1–2 weeks'},
        {'step': 7, 'topic': 'Paid Advertising (PPC)', 'explanation': 'Set up and optimise Google Ads and Meta Ads campaigns.', 'resource_type': 'Google Ads certification course', 'duration': '3–4 weeks'},
        {'step': 8, 'topic': 'Portfolio & Case Studies', 'explanation': 'Document your campaigns and create a marketing portfolio showing measurable results.', 'resource_type': 'Portfolio platform', 'duration': '2–3 weeks'},
        {'step': 9, 'topic': 'Interview Preparation', 'explanation': 'Prepare to discuss your campaigns, metrics, and strategic thinking.', 'resource_type': 'Mock interviews', 'duration': 'Ongoing'},
    ],
}


def get_roadmap(career_key: str) -> List[Dict]:
    """Return the learning roadmap for a given career key."""
    return ROADMAPS.get(career_key, [])


def get_all_roadmap_keys() -> List[str]:
    return list(ROADMAPS.keys())
