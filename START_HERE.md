# Start Here — UXLens v3

This package contains the presentation-ready, full-page UXLens HCI review studio.

## First-time setup on macOS

```bash
cd /path/to/UXLens
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py
```

The first full-RAG launch may download the Hugging Face models. Later launches normally reuse the local model cache.

## Interaction

- **Enter** — submit/analyze the current scenario
- **Shift + Enter** — add a new line
- **New review** — clear the conversation and start fresh
- **Review lens** — focus the critique on a specific HCI dimension
- **Demo scenario buttons** — run a professor-ready example immediately
- **Live RAG trace** — see the HCI knowledge chunks retrieved for the current review
- **Evidence & sources** — expand the evidence section inside an answer when you want to show source transparency

## Recommended demo order

1. Launch the app and point out **Full semantic RAG** in the top bar.
2. Select **Usability & Feedback** and run **Save confirmation**.
3. Walk through the structured response: **UX diagnosis → HCI principles → Recommended redesign → What to validate**.
4. Point to the **Live RAG trace** and show the retrieved evidence.
5. Select **Accessibility** and run **Color accessibility**.
6. End with **Dangerous delete** to demonstrate user control and error prevention.

## Evaluation

Run the semantic retrieval evaluation after installation:

```bash
python tests/evaluate_retrieval.py --semantic
```

Keep the output for the Results Report.

Do not publish to GitHub until the app has been tested successfully on the demo laptop.
