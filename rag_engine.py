"""Core retrieval and grounded response logic for UXLens.

UXLens is intentionally small enough for a graduate HCI course project and a
normal laptop. It uses a local SentenceTransformer for semantic retrieval and
FLAN-T5 for a concise diagnosis. The final review is normalized into a stable,
source-grounded structure so the interface remains consistent even when a
small local model does not follow long formatting instructions perfectly.

If model files cannot be downloaded or loaded, UXLens gracefully falls back to
lexical retrieval and still produces a structured review from the curated HCI
knowledge base.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import os
import re
from typing import Iterable


DEFAULT_EMBEDDING_MODEL = os.getenv(
    "UXLENS_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
DEFAULT_GENERATION_MODEL = os.getenv(
    "UXLENS_GENERATION_MODEL", "google/flan-t5-small"
)


@dataclass(frozen=True)
class KnowledgeChunk:
    """One retrievable unit from the HCI knowledge base."""

    title: str
    text: str
    source_file: str
    reference: str = ""


@dataclass(frozen=True)
class SearchResult:
    """A knowledge chunk paired with a relevance score."""

    chunk: KnowledgeChunk
    score: float


class UXLensEngine:
    """Retrieval-augmented HCI guidance engine."""

    VALIDATION_QUESTIONS = {
        "Visibility of System Status": "After the action, can users tell whether it succeeded without repeating it or guessing?",
        "Preserve Valid User Input": "Can users correct the problem without losing valid information they already entered?",
        "Explain Expected Formats": "Can users understand the expected format before submitting and recover without trial and error?",
        "Error Identification": "Can users immediately identify what is wrong, where it occurred, and what they should do next?",
        "Do Not Rely on Color Alone": "Can users understand the same state or error without depending on color perception alone?",
        "Confirm Consequential Actions": "Before committing, do users clearly understand the consequence and have a safe way to cancel or recover?",
        "User Control and Freedom": "Can users undo, cancel, go back, or otherwise recover from an unintended action?",
        "Limit Overwhelming Choice": "Can users identify the most relevant next action without scanning too many equally prominent choices?",
        "Support Working Memory": "Can users complete the task without memorizing information from another screen or earlier step?",
        "Consistency and Standards": "Do equivalent controls, terms, and behaviors remain consistent across the experience?",
        "Follow Familiar Conventions": "Can users recognize the control or interaction without first learning a novel convention?",
        "Predictable Navigation": "Can users tell where they are, what choices are available, and how to return to a broader level?",
        "Set Appropriate Expectations": "Does the assistant communicate its scope and limits clearly enough to support calibrated trust?",
        "Ground Responses in Visible Context": "Can users see enough evidence to judge where the recommendation came from?",
        "Design Useful Fallbacks": "When the system cannot help, does it explain why and provide a clear recovery path?",
    }

    def __init__(
        self,
        knowledge_dir: str | Path | None = None,
        *,
        enable_models: bool = True,
        top_k: int = 3,
    ) -> None:
        base_dir = Path(__file__).resolve().parent
        self.knowledge_dir = Path(knowledge_dir or base_dir / "knowledge_base")
        self.top_k = max(1, top_k)
        self.chunks = self._load_knowledge_base(self.knowledge_dir)
        if not self.chunks:
            raise RuntimeError(f"No knowledge-base content found in {self.knowledge_dir}")

        self.embedding_model = None
        self.corpus_embeddings = None
        self.tokenizer = None
        self.generation_model = None
        self.model_error: str | None = None

        if enable_models:
            self._load_models()

    @property
    def full_rag_available(self) -> bool:
        return bool(
            self.embedding_model is not None
            and self.corpus_embeddings is not None
            and self.tokenizer is not None
            and self.generation_model is not None
        )

    @property
    def mode_label(self) -> str:
        return "Full semantic RAG" if self.full_rag_available else "Retrieval fallback"

    def _load_models(self) -> None:
        """Load local Hugging Face models; preserve graceful degradation on failure."""
        try:
            import torch
            from sentence_transformers import SentenceTransformer
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            self.embedding_model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
            texts = [chunk.text for chunk in self.chunks]
            self.corpus_embeddings = self.embedding_model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            self.tokenizer = AutoTokenizer.from_pretrained(DEFAULT_GENERATION_MODEL)
            self.generation_model = AutoModelForSeq2SeqLM.from_pretrained(
                DEFAULT_GENERATION_MODEL
            )
            self.generation_model.eval()

            if torch.cuda.is_available():
                self.generation_model.to("cuda")
        except Exception as exc:  # noqa: BLE001 - deliberate graceful degradation
            self.embedding_model = None
            self.corpus_embeddings = None
            self.tokenizer = None
            self.generation_model = None
            self.model_error = f"{type(exc).__name__}: {exc}"

    @staticmethod
    def _clean_markdown(text: str) -> str:
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def _load_knowledge_base(cls, directory: Path) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        for file_path in sorted(directory.glob("*.md")):
            raw = cls._clean_markdown(file_path.read_text(encoding="utf-8"))
            if not raw:
                continue

            sections = re.split(r"(?m)^##\s+", raw)
            intro = sections[0].strip()
            for section in sections[1:]:
                lines = section.splitlines()
                title = lines[0].strip()
                body = "\n".join(lines[1:]).strip()
                if not body:
                    continue
                reference = cls._extract_reference(body) or cls._extract_reference(intro)
                chunks.append(
                    KnowledgeChunk(
                        title=title,
                        text=f"{title}\n{body}",
                        source_file=file_path.name,
                        reference=reference,
                    )
                )

            if len(sections) == 1 and intro:
                title = file_path.stem.replace("_", " ").title()
                chunks.append(
                    KnowledgeChunk(
                        title=title,
                        text=intro,
                        source_file=file_path.name,
                        reference=cls._extract_reference(intro),
                    )
                )
        return chunks

    @staticmethod
    def _extract_reference(text: str) -> str:
        match = re.search(r"Reference:\s*(https?://\S+)", text)
        return match.group(1).rstrip(".,)") if match else ""

    @staticmethod
    def _tokens(text: str) -> set[str]:
        words = re.findall(r"[a-z0-9]+", text.lower())
        stop_words = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "have", "how", "i", "if", "in", "is", "it", "my", "of",
            "on", "or", "that", "the", "their", "this", "to", "user", "users",
            "what", "when", "with", "you", "your",
        }
        return {word for word in words if len(word) > 2 and word not in stop_words}

    @classmethod
    def _lexical_score(cls, query: str, chunk: KnowledgeChunk) -> float:
        q = cls._tokens(query)
        d = cls._tokens(chunk.text)
        if not q or not d:
            return 0.0
        intersection = len(q & d)
        score = intersection / math.sqrt(len(q) * len(d))

        query_lower = query.lower()
        hints = {
            "Visibility of System Status": {"save", "saved", "status", "feedback", "confirmation", "confirm", "loading", "progress"},
            "Do Not Rely on Color Alone": {"color", "colour", "red", "green", "blue"},
            "Preserve Valid User Input": {"clear", "clears", "cleared", "invalid", "re-enter", "erases", "erased"},
            "User Control and Freedom": {"delete", "deletes", "permanent", "irreversible", "undo", "cancel", "back"},
            "Confirm Consequential Actions": {"delete", "deletes", "permanent", "irreversible", "account", "confirm"},
            "Limit Overwhelming Choice": {"menu", "navigation", "choices", "options", "many", "overwhelming"},
            "Consistency and Standards": {"different", "same", "inconsistent", "terminology", "label", "icon"},
            "Support Working Memory": {"remember", "memorize", "previous", "confirmation number", "code"},
            "Explain Expected Formats": {"format", "date", "phone", "example", "expected"},
            "Follow Familiar Conventions": {"custom icon", "back", "unfamiliar", "convention", "icon"},
            "Set Appropriate Expectations": {"chatbot", "certain", "scope", "outside", "knowledge base"},
        }
        for hint in hints.get(chunk.title, set()):
            if hint in query_lower:
                score += 0.12
        return score

    def retrieve(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        query = query.strip()
        if not query:
            return []
        k = min(top_k or self.top_k, len(self.chunks))

        if self.embedding_model is not None and self.corpus_embeddings is not None:
            query_embedding = self.embedding_model.encode(
                [query],
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )[0]
            scores = self.corpus_embeddings @ query_embedding
            ranked = sorted(
                enumerate(scores), key=lambda pair: float(pair[1]), reverse=True
            )[:k]
            return [
                SearchResult(self.chunks[index], float(score))
                for index, score in ranked
            ]

        ranked_chunks = sorted(
            (SearchResult(chunk, self._lexical_score(query, chunk)) for chunk in self.chunks),
            key=lambda result: result.score,
            reverse=True,
        )[:k]
        return ranked_chunks

    @staticmethod
    def _context_from_results(results: Iterable[SearchResult]) -> str:
        parts: list[str] = []
        for number, result in enumerate(results, start=1):
            parts.append(
                f"SOURCE {number}: {result.chunk.title}\n"
                f"File: {result.chunk.source_file}\n"
                f"{result.chunk.text}"
            )
        return "\n\n".join(parts)

    def build_prompt(
        self,
        query: str,
        results: list[SearchResult],
        lens: str | None = None,
    ) -> str:
        """Build a grounded prompt. The output template is also useful documentation."""
        context = self._context_from_results(results)
        lens_instruction = ""
        if lens and lens != "Balanced Review":
            lens_instruction = f"\nPrioritize the {lens} lens while remaining grounded in the context."
        return f"""You are UXLens, a human-computer interaction design review assistant.
Use ONLY the supplied HCI context. Do not invent standards, laws, statistics, or sources.
If the context is insufficient, say that the knowledge base does not contain enough information.
Give practical design guidance, not legal compliance certification.{lens_instruction}

Respond in concise Markdown using exactly these sections:
### UX diagnosis
Explain the core interaction problem in 1-2 sentences.

### HCI principles
List the 1-3 most relevant principles as bullets and briefly connect each to the scenario.

### Recommended redesign
Give 3-5 concrete, prioritized design changes as a numbered list.

### What to validate
Give 1-2 practical usability checks or user-testing questions.

HCI CONTEXT:
{context}

DESIGN SCENARIO OR QUESTION:
{query}

UXLENS RESPONSE:
"""

    def _diagnosis_prompt(
        self,
        query: str,
        results: list[SearchResult],
        lens: str | None = None,
    ) -> str:
        context = self._context_from_results(results)
        lens_instruction = ""
        if lens and lens != "Balanced Review":
            lens_instruction = f" Focus especially on {lens}."
        return f"""You are an HCI design reviewer. Use only the context below.
Write one or two clear sentences diagnosing the interface problem. Mention the most relevant HCI idea.
Do not introduce yourself. Do not list sources. Do not use headings.{lens_instruction}

CONTEXT:
{context}

SCENARIO:
{query}

DIAGNOSIS:
"""

    def _generate(self, prompt: str, *, max_new_tokens: int = 90) -> str:
        if not self.full_rag_available:
            raise RuntimeError("The local generation model is not available.")

        import torch

        device = next(self.generation_model.parameters()).device
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )
        inputs = {key: value.to(device) for key, value in inputs.items()}
        with torch.no_grad():
            output_ids = self.generation_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=4,
                do_sample=False,
                repetition_penalty=1.08,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    @staticmethod
    def _plain_chunk_body(chunk: KnowledgeChunk) -> str:
        body = chunk.text
        if body.startswith(chunk.title):
            body = body[len(chunk.title):].lstrip("\n ")
        body = re.sub(r"Reference:\s*https?://\S+", "", body)
        body = re.split(r"Design guidance:\s*", body, maxsplit=1)[0]
        return re.sub(r"\s+", " ", body).strip()

    @classmethod
    def _chunk_summary(cls, chunk: KnowledgeChunk, max_chars: int = 190) -> str:
        body = cls._plain_chunk_body(chunk)
        sentences = re.split(r"(?<=[.!?])\s+", body)
        summary = " ".join(sentences[:2]).strip()
        if len(summary) > max_chars:
            summary = summary[:max_chars].rsplit(" ", 1)[0].rstrip(".,;") + "…"
        return summary

    @staticmethod
    def _guidance_actions(chunk: KnowledgeChunk) -> list[str]:
        match = re.search(
            r"Design guidance:\s*(.*?)(?:\n\s*Reference:|$)",
            chunk.text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if not match:
            return []
        guidance = re.sub(r"\s+", " ", match.group(1)).strip()
        raw_actions = [item.strip() for item in guidance.split(";") if item.strip()]
        actions: list[str] = []
        for action in raw_actions:
            action = action[0].upper() + action[1:] if action else action
            if action and action[-1] not in ".!?":
                action += "."
            actions.append(action)
        return actions

    def _fallback_diagnosis(self, results: list[SearchResult]) -> str:
        if not results:
            return "The available HCI knowledge base does not contain enough information for a reliable review."
        top = results[0].chunk
        summary = self._chunk_summary(top)
        return f"This scenario most strongly relates to **{top.title}**. {summary}"

    @staticmethod
    def _diagnosis_is_useful(text: str) -> bool:
        clean = re.sub(r"[#*_`]", "", (text or "")).strip()
        if len(clean) < 35:
            return False
        generic = {
            "uxlens, a human-computer interaction design review assistant",
            "human-computer interaction design review assistant",
        }
        if clean.lower().strip(". ") in generic:
            return False
        return True

    def _build_structured_review(
        self,
        query: str,
        results: list[SearchResult],
        *,
        lens: str | None = None,
        diagnosis: str | None = None,
    ) -> str:
        if not results:
            return (
                "### UX diagnosis\n"
                "The local knowledge base does not contain enough matching information to give a reliable recommendation.\n\n"
                "### What to validate\n"
                "- Add more detail about the interface behavior, the user goal, and what is going wrong."
            )

        diagnosis = (diagnosis or "").strip()
        if not self._diagnosis_is_useful(diagnosis):
            diagnosis = self._fallback_diagnosis(results)

        principle_lines: list[str] = []
        for result in results:
            principle_lines.append(
                f"- **{result.chunk.title}** — {self._chunk_summary(result.chunk)}"
            )

        actions: list[str] = []
        seen: set[str] = set()
        for result in results:
            for action in self._guidance_actions(result.chunk):
                key = re.sub(r"[^a-z0-9]+", " ", action.lower()).strip()
                if key and key not in seen:
                    actions.append(action)
                    seen.add(key)
                if len(actions) >= 5:
                    break
            if len(actions) >= 5:
                break
        if not actions:
            actions = [
                "Use the retrieved HCI principles as explicit design constraints and test the revised interaction with representative users."
            ]

        validation: list[str] = []
        for result in results:
            question = self.VALIDATION_QUESTIONS.get(result.chunk.title)
            if question and question not in validation:
                validation.append(question)
            if len(validation) >= 2:
                break
        if not validation:
            validation = [
                "Can representative users complete the task without confusion, unnecessary repetition, or avoidable errors?",
                "Do users understand the system state and the next available action at each step?",
            ]

        mode = self.mode_label
        lens_text = lens or "Balanced Review"

        source_items: list[str] = []
        for result in results:
            label = f"`{result.chunk.source_file}` — **{result.chunk.title}**"
            if result.chunk.reference:
                label += f" — [reference]({result.chunk.reference})"
            source_items.append(f"<li>{label}</li>")

        return (
            "### UX diagnosis\n"
            f"{diagnosis}\n\n"
            "### HCI principles\n"
            + "\n".join(principle_lines)
            + "\n\n### Recommended redesign\n"
            + "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))
            + "\n\n### What to validate\n"
            + "\n".join(f"- {question}" for question in validation)
            + "\n\n### Evidence used\n"
            + f"**{len(results)} retrieved HCI principles** · {mode} · {lens_text}\n\n"
            + "<details class=\"ux-evidence-details\"><summary>View evidence & sources</summary><ul>"
            + "".join(source_items)
            + "</ul></details>\n\n"
            + "> UXLens provides design guidance, not a formal accessibility or legal compliance determination."
        )

    def answer(self, query: str, *, lens: str | None = None) -> str:
        query = (query or "").strip()
        if not query:
            return "Please describe an interface, usability issue, or HCI design question."
        if len(query) < 8:
            return "Please provide a little more detail so I can evaluate the design scenario."

        results = self.retrieve(query)
        if not results:
            return "I could not retrieve relevant guidance from the local knowledge base."

        diagnosis = ""
        if self.full_rag_available:
            try:
                diagnosis = self._generate(
                    self._diagnosis_prompt(query, results, lens),
                    max_new_tokens=80,
                )
            except Exception as exc:  # noqa: BLE001
                self.model_error = f"{type(exc).__name__}: {exc}"

        return self._build_structured_review(
            query,
            results,
            lens=lens,
            diagnosis=diagnosis,
        )
