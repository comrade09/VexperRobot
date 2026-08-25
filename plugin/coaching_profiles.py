"""
Registry of per-coaching parsing profiles.

Every coaching brand formats its test PDFs slightly differently, so each
profile just tunes a few regexes/keywords rather than needing a whole new
parser. Ship a new coaching by adding an entry here (and, if its layout is
genuinely unusual, adjusting parser.py's block-walk — see README).

Fields:
  label              - button text shown to the user
  subject_names      - set of exact subject-header strings this paper uses
  question_re        - regex matching the START of a question text block,
                        group(1) = question number (as text)
  option_re          - regex matching the START of an option text block,
                        group(1) = option number 1-4
  answer_key_heading - the heading text that starts the answer-key section
  answer_key_modes   - list of parsing strategies to try, in order, until
                        one produces answers for (close to) every question:
                          "qa_table"    -> repeating "Q. 1 2 3.. / A. 3 3 1.."
                                           rows, GLOBAL numbering across the
                                           whole paper (ALLEN-style)
                          "inline_list" -> "1. (3)  2. (1)  3. (4) ..." runs
                                           of "<num>. (<ans>)" anywhere in
                                           the section
  solutions_heading  - optional heading marking the end of the answer-key
                        section (so solution text below isn't misread as
                        more answers)
"""
import re

_DEFAULT_SUBJECTS = {"PHYSICS", "CHEMISTRY", "BIOLOGY", "MATHEMATICS", "MATHS", "ZOOLOGY", "BOTANY"}

PROFILES = {
    "allen": {
        "label": "ALLEN",
        "subject_names": _DEFAULT_SUBJECTS,
        "question_re": re.compile(r"^(\d{1,3})\)\s?(.*)$", re.DOTALL),
        "option_re": re.compile(r"^\((\d)\)\s?(.*)$", re.DOTALL),
        "answer_key_heading": "ANSWER KEYS",
        "answer_key_modes": ["qa_table", "inline_list"],
        "solutions_heading": "SOLUTIONS",
    },
    "generic": {
        "label": "Other / Generic",
        "subject_names": _DEFAULT_SUBJECTS,
        "question_re": re.compile(r"^(\d{1,3})[\)\.]\s?(.*)$", re.DOTALL),
        "option_re": re.compile(r"^\(?([1-4])\)[\.\)]?\s?(.*)$", re.DOTALL),
        "answer_key_heading": "ANSWER KEY",   # matched as a substring, see parser.py
        "answer_key_modes": ["qa_table", "inline_list"],
        "solutions_heading": "SOLUTION",
    },
    # Add new coachings here once you've sent a sample PDF and it's been
    # tuned, e.g.:
    # "resonance": {
    #     "label": "Resonance",
    #     "subject_names": _DEFAULT_SUBJECTS,
    #     "question_re": re.compile(r"^Q\.(\d{1,3})\s?(.*)$", re.DOTALL),
    #     "option_re": re.compile(r"^\(([A-D])\)\s?(.*)$", re.DOTALL),
    #     "answer_key_heading": "ANSWER KEY",
    #     "answer_key_modes": ["inline_list"],
    #     "solutions_heading": "SOLUTIONS",
    # },
}

DEFAULT_PROFILE_ID = "generic"


def get_profile(profile_id):
    return PROFILES.get(profile_id, PROFILES[DEFAULT_PROFILE_ID])


def list_profiles():
    """Returns [(id, label), ...] in a stable, deliberate order."""
    order = ["allen"] + sorted(p for p in PROFILES if p not in ("allen", "generic")) + ["generic"]
    return [(pid, PROFILES[pid]["label"]) for pid in order if pid in PROFILES]
