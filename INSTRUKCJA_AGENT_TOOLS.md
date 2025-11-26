# 📖 Przepis: Jak przekształcić Agentów w Narzędzia (Agent Tools)

## 🎯 Cel

Przekształcenie istniejących agentów AI w wielokrotnego użytku **function_tools**, które mogą być:
- Wywoływane przez inne agenty
- Używane w workflows
- Zarejestrowane w Coordinator Agent
- Testowane jednostkowo

## 🛒 Lista składników (wymagane importy)

### Plik: `agent_tools.py`
```python
from agents import function_tool, Runner
from planner_agent import planner_agent, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from evaluator_agent import evaluator_agent, EvaluationResult
from clarification_agent import clarification_agent, ClarificationQuestions
from query_enrichment import enrich_query_with_answers
from clarification_agent import EnrichedQuery
```

### Opcjonalnie: `test_agent_tools.py`
```python
import asyncio
from agent_tools import AGENT_TOOLS, [nazwy_konkretnych_tools]
import json
from dotenv import load_dotenv
```

---

## 👨‍🍳 Plan wykonania

### **KROK 1: Stwórz plik `agent_tools.py`**

#### 1.1 Zaimportuj wymagane biblioteki i agentów

```python
from agents import function_tool, Runner
# Import wszystkich agentów które chcesz przekształcić w tools
from [nazwa_agenta] import [agent_object], [OutputModel]
```

**Wskazówki:**
- `function_tool` - dekorator OpenAI SDK który tworzy tool z funkcji
- `Runner` - do wykonywania agentów wewnątrz toola
- Importuj zarówno agenta jak i jego modele wyjściowe (Pydantic)

---

#### 1.2 Dla każdego agenta - stwórz function_tool wrapper

**Szablon:**

```python
@function_tool
async def [nazwa_narzedzia]([parametr_1]: [typ], [parametr_2]: [typ]) -> str:
    """
    [KRÓTKI OPIS CO ROBI - 1 zdanie]

    Args:
        [parametr_1]: [Opis parametru]
        [parametr_2]: [Opis parametru]

    Returns:
        [Opis wyniku - zawsze string dla prostoty komunikacji między agentami]
    """
    # KROK A: Przygotuj input dla agenta
    input_text = f"[FORMAT INPUTU DLA AGENTA]: {[parametr_1]}\n..."

    # KROK B: Uruchom agenta
    result = await Runner.run(
        [agent_object],
        input_text
    )

    # KROK C: Wyciągnij structured output (jeśli agent ma output_type)
    [structured_output] = result.final_output_as([OutputModel])

    # KROK D: Sformatuj jako string (dla innych agentów)
    output = f"""[NAGŁÓWEK]: {[structured_output].[pole]}

[SEKCJA_1]:
{[structured_output].[pole_2]}
"""

    # KROK E: Zwróć string
    return output
```

**Kluczowe zasady:**
1. **Zawsze zwracaj `str`** - łatwiejsze parsowanie przez inne agenty
2. **Dekorator `@function_tool`** - PRZED definicją funkcji
3. **Async** - wszystkie narzędzia asynchroniczne (`async def`)
4. **Docstring** - obowiązkowy, opisuje tool dla innych agentów
5. **Structured → String** - konwertuj Pydantic modele na czytelny tekst

---

#### 1.3 Przykłady konkretnych tools

**Przykład 1: Tool do planowania searcha**

```python
@function_tool
async def plan_research_searches(query: str) -> str:
    """
    Plan web searches for a research query.

    Args:
        query: The research query to plan searches for

    Returns:
        List of planned searches with reasoning
    """
    # A: Input
    result = await Runner.run(
        planner_agent,
        f"Query: {query}"
    )

    # B: Structured output
    plan = result.final_output_as(WebSearchPlan)

    # C: Format jako string
    output = f"Planned {len(plan.searches)} searches:\n\n"
    for i, item in enumerate(plan.searches, 1):
        output += f"{i}. Search: \"{item.query}\"\n"
        output += f"   Reason: {item.reason}\n\n"

    return output
```

**Przykład 2: Tool do wykonania web search**

```python
@function_tool
async def perform_web_search(search_term: str, reason: str) -> str:
    """
    Perform a single web search and summarize results.

    Args:
        search_term: The search query
        reason: Why this search is important

    Returns:
        Summary of search results (2-3 paragraphs)
    """
    input_text = f"Search term: {search_term}\nReason: {reason}"

    try:
        result = await Runner.run(search_agent, input_text)
        return str(result.final_output)  # Agent już zwraca string
    except Exception as e:
        return f"Search failed: {str(e)}"
```

**Przykład 3: Tool z JSON parametrem**

```python
@function_tool
async def enrich_query_context(original_query: str, qa_pairs_json: str) -> str:
    """
    Enrich query with Q&A pairs.

    Args:
        original_query: Original query
        qa_pairs_json: JSON string of Q&A pairs

    Returns:
        Enriched research context
    """
    import json

    # Parse JSON input
    qa_pairs = json.loads(qa_pairs_json)

    # Call helper function
    enriched = await enrich_query_with_answers(original_query, qa_pairs)

    # Format output
    output = f"Enriched Context: {enriched.enriched_context}\n\n"
    output += "Key Focus Areas:\n"
    for area in enriched.key_focus_areas:
        output += f"- {area}\n"

    return output
```

**Wskazówki:**
- Używaj `try/except` dla tools które mogą się nie udać (np. web search)
- JSON stringi dla złożonych struktur danych
- Formatuj output czytelnie - inne agenty muszą go zrozumieć

---

#### 1.4 Eksportuj listę wszystkich tools

Na końcu pliku:

```python
# Export all tools as a list for easy registration
AGENT_TOOLS = [
    [nazwa_tool_1],
    [nazwa_tool_2],
    [nazwa_tool_3],
    # ... wszystkie tools
]
```

**Po co:**
- Łatwa rejestracja wszystkich tools w Coordinator
- Lista dostępnych możliwości
- Ułatwia testowanie

---

### **KROK 2: (Opcjonalnie) Stwórz V2 ResearchManager**

Jeśli chcesz pokazać jak używać tools zamiast bezpośrednich wywołań agentów.

```python
from agent_tools import perform_web_search, evaluate_report_quality
# ... inne tools

class ResearchManagerV2:
    async def search_with_tool(self, item: WebSearchItem) -> str | None:
        """Użyj tool zamiast bezpośredniego wywołania agenta"""
        try:
            result = await perform_web_search(item.query, item.reason)
            return result
        except Exception:
            return None
```

**Wskazówki:**
- Trzymaj oryginalny ResearchManager dla backward compatibility
- V2 pokazuje nową architekturę
- Stopniowa migracja - nie wszystko na raz

---

### **KROK 3: Stwórz testy `test_agent_tools.py`**

#### 3.1 Struktura testów

```python
import asyncio
from agent_tools import [tool_1], [tool_2], AGENT_TOOLS
from dotenv import load_dotenv

load_dotenv(override=True)

async def test_agent_tools():
    """Test każdego tool osobno"""

    print("=" * 60)
    print("AGENT TOOLS TEST")
    print("=" * 60)

    # TEST 1: [Nazwa toola]
    print("\nTEST 1: [Nazwa]")
    result = await [tool_1]([parametry])
    print(f"Output:\n{result}")

    # TEST 2: [Kolejny tool]
    # ...

    # TEST FINAL: Lista dostępnych tools
    print(f"\nAvailable tools: {len(AGENT_TOOLS)}")
    for tool in AGENT_TOOLS:
        print(f"- {tool.__name__}")

if __name__ == "__main__":
    asyncio.run(test_agent_tools())
```

**Wskazówki:**
- Testuj każdy tool osobno
- Używaj przykładowych danych (nie prawdziwe searche w testach)
- Sprawdź czy output jest czytelny
- Lista wszystkich tools na końcu

---

#### 3.2 Uruchom testy

```bash
python test_agent_tools.py
```

**Czego się spodziewać:**
- Każdy tool zwraca sformatowany string
- Brak błędów importu
- Output jest czytelny dla człowieka (i dla agenta)

---

## 📊 Porównanie: Przed vs Po

### Przed (bezpośrednie wywołanie agenta):

```python
# W ResearchManager
result = await Runner.run(planner_agent, f"Query: {query}")
plan = result.final_output_as(WebSearchPlan)
# Musisz wiedzieć o WebSearchPlan, planner_agent, etc.
```

**Problemy:**
- Tight coupling
- Trudno wielokrotnie użyć
- Nie można przekazać innemu agentowi

### Po (użycie tool):

```python
# Gdziekolwiek - nawet w innym agencie
search_plan = await plan_research_searches(query)
# Prosty string, łatwy do użycia
```

**Korzyści:**
- Loose coupling
- Wielokrotne użycie
- Może być tool dla coordinator agent
- Łatwiejsze testowanie

---

## 🔧 Zastosowania Agent Tools

### 1. Coordinator Agent (Commit 5)
```python
coordinator = Agent(
    name="Coordinator",
    tools=AGENT_TOOLS,  # Wszystkie tools dostępne
    instructions="..."
)
```

### 2. Standalone użycie
```python
result = await evaluate_report_quality(query, report)
print(result)
```

### 3. Custom workflows
```python
# Mix and match tools
plan = await plan_research_searches(query)
# ... parsuj plan ...
result = await perform_web_search(term, reason)
```

### 4. Testing
```python
# Łatwe unit testy
result = await generate_clarification_questions("test query")
assert "Question" in result
```

---

## ⚠️ Najważniejsze punkty uwagi

### 1. **Zawsze zwracaj `str`**
✅ Dobre:
```python
return f"Result: {data.field}"
```

❌ Złe:
```python
return data  # Pydantic object - nie zadziała jako tool
```

### 2. **Async all the way**
```python
@function_tool
async def my_tool(...):  # ZAWSZE async
    result = await Runner.run(...)  # await
```

### 3. **Docstring jest obowiązkowy**
Agent coordinator czyta docstring żeby zrozumieć co tool robi!

```python
@function_tool
async def my_tool(param: str) -> str:
    """
    [TO JEST BARDZO WAŻNE - agent to czyta]
    """
```

### 4. **Error handling**
Dla tools które mogą się nie udać:

```python
try:
    result = await Runner.run(...)
    return str(result.final_output)
except Exception as e:
    return f"Operation failed: {str(e)}"
```

### 5. **Format outputu**
Strukturyzuj output czytelnie:

```python
output = f"""Title: {title}

Section 1:
- Point A
- Point B

Section 2:
{detailed_info}
"""
return output
```

---

## ✅ Checklist przed commitowaniem

- [ ] Plik `agent_tools.py` zawiera wszystkie function_tools
- [ ] Każdy tool ma dekorator `@function_tool`
- [ ] Każdy tool zwraca `str` (nie Pydantic obiekty)
- [ ] Każdy tool ma kompletny docstring
- [ ] Wszystkie tools są async
- [ ] Lista `AGENT_TOOLS` eksportowana na końcu
- [ ] `test_agent_tools.py` działa bez błędów
- [ ] Wszystkie testy przechodzą
- [ ] Backward compatibility zachowana (oryginalny ResearchManager działa)

---

## 🎯 Następne kroki

Po implementacji Agent Tools:
1. **Commit 4**: Dodaj handoffy między tools
2. **Commit 5**: Stwórz Coordinator Agent używając `AGENT_TOOLS`
3. **Commit 7**: Iteracyjne ulepszanie używając tools w pętli

---

## 💡 Pro tips

1. **Nazywaj tools opisowo**: `plan_research_searches` > `plan_stuff`
2. **Jeden tool = jedna odpowiedzialność**: nie mieszaj planowania i wykonania
3. **Test coverage**: przetestuj każdy tool osobno
4. **Dokumentuj**: czytelny docstring = agent wie kiedy użyć tool
5. **String formatting**: używaj f-strings z czytelnymi sekcjami

---

Ten wzorzec sprawia, że agenty stają się **kompozytowalne** - możesz je łączyć jak klocki LEGO! 🧱
