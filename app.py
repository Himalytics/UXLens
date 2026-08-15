"""Full-page Gradio interface for UXLens.

The interface demonstrates HCI concepts directly: visible system status,
source transparency, focused information architecture, error recovery,
example-driven onboarding, keyboard-efficient input, and clear response
hierarchy.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import gradio as gr

from rag_engine import UXLensEngine


BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "assets" / "uxlens.css"
FAVICON_PATH = BASE_DIR / "assets" / "uxlens_favicon.png"

ENGINE = UXLensEngine(enable_models=True, top_k=3)

LENSES = [
    "Balanced Review",
    "Usability & Feedback",
    "Accessibility",
    "Error Prevention",
    "Cognitive Load",
    "Navigation & Consistency",
]

SCENARIOS = {
    "Checkout validation": (
        "My checkout form clears every field when the ZIP code is invalid. "
        "How should I redesign the error experience?"
    ),
    "Save confirmation": (
        "Users click Save but the page gives no confirmation. "
        "What usability problem does this create and how should I fix it?"
    ),
    "Color accessibility": (
        "My form marks required fields only with red color. "
        "What accessibility concerns should I consider?"
    ),
    "Dangerous delete": (
        "A Delete Account button permanently deletes the account immediately "
        "after one click. What should change?"
    ),
}

WELCOME = (
    "### Ready for review\n"
    "Describe an interface behavior or interaction problem below. I’ll map it to relevant HCI principles and show the evidence used."
)


def _mode_label() -> str:
    return ENGINE.mode_label


def _initial_trace() -> str:
    return f"""
    <div class="ux-trace-status"><span class="ux-trace-dot"></span>{escape(_mode_label())}</div>
    <div class="ux-side-copy">Run a review to see the three HCI principles retrieved for this scenario.</div>
    """


def _trace_html(query: str) -> str:
    results = ENGINE.retrieve(query)
    items: list[str] = []
    for index, result in enumerate(results, start=1):
        score = max(0.0, min(1.0, float(result.score)))
        items.append(
            "<div class='ux-trace-item'>"
            f"<div class='ux-trace-top'><span class='ux-trace-rank'>Retrieved {index}</span>"
            f"<span class='ux-trace-score'>{score:.2f}</span></div>"
            f"<div class='ux-trace-name'>{escape(result.chunk.title)}</div>"
            f"<div class='ux-trace-source'>{escape(result.chunk.source_file)}</div>"
            "</div>"
        )
    return (
        f"<div class='ux-trace-status'><span class='ux-trace-dot'></span>{escape(_mode_label())}</div>"
        + "".join(items)
    )


def analyze(
    message: str,
    history: list[dict] | None,
    lens: str,
) -> tuple[list[dict], str, str]:
    """Append one user/assistant turn and refresh the visible RAG trace."""
    history = list(history or [])
    cleaned = (message or "").strip()
    if not cleaned:
        return history, "", _initial_trace()

    response = ENGINE.answer(cleaned, lens=lens)
    history.append({"role": "user", "content": cleaned})
    history.append({"role": "assistant", "content": response})
    return history, "", _trace_html(cleaned)


def run_scenario(
    scenario_text: str,
    history: list[dict] | None,
    lens: str,
) -> tuple[list[dict], str, str]:
    return analyze(scenario_text, history, lens)


def clear_review() -> tuple[list[dict], str, str]:
    return [{"role": "assistant", "content": WELCOME}], "", _initial_trace()


def topbar_html() -> str:
    status_class = "good" if ENGINE.full_rag_available else "info"
    return f"""
    <div class="ux-topbar-inner">
      <div class="ux-brand">
        <div class="ux-logo" aria-hidden="true">
          <svg width="27" height="27" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3.4 14C5.8 8.9 9.4 6.2 14 6.2C18.6 6.2 22.2 8.9 24.6 14C22.2 19.1 18.6 21.8 14 21.8C9.4 21.8 5.8 19.1 3.4 14Z" stroke="#92F2F5" stroke-width="1.8"/>
            <circle cx="14" cy="14" r="4.1" stroke="#B8A7FF" stroke-width="1.8"/>
            <circle cx="14" cy="14" r="1.5" fill="#F5FBFF"/>
          </svg>
        </div>
        <div>
          <div class="ux-brand-title">UXLens</div>
          <div class="ux-brand-subtitle">AI-Powered HCI Design Review Studio</div>
        </div>
      </div>
      <div class="ux-top-pills">
        <span class="ux-pill {status_class}">{escape(_mode_label())}</span>
        <span class="ux-pill">Local models</span>
        <span class="ux-pill">Source-grounded</span>
      </div>
    </div>
    """


def hero_html() -> str:
    return f"""
    <div class="ux-hero-inner">
      <div class="ux-hero-copy-wrap">
        <div class="ux-eyebrow">Human-centered intelligence</div>
        <h1 class="ux-hero-title">Turn interface problems into <span class="ux-gradient-text">grounded UX decisions.</span></h1>
        <div class="ux-hero-copy">
          Semantic retrieval + local language generation + visible HCI evidence, designed for practical interface reviews.
        </div>
      </div>
      <div class="ux-metrics">
        <span class="ux-metric"><b>{len(ENGINE.chunks)}</b> guidance chunks</span>
        <span class="ux-metric"><b>6</b> review lenses</span>
        <span class="ux-metric"><b>3</b> principles / review</span>
        <span class="ux-metric">No paid API key</span>
      </div>
    </div>
    """


HEAD = """
<meta name="theme-color" content="#07111f" />
<meta name="description" content="UXLens — AI-powered HCI design review assistant" />
"""


with gr.Blocks(
    title="UXLens — HCI Design Review Studio",
    analytics_enabled=False,
    fill_width=True,
    fill_height=True,
) as demo:
    gr.HTML(topbar_html(), elem_id="ux-topbar")
    gr.HTML(hero_html(), elem_id="ux-hero")

    with gr.Row(elem_id="ux-main-row"):
        with gr.Column(scale=9, elem_id="chat-shell", elem_classes="ux-card"):
            gr.HTML(
                """
                <div class="ux-section-head">
                  <div>
                    <div class="ux-section-title">Design Review Workspace</div>
                    <div class="ux-section-caption">Describe the behavior. UXLens retrieves evidence, diagnoses the issue, and recommends a redesign.</div>
                  </div>
                  <div class="ux-flow-label"><span>Ask</span><b>→</b><span>Retrieve</span><b>→</b><span>Review</span></div>
                </div>
                """
            )

            chatbot = gr.Chatbot(
                value=[{"role": "assistant", "content": WELCOME}],
                show_label=False,
                container=False,
                height="58vh",
                min_height=520,
                max_height=760,
                elem_id="ux-chatbot",
                autoscroll=True,
                layout="bubble",
                buttons=["copy"],
                feedback_options=None,
                placeholder="Your HCI review will appear here.",
            )

            with gr.Row(elem_id="composer-row"):
                prompt = gr.Textbox(
                    placeholder="Describe an interface problem or ask an HCI design question…",
                    show_label=False,
                    container=False,
                    lines=1,
                    max_lines=6,
                    autofocus=True,
                    submit_btn="Analyze",
                    elem_id="prompt-box",
                    scale=10,
                )
                clear_btn = gr.Button(
                    "↻ New review",
                    variant="secondary",
                    elem_id="new-review-btn",
                    scale=1,
                )

            gr.HTML(
                """
                <div class="ux-key-hint">
                  <span><span class="ux-key">Enter</span> Analyze</span>
                  <span><span class="ux-key">Shift + Enter</span> New line</span>
                </div>
                """
            )

        with gr.Column(scale=3, elem_id="sidebar-shell", elem_classes="ux-card"):
            gr.HTML(
                """
                <div class="ux-side-block ux-side-intro">
                  <div class="ux-side-title">Choose a review lens</div>
                  <div class="ux-side-copy">Focus the critique on one HCI dimension or keep it balanced.</div>
                </div>
                """
            )
            lens = gr.Radio(
                choices=LENSES,
                value="Balanced Review",
                label=None,
                show_label=False,
                container=False,
                elem_id="review-lens",
            )

            gr.HTML(
                """
                <div class="ux-side-block ux-side-heading">
                  <div class="ux-side-title">Live RAG trace</div>
                  <div class="ux-side-copy">See which knowledge chunks informed the current review.</div>
                </div>
                """
            )
            trace = gr.HTML(_initial_trace(), elem_id="rag-trace")

            gr.HTML(
                """
                <div class="ux-side-block ux-side-heading">
                  <div class="ux-side-title">Professor-ready demo scenarios</div>
                  <div class="ux-side-copy">One click runs a complete HCI review.</div>
                </div>
                """
            )

            scenario_buttons: list[tuple[gr.Button, str]] = []
            for label, scenario in SCENARIOS.items():
                button = gr.Button(
                    f"→  {label}",
                    variant="secondary",
                    elem_classes="demo-button",
                )
                scenario_buttons.append((button, scenario))

            gr.HTML(
                """
                <details class="ux-about">
                  <summary>How UXLens works <span>+</span></summary>
                  <div class="ux-about-body">
                    <div><b>1 · Retrieve</b><br>Sentence embeddings find relevant HCI knowledge.</div>
                    <div><b>2 · Ground</b><br>Retrieved guidance constrains the review.</div>
                    <div><b>3 · Synthesize</b><br>A local FLAN-T5 model produces a concise diagnosis.</div>
                    <div><b>4 · Explain</b><br>The app exposes the evidence behind the recommendation.</div>
                  </div>
                </details>
                """
            )

    gr.HTML(
        "<div class='ux-footer-note'>Academic HCI prototype · Design guidance, not formal accessibility or legal certification.</div>"
    )

    prompt.submit(
        fn=analyze,
        inputs=[prompt, chatbot, lens],
        outputs=[chatbot, prompt, trace],
        show_progress="minimal",
    )

    clear_btn.click(
        fn=clear_review,
        inputs=None,
        outputs=[chatbot, prompt, trace],
        show_progress="hidden",
    )

    def _scenario_runner(text: str):
        def _run(history: list[dict] | None, selected_lens: str):
            return run_scenario(text, history, selected_lens)

        return _run

    for button, scenario in scenario_buttons:
        button.click(
            fn=_scenario_runner(scenario),
            inputs=[chatbot, lens],
            outputs=[chatbot, prompt, trace],
            show_progress="minimal",
        )


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=2).launch(
        inbrowser=True,
        show_error=True,
        footer_links=[],
        favicon_path=FAVICON_PATH,
        theme=gr.themes.Soft(),
        css_paths=CSS_PATH,
        head=HEAD,
    )
