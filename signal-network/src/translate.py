"""Translation wrapper around AI4Bharat IndicTrans2."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TranslationResult:
    success: bool
    translations: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None


class IndicTrans2Translator:
    """Wrapper for AI4Bharat IndicTrans2 direct Indic→Indic translation.

    Supports dependency injection of a model/tokenizer for testing.
    """

    def __init__(
        self,
        model_id: str = "ai4bharat/indictrans2-indic-indic-1B",
        device: str = "cpu",
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
    ):
        self.model_id = model_id
        self.device = device
        self._model = model
        self._tokenizer = tokenizer

    def load(self) -> None:
        """Load model and tokenizer. Skipped if injected."""
        # If a callable mock model was injected without a tokenizer, assume the
        # caller wants to bypass real model loading entirely.
        if callable(self._model) and self._tokenizer is None:
            return
        if self._model is not None and self._tokenizer is not None:
            return
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_id,
                trust_remote_code=True,
            ).to(self.device)
        except Exception as exc:
            raise RuntimeError(f"Failed to load translation model {self.model_id}: {exc}") from exc

    # Map short language codes to IndicTrans2 Flores codes.
    LANG_MAP = {
        "as": "asm_Beng", "bn": "ben_Beng", "brx": "brx_Deva", "doi": "doi_Deva",
        "en": "eng_Latn", "gom": "gom_Deva", "gu": "guj_Gujr", "hi": "hin_Deva",
        "kn": "kan_Knda", "ks": "kas_Deva", "mai": "mai_Deva", "ml": "mal_Mlym",
        "mni": "mni_Beng", "mr": "mar_Deva", "ne": "npi_Deva", "or": "ory_Orya",
        "pa": "pan_Guru", "sa": "san_Deva", "sat": "sat_Olck", "sd": "snd_Deva",
        "ta": "tam_Taml", "te": "tel_Telu", "ur": "urd_Arab",
    }

    def _flores(self, code: str) -> str:
        return self.LANG_MAP.get(code, code)

    def translate(
        self,
        text: str,
        source_lang: str,
        target_langs: List[str],
    ) -> TranslationResult:
        """Translate text from source_lang into each target language."""
        if not text.strip():
            return TranslationResult(success=True, translations={})

        self.load()

        translations: Dict[str, str] = {}
        try:
            src = self._flores(source_lang)
            for tgt in target_langs:
                tgt_flores = self._flores(tgt)
                # If a callable was injected, use it.
                if callable(self._model) and self._tokenizer is None:
                    translated = self._model(text, source_lang, tgt)
                else:
                    prefix = f"{src} {tgt_flores} "
                    inputs = self._tokenizer(
                        prefix + text,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                    ).to(self.device)
                    outputs = self._model.generate(**inputs, use_cache=False)
                    translated = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
                translations[tgt] = translated.strip()
            return TranslationResult(success=True, translations=translations)
        except Exception as exc:
            return TranslationResult(success=False, error=f"Translation failed: {exc}")
