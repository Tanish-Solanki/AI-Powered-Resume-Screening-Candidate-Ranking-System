"""
Evaluation Dataset Generator for Resume Ranking System.

Since the project stores data in PostgreSQL (via Candidate and JobDescription models)
and no seed/sample data exists in the repository, this script creates a realistic
evaluation dataset directly from synthetic but domain-accurate resume and JD texts.

The generated resumes and JDs are crafted to produce a realistic distribution of
relevance levels when matched by the ranking engine's scoring formula:
    Final Score = 50% Semantic Similarity + 30% Skill Match + 20% Experience Score

Each resume is written to realistically represent a candidate profile with varying
degrees of fitness for each job description. Suggested relevance labels are computed
using a rule-based heuristic (skill overlap + domain match) and marked REVIEW_REQUIRED.

Usage:
    cd backend
    python -m evaluation.generate_dataset
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


# ============================================================================
# Realistic Job Descriptions (3 diverse roles)
# ============================================================================

JOB_DESCRIPTIONS = [
    {
        "job_id": "jd_backend_python",
        "job_title": "Senior Backend Python Developer",
        "job_description_text": (
            "We are hiring a Senior Backend Python Developer to join our engineering team. "
            "The ideal candidate has 4+ years of experience building scalable REST APIs and "
            "microservices using Python. You will design and implement high-throughput backend "
            "services, optimize database queries, and collaborate with frontend teams.\n\n"
            "Required Skills:\n"
            "- Python (advanced), FastAPI or Django\n"
            "- PostgreSQL, Redis\n"
            "- Docker, Kubernetes\n"
            "- REST API design, microservices architecture\n"
            "- Git, CI/CD pipelines (Jenkins/GitHub Actions)\n"
            "- Unit testing with pytest\n\n"
            "Nice to Have:\n"
            "- AWS (EC2, S3, Lambda)\n"
            "- Message queues (RabbitMQ, Kafka)\n"
            "- GraphQL\n"
            "- Experience with agile/scrum methodologies\n\n"
            "Experience: 4+ years in backend software development."
        ),
        "required_skills": [
            "python", "fastapi", "django", "postgresql", "redis",
            "docker", "kubernetes", "git", "jenkins"
        ],
        "experience_requirements": "4+ years of backend development experience with Python web frameworks and microservices"
    },
    {
        "job_id": "jd_data_scientist",
        "job_title": "Data Scientist - NLP & Machine Learning",
        "job_description_text": (
            "We are seeking a Data Scientist specializing in Natural Language Processing and "
            "Machine Learning to join our AI team. You will develop and deploy ML models for "
            "text classification, entity extraction, and semantic similarity tasks. You will "
            "work closely with engineering to productionize models.\n\n"
            "Required Skills:\n"
            "- Python, scikit-learn, pandas, numpy\n"
            "- NLP: SpaCy, NLTK, Hugging Face Transformers\n"
            "- Deep Learning: PyTorch or TensorFlow\n"
            "- Machine Learning: classification, clustering, regression\n"
            "- Data visualization: matplotlib, seaborn\n"
            "- SQL for data extraction\n\n"
            "Nice to Have:\n"
            "- MLOps (MLflow, Weights & Biases)\n"
            "- Cloud deployment (AWS SageMaker, GCP Vertex AI)\n"
            "- Experience with large language models (LLMs)\n"
            "- Published research or Kaggle competition experience\n\n"
            "Experience: 3+ years in data science or applied ML roles."
        ),
        "required_skills": [
            "python", "scikit-learn", "pandas", "numpy", "nlp",
            "pytorch", "tensorflow", "machine learning", "deep learning",
            "matplotlib", "sql"
        ],
        "experience_requirements": "3+ years in data science, NLP, or applied machine learning"
    },
    {
        "job_id": "jd_fullstack_react",
        "job_title": "Full Stack Developer (React + Node.js)",
        "job_description_text": (
            "We are looking for a Full Stack Developer proficient in React.js and Node.js "
            "to build modern, responsive web applications. You will own features end-to-end, "
            "from UI design implementation to API development and database management.\n\n"
            "Required Skills:\n"
            "- JavaScript/TypeScript (advanced)\n"
            "- React.js, Redux or Context API\n"
            "- Node.js, Express.js\n"
            "- MongoDB or PostgreSQL\n"
            "- HTML5, CSS3, responsive design\n"
            "- Git version control\n\n"
            "Nice to Have:\n"
            "- Next.js or Gatsby\n"
            "- GraphQL, Apollo\n"
            "- AWS or Azure deployment\n"
            "- Docker containerization\n"
            "- Agile/Scrum experience\n\n"
            "Experience: 2+ years building production web applications."
        ),
        "required_skills": [
            "javascript", "typescript", "react", "angular", "vue",
            "mongodb", "postgresql", "git", "docker"
        ],
        "experience_requirements": "2+ years of full stack web development with modern JavaScript frameworks"
    }
]


# ============================================================================
# Realistic Resume Texts (10 diverse candidates)
# ============================================================================

RESUMES = [
    {
        "candidate_id": "resume_arjun_mehta",
        "candidate_name": "Arjun Mehta",
        "resume_text": (
            "Arjun Mehta\n"
            "Email: arjun.mehta@email.com | Phone: +91-9876543210 | LinkedIn: linkedin.com/in/arjunmehta\n\n"
            "Summary\n"
            "Senior Backend Developer with 5 years of experience building high-performance REST APIs "
            "and microservices using Python, FastAPI, and Django. Strong expertise in PostgreSQL "
            "optimization, Docker containerization, and CI/CD automation.\n\n"
            "Technical Skills\n"
            "Languages: Python, SQL, Bash\n"
            "Frameworks: FastAPI, Django, Flask, Celery\n"
            "Databases: PostgreSQL, Redis, MongoDB\n"
            "DevOps: Docker, Kubernetes, Jenkins, GitHub Actions\n"
            "Cloud: AWS (EC2, S3, Lambda, RDS)\n"
            "Testing: pytest, unittest, Postman\n"
            "Tools: Git, Jira, Confluence\n\n"
            "Experience\n"
            "Senior Backend Developer | TechCorp Solutions | Jan 2021 - Present\n"
            "- Architected and deployed 12 microservices serving 50K+ daily active users using FastAPI and PostgreSQL\n"
            "- Reduced API response time by 40% through query optimization and Redis caching layer implementation\n"
            "- Implemented CI/CD pipelines with Jenkins and GitHub Actions, reducing deployment time from 2 hours to 15 minutes\n"
            "- Designed event-driven architecture using RabbitMQ for async processing of batch operations\n"
            "- Mentored team of 4 junior developers on Python best practices and code review standards\n\n"
            "Backend Developer | DataFlow Inc | Jun 2019 - Dec 2020\n"
            "- Built RESTful APIs with Django REST Framework serving internal analytics dashboard\n"
            "- Managed PostgreSQL database with 10M+ records, implemented partitioning and indexing strategies\n"
            "- Containerized applications using Docker and orchestrated with Kubernetes on AWS EKS\n"
            "- Wrote comprehensive test suites achieving 92% code coverage with pytest\n\n"
            "Education\n"
            "B.Tech in Computer Science | IIT Delhi | 2015-2019 | GPA: 8.7/10\n"
        )
    },
    {
        "candidate_id": "resume_priya_sharma",
        "candidate_name": "Priya Sharma",
        "resume_text": (
            "Priya Sharma\n"
            "Email: priya.sharma@email.com | Phone: +91-9123456789\n\n"
            "Summary\n"
            "Data Scientist with 4 years of experience in NLP, machine learning, and deep learning. "
            "Specialized in building text classification, named entity recognition, and semantic similarity "
            "models using PyTorch and Hugging Face Transformers. Published researcher in computational linguistics.\n\n"
            "Technical Skills\n"
            "Languages: Python, R, SQL\n"
            "ML/DL: scikit-learn, PyTorch, TensorFlow, Keras\n"
            "NLP: SpaCy, NLTK, Hugging Face Transformers, Sentence-BERT\n"
            "Data: pandas, numpy, matplotlib, seaborn, Plotly\n"
            "MLOps: MLflow, Weights & Biases, Docker\n"
            "Cloud: AWS SageMaker, GCP Vertex AI\n"
            "Databases: PostgreSQL, BigQuery\n\n"
            "Experience\n"
            "Senior Data Scientist | AI Research Labs | Mar 2022 - Present\n"
            "- Developed transformer-based NER model achieving 94% F1-score for resume skill extraction\n"
            "- Built semantic search engine using Sentence-BERT embeddings and FAISS for 100K+ document corpus\n"
            "- Deployed ML models as REST APIs using FastAPI and Docker on AWS SageMaker\n"
            "- Led team of 3 data scientists on multi-label text classification project for customer support automation\n\n"
            "Data Scientist | DataMinds Consulting | Jul 2020 - Feb 2022\n"
            "- Built sentiment analysis pipeline processing 50K+ reviews daily using SpaCy and scikit-learn\n"
            "- Implemented topic modeling with LDA and BERT embeddings for market research insights\n"
            "- Created interactive dashboards with Plotly and Streamlit for stakeholder reporting\n"
            "- Optimized feature engineering pipeline reducing training time by 60%\n\n"
            "Education\n"
            "M.Tech in AI & Machine Learning | IIIT Hyderabad | 2018-2020 | GPA: 9.2/10\n"
            "B.Tech in Computer Science | NIT Warangal | 2014-2018 | GPA: 8.5/10\n\n"
            "Publications\n"
            "- 'Cross-lingual Transfer Learning for Low-Resource NER' - ACL 2023 Workshop\n"
            "- 'Efficient Fine-tuning of Sentence Transformers for Domain Adaptation' - EMNLP 2022\n"
        )
    },
    {
        "candidate_id": "resume_rahul_kumar",
        "candidate_name": "Rahul Kumar",
        "resume_text": (
            "Rahul Kumar\n"
            "Email: rahul.kumar@email.com | GitHub: github.com/rahulk\n\n"
            "Summary\n"
            "Full Stack Developer with 3 years of experience building modern web applications using "
            "React.js, Node.js, and TypeScript. Passionate about creating responsive, accessible "
            "user interfaces and scalable backend services.\n\n"
            "Technical Skills\n"
            "Frontend: React.js, Next.js, TypeScript, JavaScript, HTML5, CSS3, Tailwind CSS\n"
            "Backend: Node.js, Express.js, Python, FastAPI\n"
            "Databases: MongoDB, PostgreSQL, Redis\n"
            "DevOps: Docker, AWS (S3, EC2, CloudFront), Vercel, Netlify\n"
            "Tools: Git, GitHub, VS Code, Figma, Jira\n"
            "Testing: Jest, React Testing Library, Cypress\n\n"
            "Experience\n"
            "Full Stack Developer | WebScale Technologies | Aug 2021 - Present\n"
            "- Built responsive SaaS dashboard using React.js, TypeScript, and Tailwind CSS serving 5K+ users\n"
            "- Developed RESTful APIs with Node.js and Express, integrating MongoDB for document storage\n"
            "- Implemented real-time notifications using WebSockets and Redis pub/sub\n"
            "- Improved Lighthouse performance score from 62 to 94 through code splitting and lazy loading\n\n"
            "Frontend Developer | PixelPerfect Agency | Jan 2020 - Jul 2021\n"
            "- Created pixel-perfect UI components using React and styled-components\n"
            "- Integrated third-party APIs (Stripe, Google Maps, Twilio) for client projects\n"
            "- Led migration from class-based to functional components with React Hooks\n\n"
            "Education\n"
            "B.Tech in Information Technology | DTU Delhi | 2016-2020 | GPA: 8.3/10\n"
        )
    },
    {
        "candidate_id": "resume_sneha_patel",
        "candidate_name": "Sneha Patel",
        "resume_text": (
            "Sneha Patel\n"
            "Email: sneha.patel@email.com | Phone: +91-9988776655\n\n"
            "Summary\n"
            "Python Developer with 2 years of experience. Worked on Django-based web applications "
            "and basic data analysis projects. Looking to transition into a more senior backend role.\n\n"
            "Technical Skills\n"
            "Languages: Python, JavaScript, HTML, CSS\n"
            "Frameworks: Django, Flask\n"
            "Databases: MySQL, SQLite\n"
            "Tools: Git, VS Code, Postman\n"
            "Basics: REST APIs, Linux command line\n\n"
            "Experience\n"
            "Junior Python Developer | StartupXYZ | Mar 2022 - Present\n"
            "- Developed and maintained Django-based e-commerce platform with 2K monthly users\n"
            "- Created REST APIs for mobile app integration using Django REST Framework\n"
            "- Wrote unit tests using Django's built-in testing framework\n"
            "- Assisted in database schema design and basic query optimization\n\n"
            "Intern | CodeBridge Solutions | Jun 2021 - Feb 2022\n"
            "- Built simple Flask web applications for internal tools\n"
            "- Learned version control with Git and basic deployment on Heroku\n"
            "- Participated in code reviews and daily standup meetings\n\n"
            "Education\n"
            "B.Tech in Computer Science | Pune University | 2017-2021 | GPA: 7.8/10\n"
        )
    },
    {
        "candidate_id": "resume_vikram_singh",
        "candidate_name": "Vikram Singh",
        "resume_text": (
            "Vikram Singh\n"
            "Email: vikram.singh@email.com | Phone: +91-8765432109\n\n"
            "Summary\n"
            "Marketing professional with 6 years of experience in digital marketing, brand strategy, "
            "and content management. Expert in SEO, Google Analytics, and social media campaigns.\n\n"
            "Skills\n"
            "Digital Marketing: SEO/SEM, Google Ads, Facebook Ads, Email Marketing\n"
            "Analytics: Google Analytics, Adobe Analytics, Mixpanel\n"
            "Content: Copywriting, Content Strategy, WordPress\n"
            "Design: Canva, Adobe Photoshop (basic)\n"
            "Tools: HubSpot, Mailchimp, Hootsuite, Buffer\n\n"
            "Experience\n"
            "Senior Marketing Manager | BrandFirst Agency | Apr 2020 - Present\n"
            "- Led digital marketing strategy for 15+ B2B clients, increasing average lead generation by 45%\n"
            "- Managed annual marketing budget of $2M across paid search, social, and content channels\n"
            "- Built and optimized email marketing funnels with 35% open rate and 12% click-through rate\n"
            "- Coordinated with design and sales teams to produce quarterly brand campaigns\n\n"
            "Marketing Executive | GrowthHub Digital | Jun 2018 - Mar 2020\n"
            "- Executed SEO strategies improving organic traffic by 120% over 18 months\n"
            "- Created and managed content calendar across blog, social media, and newsletter\n"
            "- Analyzed campaign performance using Google Analytics and prepared monthly reports\n\n"
            "Education\n"
            "MBA in Marketing | IIM Indore | 2016-2018\n"
            "BBA | Mumbai University | 2013-2016\n"
        )
    },
    {
        "candidate_id": "resume_ananya_reddy",
        "candidate_name": "Ananya Reddy",
        "resume_text": (
            "Ananya Reddy\n"
            "Email: ananya.reddy@email.com | GitHub: github.com/ananyar\n\n"
            "Summary\n"
            "Backend Engineer with 3 years of experience primarily in Java and Spring Boot. "
            "Some exposure to Python scripting and basic data pipeline work. Looking to expand "
            "into Python-focused backend roles.\n\n"
            "Technical Skills\n"
            "Languages: Java, Python (intermediate), SQL, Bash\n"
            "Frameworks: Spring Boot, Hibernate, Flask (basic)\n"
            "Databases: MySQL, PostgreSQL, Redis\n"
            "DevOps: Docker, Jenkins, Ansible\n"
            "Cloud: AWS (EC2, S3, RDS)\n"
            "Tools: Git, Maven, IntelliJ IDEA, Postman\n\n"
            "Experience\n"
            "Backend Engineer | EnterpriseApps Ltd | Sep 2021 - Present\n"
            "- Developed and maintained Spring Boot microservices handling 10K+ requests per minute\n"
            "- Implemented RESTful APIs for customer management system integrated with PostgreSQL\n"
            "- Built automated data pipeline using Python scripts for ETL from MySQL to data warehouse\n"
            "- Set up CI/CD pipelines using Jenkins and Docker for containerized deployments\n"
            "- Participated in on-call rotation and incident response for production services\n\n"
            "Software Developer Intern | TechServe Inc | Jan 2021 - Aug 2021\n"
            "- Built REST API endpoints using Spring Boot and Hibernate ORM\n"
            "- Wrote JUnit tests achieving 85% code coverage\n"
            "- Learned Docker containerization and basic Kubernetes concepts\n\n"
            "Education\n"
            "B.Tech in Computer Science | BITS Pilani | 2017-2021 | GPA: 8.1/10\n"
        )
    },
    {
        "candidate_id": "resume_deepak_joshi",
        "candidate_name": "Deepak Joshi",
        "resume_text": (
            "Deepak Joshi\n"
            "Email: deepak.joshi@email.com | Kaggle: kaggle.com/deepakj\n\n"
            "Summary\n"
            "Machine Learning Engineer with 2 years of experience focused on computer vision "
            "and image classification using CNNs. Some exposure to NLP through coursework. "
            "Kaggle Competitions Expert.\n\n"
            "Technical Skills\n"
            "Languages: Python, C++\n"
            "ML/DL: TensorFlow, Keras, scikit-learn, OpenCV\n"
            "Data: pandas, numpy, matplotlib\n"
            "Cloud: GCP (Compute Engine, Cloud Storage)\n"
            "Tools: Git, Jupyter Notebook, Google Colab, Docker\n\n"
            "Experience\n"
            "ML Engineer | VisionAI Startup | Apr 2022 - Present\n"
            "- Built image classification model for defect detection achieving 96% accuracy on production data\n"
            "- Implemented data augmentation pipeline processing 100K+ images using OpenCV and Albumentations\n"
            "- Deployed TensorFlow Serving models on GCP with auto-scaling for real-time inference\n"
            "- Built model monitoring dashboard tracking accuracy drift and data quality metrics\n\n"
            "ML Intern | ResearchLab AI | Jun 2021 - Mar 2022\n"
            "- Trained object detection models using YOLO v5 for autonomous driving dataset\n"
            "- Experimented with transfer learning using pre-trained ResNet and EfficientNet models\n"
            "- Implemented basic text classification using TF-IDF and Naive Bayes for a side project\n\n"
            "Education\n"
            "M.Sc in Data Science | ISI Kolkata | 2019-2021 | GPA: 8.9/10\n"
            "B.Sc in Mathematics | St. Xavier's College | 2016-2019\n\n"
            "Kaggle\n"
            "- Expert tier with 2 silver medals in image classification competitions\n"
        )
    },
    {
        "candidate_id": "resume_meera_nair",
        "candidate_name": "Meera Nair",
        "resume_text": (
            "Meera Nair\n"
            "Email: meera.nair@email.com | Portfolio: meeranair.dev\n\n"
            "Summary\n"
            "Frontend Developer with 4 years of experience specializing in React.js ecosystem. "
            "Strong skills in TypeScript, state management, and building accessible, performant "
            "web applications. Currently learning backend development with Node.js.\n\n"
            "Technical Skills\n"
            "Frontend: React.js, TypeScript, JavaScript, Next.js, Redux, Zustand\n"
            "Styling: CSS3, SASS, Tailwind CSS, styled-components, Material UI\n"
            "Testing: Jest, React Testing Library, Cypress, Storybook\n"
            "Backend: Node.js (learning), Express.js (basic)\n"
            "Tools: Git, GitHub, Figma, Webpack, Vite\n"
            "Cloud: Vercel, Netlify, AWS S3 + CloudFront\n\n"
            "Experience\n"
            "Senior Frontend Developer | UIcraft Solutions | Feb 2022 - Present\n"
            "- Led frontend architecture for enterprise SaaS platform using React.js and TypeScript\n"
            "- Implemented design system with 40+ reusable components using Storybook\n"
            "- Achieved 98 Lighthouse accessibility score through ARIA compliance and semantic HTML\n"
            "- Reduced bundle size by 45% through tree shaking, code splitting, and dynamic imports\n"
            "- Mentored 2 junior developers on React best practices and TypeScript patterns\n\n"
            "Frontend Developer | DigitalWave Agency | May 2020 - Jan 2022\n"
            "- Built responsive marketing sites and web apps for 10+ clients using React and Next.js\n"
            "- Integrated REST APIs and managed client-side state with Redux Toolkit\n"
            "- Implemented animations using Framer Motion and CSS transitions\n\n"
            "Education\n"
            "B.Tech in Computer Science | NIT Calicut | 2016-2020 | GPA: 8.6/10\n"
        )
    },
    {
        "candidate_id": "resume_karthik_rao",
        "candidate_name": "Karthik Rao",
        "resume_text": (
            "Karthik Rao\n"
            "Email: karthik.rao@email.com | LinkedIn: linkedin.com/in/karthikrao\n\n"
            "Summary\n"
            "DevOps Engineer with 5 years of experience in cloud infrastructure, CI/CD automation, "
            "and container orchestration. Some Python scripting for automation. Not a traditional "
            "software developer but strong in infrastructure and deployment.\n\n"
            "Technical Skills\n"
            "Cloud: AWS (EC2, ECS, Lambda, S3, RDS, VPC, CloudFormation), GCP\n"
            "Containers: Docker, Kubernetes, Helm, ECS\n"
            "CI/CD: Jenkins, GitLab CI, GitHub Actions, ArgoCD\n"
            "IaC: Terraform, Ansible, CloudFormation\n"
            "Monitoring: Prometheus, Grafana, ELK Stack, Datadog\n"
            "Scripting: Python, Bash, Go (basic)\n"
            "Databases: PostgreSQL, MySQL (operational management)\n\n"
            "Experience\n"
            "Senior DevOps Engineer | CloudFirst Infrastructure | Jun 2021 - Present\n"
            "- Managed Kubernetes clusters (EKS) running 50+ microservices across staging and production\n"
            "- Implemented GitOps workflow using ArgoCD reducing deployment errors by 70%\n"
            "- Built infrastructure as code with Terraform managing 200+ AWS resources\n"
            "- Designed monitoring and alerting stack using Prometheus, Grafana, and PagerDuty\n"
            "- Automated certificate rotation and secrets management using HashiCorp Vault\n\n"
            "DevOps Engineer | ScaleUp Technologies | Aug 2019 - May 2021\n"
            "- Set up CI/CD pipelines with Jenkins for 20+ development teams\n"
            "- Containerized legacy applications using Docker and migrated to Kubernetes\n"
            "- Wrote Python automation scripts for log analysis and infrastructure provisioning\n\n"
            "Education\n"
            "B.Tech in Electronics & Communication | VIT Vellore | 2015-2019 | GPA: 7.9/10\n"
        )
    },
    {
        "candidate_id": "resume_sanya_gupta",
        "candidate_name": "Sanya Gupta",
        "resume_text": (
            "Sanya Gupta\n"
            "Email: sanya.gupta@email.com | GitHub: github.com/sanyag\n\n"
            "Summary\n"
            "Recent computer science graduate with internship experience in Python and data analysis. "
            "Completed coursework in machine learning and NLP. Strong academic background but "
            "limited industry experience. Eager to learn and grow.\n\n"
            "Technical Skills\n"
            "Languages: Python, Java, C, SQL\n"
            "ML/Data: scikit-learn, pandas, numpy, matplotlib (coursework level)\n"
            "Web: HTML, CSS, JavaScript (basic), Flask\n"
            "NLP: NLTK, SpaCy (coursework projects)\n"
            "Tools: Git, Jupyter Notebook, VS Code\n"
            "Databases: MySQL, SQLite\n\n"
            "Experience\n"
            "Data Science Intern | Analytics Corp | May 2024 - Aug 2024\n"
            "- Assisted senior data scientists in cleaning and preprocessing customer data using pandas\n"
            "- Built basic classification model using scikit-learn achieving 78% accuracy on churn prediction\n"
            "- Created data visualizations for weekly stakeholder reports using matplotlib\n"
            "- Learned SQL query optimization and database management basics\n\n"
            "Academic Projects\n"
            "- Resume Parser (NLP): Built a resume skill extractor using SpaCy NER as course project\n"
            "- Sentiment Analyzer: Implemented Twitter sentiment classification using NLTK and Naive Bayes\n"
            "- Web Scraper: Created Python web scraper for job postings using BeautifulSoup\n\n"
            "Education\n"
            "B.Tech in Computer Science | IIIT Bangalore | 2020-2024 | GPA: 8.8/10\n\n"
            "Certifications\n"
            "- Andrew Ng's Machine Learning (Coursera)\n"
            "- Python for Data Science (DataCamp)\n"
        )
    }
]


# ============================================================================
# Rule-based relevance suggestion heuristic
# ============================================================================

def suggest_relevance(resume: Dict, jd: Dict) -> tuple:
    """
    Suggest a relevance label (0-3) based on skill overlap, domain match,
    and experience alignment. Returns (score, reasoning).

    This is a HEURISTIC to bootstrap labeling — it MUST be reviewed by a human.
    """
    resume_text = resume["resume_text"].lower()
    jd_skills = [s.lower() for s in jd["required_skills"]]
    jd_title = jd["job_title"].lower()

    # 1. Skill overlap ratio
    skill_matches = sum(1 for skill in jd_skills if skill in resume_text)
    skill_ratio = skill_matches / len(jd_skills) if jd_skills else 0

    # 2. Domain relevance signals
    domain_signals = {
        "backend": ["backend", "rest api", "microservice", "server", "api"],
        "data_scientist": ["data scien", "machine learning", "nlp", "deep learning", "model"],
        "fullstack": ["full stack", "fullstack", "frontend", "react", "node.js", "web app"],
    }

    jd_domain = None
    if "backend" in jd_title:
        jd_domain = "backend"
    elif "data" in jd_title:
        jd_domain = "data_scientist"
    elif "full stack" in jd_title or "fullstack" in jd_title:
        jd_domain = "fullstack"

    domain_match = 0
    if jd_domain and jd_domain in domain_signals:
        domain_match = sum(1 for s in domain_signals[jd_domain] if s in resume_text)

    # 3. Experience keywords
    exp_text = jd.get("experience_requirements", "").lower()
    exp_years_mentioned = any(f"{y} year" in resume_text or f"{y}+ year" in resume_text
                              for y in range(1, 11))

    # 4. Scoring rules
    reasoning_parts = []

    if skill_ratio >= 0.6 and domain_match >= 3:
        suggested = 3
        reasoning_parts.append(f"Strong skill match ({skill_matches}/{len(jd_skills)} skills)")
        reasoning_parts.append(f"Strong domain relevance ({domain_match} signals)")
    elif skill_ratio >= 0.4 and domain_match >= 2:
        suggested = 2
        reasoning_parts.append(f"Good skill match ({skill_matches}/{len(jd_skills)} skills)")
        reasoning_parts.append(f"Moderate domain relevance ({domain_match} signals)")
    elif skill_ratio >= 0.2 or domain_match >= 1:
        suggested = 1
        reasoning_parts.append(f"Partial skill match ({skill_matches}/{len(jd_skills)} skills)")
        reasoning_parts.append(f"Weak domain relevance ({domain_match} signals)")
    else:
        suggested = 0
        reasoning_parts.append(f"Minimal skill match ({skill_matches}/{len(jd_skills)} skills)")
        reasoning_parts.append("No domain relevance detected")

    reasoning = "; ".join(reasoning_parts)
    return suggested, reasoning


# ============================================================================
# Generate ground truth dataset
# ============================================================================

def generate_ground_truth() -> Dict[str, Any]:
    """Generate complete ground truth with suggested relevance labels."""

    evaluations = []
    stats = {
        "total_labels": 0,
        "per_relevance": {0: 0, 1: 0, 2: 0, 3: 0},
        "per_job": {}
    }

    for jd in JOB_DESCRIPTIONS:
        candidates = []

        for resume in RESUMES:
            suggested_relevance, reasoning = suggest_relevance(resume, jd)

            candidates.append({
                "candidate_id": resume["candidate_id"],
                "candidate_name": resume["candidate_name"],
                "resume_text": resume["resume_text"],
                "relevance": suggested_relevance,
                "label_status": "REVIEW_REQUIRED",
                "auto_reasoning": reasoning,
                "notes": f"AUTO-SUGGESTED: {reasoning}. PLEASE VERIFY and adjust the relevance grade."
            })

            stats["total_labels"] += 1
            stats["per_relevance"][suggested_relevance] += 1

        evaluations.append({
            "job_id": jd["job_id"],
            "job_title": jd["job_title"],
            "job_description_text": jd["job_description_text"],
            "required_skills": jd["required_skills"],
            "experience_requirements": jd["experience_requirements"],
            "candidates": candidates
        })

        # Per-job stats
        job_stats = {r["candidate_name"]: r["relevance"] for r in candidates}
        stats["per_job"][jd["job_title"]] = job_stats

    ground_truth = {
        "_metadata": {
            "description": "Ground truth relevance labels for evaluating the resume ranking system.",
            "generated_by": "evaluation.generate_dataset",
            "label_status": "ALL labels are AUTO-SUGGESTED and marked REVIEW_REQUIRED.",
            "instructions": [
                "Review each candidate's relevance label against the job description.",
                "Adjust the 'relevance' field (0-3) based on YOUR human judgment.",
                "Change 'label_status' from 'REVIEW_REQUIRED' to 'VERIFIED' after review.",
                "The evaluation framework will warn if unverified labels remain."
            ],
            "relevance_scale": {
                "0": "Not relevant - wrong domain, no skill overlap",
                "1": "Marginally relevant - some transferable skills, weak fit",
                "2": "Relevant - good skill match, reasonable experience",
                "3": "Highly relevant - strong match, ideal candidate"
            }
        },
        "evaluations": evaluations
    }

    return ground_truth, stats


def generate_report(stats: Dict[str, Any]) -> str:
    """Generate human-readable report on labels needing verification."""

    lines = []
    lines.append("=" * 70)
    lines.append("  GROUND TRUTH GENERATION REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  Total labels generated:  {stats['total_labels']}")
    lines.append(f"  Labels needing review:   {stats['total_labels']} (ALL)")
    lines.append("")
    lines.append("  Relevance Distribution (auto-suggested):")
    lines.append(f"    0 (Not Relevant):      {stats['per_relevance'][0]}")
    lines.append(f"    1 (Marginally Rel.):   {stats['per_relevance'][1]}")
    lines.append(f"    2 (Relevant):          {stats['per_relevance'][2]}")
    lines.append(f"    3 (Highly Relevant):   {stats['per_relevance'][3]}")
    lines.append("")

    for jd_title, candidates in stats["per_job"].items():
        lines.append(f"  {'-' * 60}")
        lines.append(f"  Job: {jd_title}")
        lines.append(f"  {'-' * 60}")
        for name, rel in candidates.items():
            grade_labels = {0: "Not Relevant ", 1: "Marginal     ", 2: "Relevant     ", 3: "Highly Rel.  "}
            marker = "[REVIEW]" 
            lines.append(f"    {name:<25} -> {rel} ({grade_labels[rel]}) [{marker}]")
        lines.append("")

    lines.append("=" * 70)
    lines.append("  NEXT STEPS:")
    lines.append("  1. Open evaluation/ground_truth.json")
    lines.append("  2. Review each relevance label against the resume and JD")
    lines.append("  3. Adjust grades where the auto-suggestion is wrong")
    lines.append("  4. Change 'label_status' to 'VERIFIED' for reviewed labels")
    lines.append("  5. Run: python -m evaluation.run_evaluation")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    print("Generating evaluation dataset...")

    ground_truth, stats = generate_ground_truth()

    # Write ground truth JSON
    output_path = Path(__file__).parent / "ground_truth.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)

    print(f"Ground truth saved to: {output_path}")

    # Print report
    report = generate_report(stats)
    print(report)

    # Also save report
    report_path = Path(__file__).parent / "labeling_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
