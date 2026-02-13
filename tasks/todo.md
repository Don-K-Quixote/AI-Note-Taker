# Code Quality Audit + GPT LLM Integration

## Checklist

- [x] Create `src/llm_providers.py` (LLMProvider ABC, OllamaProvider, OpenAIProvider, get_provider factory)
- [x] Update `requirements.txt` (add openai, fpdf2, loguru)
- [x] Update `src/meeting_recorder.py`:
  - [x] Add `"llm"` and `"openai"` sections to DEFAULT_CONFIG
  - [x] Fix bare `except:` on line ~1133
  - [x] Refactor `MeetingProcessor.__init__()` to create LLM provider
  - [x] Refactor `generate_mom()` to use `self.llm_provider.generate()`
  - [x] Add LLM provider dropdown to FloatingButton UI
  - [x] Replace all `print()` with loguru
  - [x] Add type hints to modified methods
  - [x] Replace `traceback.print_exc()` with `logger.exception()`
- [x] Update `src/process_meeting.py`:
  - [x] Use shared LLM provider instead of duplicate Ollama code
  - [x] Add `--provider` and `--openai-model` CLI args
  - [x] Replace all `print()` with loguru
  - [x] Add type hints and docstrings

## Review

### Files Changed
| File | Change Summary |
|------|---------------|
| `src/llm_providers.py` | **NEW** - LLM provider abstraction: `LLMProvider` ABC, `OllamaProvider`, `OpenAIProvider`, `get_provider()` factory |
| `src/meeting_recorder.py` | Added `llm`/`openai` config sections, refactored `MeetingProcessor` to use providers, added LLM dropdown to UI, fixed bare `except:`, replaced all `print()` with `loguru`, added type hints |
| `src/process_meeting.py` | Replaced duplicate Ollama code with shared `LLMProvider`, added `--provider`/`--openai-model` CLI args, replaced all `print()` with `loguru`, added type hints and docstrings |
| `requirements.txt` | Added `openai>=1.0.0`, `fpdf2>=2.7.0`, `loguru>=0.7.0` |
| `tasks/todo.md` | Task tracking |

### Key Design Decisions
- **Provider pattern**: Abstract base class (`LLMProvider`) with concrete `OllamaProvider` and `OpenAIProvider` implementations, plus a `get_provider()` factory
- **Backward compatible**: Existing `ollama` config section untouched; new `llm.provider` key defaults to `"ollama"` if missing
- **API key resolution**: `OPENAI_API_KEY` env var takes priority over `config.json` value
- **UI integration**: Blue-colored LLM provider dropdown in the floating button, disabled during recording
- **Runtime switching**: `MeetingProcessor.set_provider()` allows changing the LLM provider without restarting the app
