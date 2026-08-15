# UXLens

**UXLens: A Retrieval-Augmented Chatbot for Human-Computer Interaction Design Guidance**

UXLens is a graduate HCI course project that lets a user describe an interface or usability problem and receive grounded design guidance. The application retrieves relevant content from a controlled HCI knowledge base and, when local models are available, passes that context to a small instruction-tuned language model for response generation.

## Why this project exists

Designers and developers can build technically functional interfaces while still overlooking feedback, consistency, accessibility, error recovery, cognitive load, and other interaction concerns. UXLens provides a conversational way to perform a preliminary design review against established HCI guidance.

UXLens is **not** a formal usability study, WCAG conformance audit, legal opinion, or substitute for testing with real users.

## Architecture

```text
User design scenario
        |
        v
Premium Gradio review studio
        |
        v
Selected review lens + user scenario
        |
        v
SentenceTransformer embedding
        |
        v
Semantic retrieval from local HCI knowledge base
        |
        v
Top relevant HCI chunks
        |
        v
Grounded context to local FLAN-T5 model
        |
        v
Concise model diagnosis
        |
        v
Programmatically normalized HCI review
        |
        v
Diagnosis + principles + redesign + validation + evidence
```

If local model loading fails, UXLens remains usable in a retrieval-only fallback mode and explains that limitation instead of crashing.

## Technology

- Python
- Gradio
- Sentence Transformers
- Hugging Face Transformers
- `sentence-transformers/all-MiniLM-L6-v2` for semantic retrieval
- `google/flan-t5-small` for local text generation
- Local Markdown knowledge base
- Git / GitHub for version control

No OpenAI API key or paid LLM API is required.

## Project structure

```text
UXLens/
├── app.py
├── rag_engine.py
├── assets/
│   ├── uxlens.css
│   └── uxlens_favicon.png
├── requirements.txt
├── README.md
├── .gitignore
├── knowledge_base/
│   ├── accessibility.md
│   ├── cognitive_load.md
│   ├── conversational_ai.md
│   ├── forms_and_errors.md
│   ├── navigation_and_consistency.md
│   └── nielsen_heuristics.md
├── tests/
│   ├── evaluation_questions.csv
│   └── test_engine.py
└── screenshots/
```

## Setup

### 1. Open a terminal in the project folder

On macOS or Linux:

```bash
cd /path/to/UXLens
```

On Windows PowerShell:

```powershell
cd C:\path\to\UXLens
```

### 2. Create a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Upgrade pip and install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the tests

```bash
python -m unittest discover -s tests -v
```

The unit tests intentionally use the retrieval fallback so they do not need to download the language models.

### 5. Run UXLens

```bash
python app.py
```

Gradio will start a local web server and open the app in the default browser.

**First run note:** Hugging Face model files are downloaded the first time full RAG mode starts. Allow the download to finish before demonstrating the project. Later runs normally reuse the local model cache.


## Interface highlights

The current interface is designed as a polished HCI review studio rather than a default chatbot page. It includes:

- a full-page branded review studio with a dark glass-style visual system;
- six selectable review lenses, including accessibility and cognitive load;
- a live **RAG trace** that reveals the top retrieved HCI principles for each review;
- one-click professor-ready demo scenarios;
- a visible system-status indicator showing full semantic RAG or fallback mode;
- a dedicated **New review** action for error recovery and task reset;
- **Enter to analyze** and **Shift + Enter for a new line**; and
- structured responses organized into **UX diagnosis**, **HCI principles**, **Recommended redesign**, **What to validate**, and **Evidence used**; and
- collapsible evidence/source details so citations remain available without dominating the recommendation.

These interface choices intentionally demonstrate visibility of system status, progressive disclosure, recognition over recall, clear feedback, consistency, and user control.

## Suggested demo prompts

1. `My checkout form clears every field when the ZIP code is invalid. How should I redesign it?`
2. `Users click Save but the page gives no confirmation. What usability problem does this create?`
3. `My form marks required fields only with red color. What accessibility concerns should I consider?`
4. `The navigation menu has 18 choices at the same level. How could I reduce cognitive load?`
5. `A Delete Account button permanently deletes the account immediately after one click. What should change?`

## Evaluation approach

The `tests/evaluation_questions.csv` file contains ten representative scenarios and the HCI principle expected to be most relevant. These scenarios support qualitative testing of retrieval quality, response grounding, coverage across HCI topics, and failure behavior.

A complete project evaluation should record:

- whether the expected principle was retrieved;
- whether the recommendation was relevant to the scenario;
- whether the response stayed within the supplied knowledge base;
- whether source information was displayed;
- whether the application recovered gracefully from weak or unsupported questions.

## Knowledge-base references

The local knowledge base summarizes guidance from the following sources:

- Nielsen Norman Group, *10 Usability Heuristics for User Interface Design*: https://www.nngroup.com/articles/ten-usability-heuristics/
- Nielsen Norman Group, *Minimize Cognitive Load to Maximize Usability*: https://www.nngroup.com/articles/minimize-cognitive-load/
- Nielsen Norman Group, *Consistency and Standards*: https://www.nngroup.com/articles/consistency-and-standards/
- Nielsen Norman Group, *Mental Models and User Experience Design*: https://www.nngroup.com/articles/mental-models/
- W3C Web Accessibility Initiative, *WCAG 2 Overview*: https://www.w3.org/WAI/standards-guidelines/wcag/
- W3C Web Accessibility Initiative, *Understanding WCAG 2.2*: https://www.w3.org/WAI/WCAG22/Understanding/
- W3C Web Accessibility Initiative, forms tutorials and accessibility guidance: https://www.w3.org/WAI/tutorials/forms/

The knowledge-base text is a concise project-specific summary rather than a copy of the source pages.

## Model and library references

- Gradio ChatInterface: https://www.gradio.app/docs/gradio/chatinterface
- Sentence Transformers semantic search documentation: https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html
- Hugging Face FLAN-T5 documentation: https://huggingface.co/docs/transformers/model_doc/flan-t5
- FLAN-T5 Small model card: https://huggingface.co/google/flan-t5-small

## Limitations

- A small local language model can produce incomplete or awkward phrasing; UXLens therefore normalizes the final response structure and falls back to retrieved HCI guidance when needed.
- Retrieval quality depends on the coverage and wording of the local knowledge base.
- UXLens evaluates text descriptions; it does not inspect a live interface or image in this version.
- Source display improves transparency but does not prove that every generated sentence is correct.
- The project is a learning prototype and should not be used as a certification tool.

## Course context

Created for **Artificial Intelligence for Human-Computer Interaction**, University of the Cumberlands, as an individual makeup residency project.
