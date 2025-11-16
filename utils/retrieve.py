# utils/retrieve.py
import re
import json
from models.embeddings import embed_single
from utils.indexer import search_vector
from utils.prompts import build_learning_path_prompt
from models.llm import LLMModel

class CourseRetriever:

    def __init__(self):
        self.llm = LLMModel()

    def is_learning_intent(self, text: str) -> bool:
        """
        Lightweight intent detector to decide if user wants to learn / get courses.
        This keeps the main app fast and simple.
        """
        t = (text or "").lower()
        # phrases that indicate the user wants course recommendations / learning path
        keywords = [
            "learn", "learning", "i want to learn", "recommend me a course",
            "recommend courses", "recommend course", "course for", "teach me",
            "i want to study", "want to study", "suggest a course", "recommend"
        ]
        for k in keywords:
            if k in t:
                return True
        return False

    def retrieve_courses(self, query: str, top_k: int = 5):
        """
        Query Qdrant for similar courses.
        """
        if not query:
            query = "machine learning"  # fallback default
        query_vec = embed_single(query)
        results = search_vector(query_vec, top_k)
        return results

    def generate_learning_path(self, user_profile: dict, retrieved_courses: list):
        """
        Build the roadmap using cleaned course data + LLM.
        """

        cleaned_courses = []

        for item in retrieved_courses:
            payload = item.get("payload", {}) if item else {}
            cleaned_courses.append({
                "title": payload.get("title") or payload.get("course_title"),
                "url": payload.get("url") or payload.get("course_url") or payload.get("final_url"),
                "site": payload.get("site"),
                "rating": payload.get("rating"),
                "skills": payload.get("skills"),
                "instructors": payload.get("instructors"),
                "category": payload.get("category") or payload.get("sub-category"),
                "intro": payload.get("short_intro") or payload.get("course_short_intro") or payload.get("Short Intro")
            })

        prompt = build_learning_path_prompt(user_profile, cleaned_courses)
        return self.llm.generate(prompt)

    def continue_conversation(self, user_message, history):
        """
        Continue normal chat using LLM.
        history is [(role, msg), (role, msg) ...]
        """

        # LLM expects -> [{"role": "...", "content": "..."}]
        formatted_history = [{"role": r, "content": m} for (r, m) in history]

        return self.llm.chat(user_message, formatted_history)



# ------------------------------------------------------
# PROFILE PARSER
# ------------------------------------------------------
def parse_profile_from_message(message: str):

    if not message:
        return {}

    m = message.lower()

    extracted = {
        "field_of_interest": None,
        "skills_to_master": None,
        "preference": None,
        "level": None,
        "career_goal": None,
        "availability": None
    }

    # Field detection (more permissive)
    fields = [
        "machine learning", "ml", "web development", "web dev", "cybersecurity",
        "ui design", "data science", "cloud computing", "ai", "java", "python"
    ]
    for f in fields:
        if f in m:
            # normalize ml -> machine learning
            if f == "ml":
                f = "machine learning"
            extracted["field_of_interest"] = f
            break

    # Skills (add a few common keywords)
    skills = re.findall(r"(python|react|node|sql|javascript|html|css|nlp|dl|ml|data science|java|pandas|numpy|pytorch)", m)
    if skills:
        extracted["skills_to_master"] = ", ".join(sorted(set(skills)))

    # Preference detection
    if "video" in m or "video-based" in m or "videos" in m:
        extracted["preference"] = "video courses"
    elif "text" in m or "book" in m or "article" in m:
        extracted["preference"] = "text-based learning"

    # Level
    if "beginner" in m:
        extracted["level"] = "beginner"
    elif "intermediate" in m:
        extracted["level"] = "intermediate"
    elif "advanced" in m:
        extracted["level"] = "advanced"

    # Career goal
    goal_match = re.search(r"become (an? )?([a-z ]+)", m)
    if goal_match:
        extracted["career_goal"] = goal_match.group(2).strip()

    # Availability (hours)
    time_match = re.search(r"(\d+)\s*(hours|hrs|hour)\/?\s*(week|weekly)?", m)
    if time_match:
        extracted["availability"] = time_match.group(1) + " hours/week"

    return extracted


# ------------------------------------------------------
# FOLLOW-UP QUESTIONS
# ------------------------------------------------------
def make_followup_for_missing(missing_fields: list):

    mapping = {
        "field_of_interest": "Which field do you want to learn? (e.g. machine learning, web development, data science, Java...)\n",
        "skills_to_master": "What specific skills do you want to master? (e.g. Python, SQL, React, NLP)\n",
        "preference": "Do you prefer video courses or text-based learning?\n",
        "level": "What is your current skill level? (Beginner / Intermediate / Advanced)\n",
        "career_goal": "What career goal are you aiming for (e.g. data scientist, backend developer)?\n",
        "availability": "How many hours per week can you study? (e.g. 10 hours)\n"
    }

    questions = [mapping[m] for m in missing_fields if m in mapping]

    if not questions:
        return "I need a few more details before I can advise you."

    return "I need a few more details before I can recommend courses:\n" + "\n".join(questions)
