import re


COMMON_SKILLS = [
    "python",
    "java",
    "fastapi",
    "spring boot",
    "docker",
    "kubernetes",
    "postgresql",
    "mysql",
    "redis",
    "kafka",
    "rabbitmq",
    "aws",
    "gcp",
    "azure",
    "rest api",
    "microservices",
    "mongodb",
    "react",
    "javascript"
]


def extract_skills(text):

    text = text.lower()

    found = []

    for skill in COMMON_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found.append(skill)

    return sorted(list(set(found)))


def calculate_match(resume_skills, jd_skills):

    matched = set(resume_skills).intersection(set(jd_skills))

    missing = set(jd_skills) - set(resume_skills)

    if len(jd_skills) == 0:
        return 0, [], []

    score = (len(matched) / len(jd_skills)) * 100

    return round(score, 2), list(matched), list(missing)
