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
                                           the section, REQUIRING strictly
                                           increasing numbers (rejects
                                           noise, but breaks on multi-
                                           column row-major grids)
                          "grid_list"   -> same "<num>. (<ans>)" matching
                                           as inline_list but WITHOUT the
                                           increasing-order requirement --
                                           for answer keys laid out in
                                           several side-by-side columns
                                           per row (AAKASH-style)
  solutions_heading  - optional heading marking the end of the answer-key
                        section (so solution text below isn't misread as
                        more answers)
  two_pdf             - optional, default False. Set True when this
                        coaching ships the question paper and the
                        answer-key/solutions as two SEPARATE PDFs (e.g.
                        AAKASH) rather than one combined file. When set,
                        cbt.py collects both PDFs before processing and
                        hands the second one to parser.parse_pdf() as
                        second_pdf_path; the answer-key section is then
                        taken to start exactly at the question paper's
                        last page instead of being located via
                        answer_key_heading (which may not exist as
                        literal text on such profiles). answer_key_heading
                        is unused for two_pdf profiles but is still kept
                        as a dict key for uniformity -- set it to None.
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
    "aakash": {
        # AAKASH (AIATS) papers: question numbers are "1.", "2." ... (a
        # dot, not Allen's paren) and options are "(1)".."(4)" same as
        # Allen. The question paper and the answer-key/"Hints and
        # Solutions" booklet are two separate PDF files, and the answer
        # grid page has no literal "ANSWER KEY" heading text -- it just
        # starts straight into a subject box ("PHYSICS") followed by
        # lines like "1.  (1)", so answer_key_heading can't be used to
        # locate it. two_pdf=True tells cbt.py to collect both files and
        # parser.py to take the boundary as the question-paper's page
        # count instead of searching for a heading.
        "label": "Aakash",
        "subject_names": _DEFAULT_SUBJECTS,
        "question_re": re.compile(r"^(\d{1,3})\.\s?(.*)$", re.DOTALL),
        "option_re": re.compile(r"^\((\d)\)\s?(.*)$", re.DOTALL),
        "answer_key_heading": None,
        # inline_list tried first (works if the grid extracts single-file);
        # grid_list is the fallback for the row-major two-column layout
        # ("1. (1)   24. (2)" on one line) -- whichever gets better
        # coverage wins automatically (see parse_pdf's mode loop).
        "answer_key_modes": ["inline_list", "grid_list"],
        "solutions_heading": "Hints and Solutions",
        "two_pdf": True,
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
    order = ["allen", "aakash"] + sorted(p for p in PROFILES if p not in ("allen", "aakash", "generic")) + ["generic"]
    return [(pid, PROFILES[pid]["label"]) for pid in order if pid in PROFILES]
