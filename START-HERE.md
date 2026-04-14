# 🚀 START HERE - Proyecto GAZE-INFERENCE

**Bienvenido, ingeniero distribuido. Aquí está todo lo que necesitas.**

---

## 📖 Qué Leer en Este Orden

### 1️⃣ Este archivo (5 min)
Ya lo estás leyendo. Es tu mapa.

### 2️⃣ QUICK-START.md (15 min)
Cómo instalar, tu primer task, comandos salvavidas.

**Si:** Quieres empezar a codear HOY  
**Lee:** `QUICK-START.md` → Salta al punto "Día 1-2: Tu Primer Task"

### 3️⃣ ENGINEERING-GUIDELINES.md (30-60 min)
La biblia completa. Estructura del proyecto, Git workflow, testing, buenas prácticas.

**Si:** Necesitas saber cómo hacer X (logs, testing, commits, etc)  
**Lee:** Busca en Índice de `ENGINEERING-GUIDELINES.md` → Jump a sección

### 4️⃣ GAZE-INFERENCE-ROADMAP.md (15 min)
Qué fases existen, arquitectura, timeline.

**Si:** Necesitas contexto del proyecto  
**Lee:** `GAZE-INFERENCE-ROADMAP.md`

---

## 🗂️ Estructura de Archivos (Lo Esencial)

```
gaze-inference/
├── START-HERE.md                    ← TÚ ESTÁS AQUÍ
├── QUICK-START.md                   ← Lee luego
├── ENGINEERING-GUIDELINES.md        ← Tu referencia (bookmark)
├── GAZE-INFERENCE-ROADMAP.md        ← Contexto del proyecto
│
├── Makefile                         ← make test, make lint, make run-app
├── requirements.txt                 ← pip install -r requirements.txt
├── requirements-dev.txt             ← pip install -r requirements-dev.txt
├── pyproject.toml                   ← Configuración centralizada
├── .pre-commit-config.yaml          ← Hooks automáticos (pre-commit install)
├── .gitignore                       ← Qué NO comittear
│
├── src/                             ← Tu código fuente
│   ├── sensorium/                   ← 🎥 Percepción (MediaPipe, OpenCV)
│   ├── brain/                       ← 🧠 Inferencia (KAN, Friston)
│   ├── overlay/                     ← 🖥️ Interfaz (PyQt6)
│   └── utils/
│
├── tests/                           ← Tests (unit, integration, e2e)
│   ├── conftest.py                  ← Fixtures compartidas (ver tests-conftest.py)
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── scripts/                         ← Scripts ejecutables
    ├── run.py                       ← App principal
    ├── calibrate.py                 ← Modo training
    └── validate_latency.py          ← Test básico

```

---

## 🎯 Tu Flujo de Trabajo (Repítelo Diariamente)

### Morning
1. `git checkout develop && git pull`  
   → Asegurate que tienes última versión

2. Abre un issue en GitHub que te asignes a ti  
   → O comenta: "I'll take this"

3. `git checkout -b feature/tu-feature`  
   → Crea rama local

### Mid-day
4. Escribe test primero (TDD)  
   → `tests/unit/test_tu_feature.py`

5. Implementa código  
   → `src/modulo/file.py`

6. `pytest && make lint && make format`  
   → Verifica todo pase

7. `git commit -m "type(scope): description"`  
   → Conventional commits

### Afternoon
8. `git push -u origin feature/tu-feature`  
   → Empuja a remoto

9. GitHub PR → Completa template automático  
   → Espera review (24h máx)

10. Si hay comentarios → responde con commits  
    → `git push` (sin -u, ya existe rama)

11. Cuando CI pase + 1 approval → **MERGE**  
    → GitHub merge button

### Evening
12. Revisa PRs de otros ingenieros  
    → Comenta, approba, o pide cambios

---

## 🔧 Comandos Más Frecuentes

```bash
# Testing
make test                          # Corre todos los tests
make test-unit                     # Solo unit tests
make benchmark                     # Tests de latencia
pytest tests/unit/ -v              # Específico

# Linting & Format
make lint                          # Verifica código
make format                        # Formatea automático
black src/ && pylint src/          # Explícito

# Desarrollo
make run-app                       # Ejecuta app
make run-calibrate                 # Modo training

# Git
git status                         # ¿Qué cambié?
git diff                          # Ver cambios
git log --oneline -5              # Últimos commits

# Útil
make clean                        # Limpia archivos temporales
make help                         # Lista todos los make commands
```

---

## 📋 Checklist: Antes de `git push`

- [ ] `pytest` pasa (todos los tests)
- [ ] `make lint` sin errores (score > 8.0)
- [ ] `make format` ejecutado
- [ ] Docstrings en funciones nuevas
- [ ] Tipo hints en firmas (`def func(x: int) -> str:`)
- [ ] No hay `print()` (usar `logger`)
- [ ] Commits en Conventional Commits format
- [ ] No hay credenciales/secrets en código
- [ ] PR tiene descripción clara

---

## ❓ FAQ Rápidas

### "¿Dónde veo qué trabajar?"
GitHub Issues → Filtra por:
- `phase: phase-0` (actual)
- `priority: high` o `medium`
- Status: Open
- Click en uno, comenta "I'll take this"

### "¿Mi test no pasa en CI pero sí local?"
Causas más comunes:
- No usar `set_seed(42)` → Agregar al init de test
- Paths relativos vs absolutos → Usar `Path(__file__).parent`
- Requerir GPU en CI → Forzar CPU en test: `device='cpu'`

### "¿Cómo hago merge de dos branches?"
No lo haces manualmente. GitHub lo hace automático cuando:
1. Tests de CI pasan ✅
2. Al menos 1 review approval ✅
3. Clickeas "Merge pull request" ✅

### "¿Qué pasa si me equivoco?"
Tranquilo:
```bash
git revert HEAD      # Crea nuevo commit que deshace el anterior
git push             # Empuja
```

### "¿Puedo trabajar offline?"
Sí, pero máximo 1 día sin `git pull`:
```bash
git fetch origin     # Descarga cambios remotos (sin mergear)
git rebase origin/develop  # Aplica tus cambios arriba
git push -f origin feature/tu-feature  # ⚠️ Force push
```

### "¿Cómo actualizo dependencias?"
```bash
pip install --upgrade torch jax
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: upgrade dependencies"
git push
```

### "¿Mi GPU no funciona?"
```python
# Force CPU en code
device = torch.device("cpu")
model.to(device)
x = x.to(device)
```

### "¿Dónde reporto bugs?"
GitHub Issues → Click "New issue" → Usa template automático

---

## 👥 Comunicación Inter-Pueblos

### Síncrono (Raro)
- **Emergencias críticas:** Slack #urgent
- **Decisiones de diseño:** GitHub Discussion

### Asíncrono (Normal)
- **Status:** Lunes 10:00 UTC en issue pinned (comentar)
- **Code review:** Responde en 24h máximo
- **Preguntas:** GitHub issue + @ mention

**Plantilla de status (pon esto en lunes):**
```
**Tu Nombre (Pueblo X):**
- ✅ Completado: Feature X (PR #123 merged)
- 🚧 Working: Feature Y (ETA: Jueves)
- ❓ Bloqueado en: Issue #456 (esperando otra rama)
- 💭 Questions: ¿Deberíamos usar JAX o PyTorch para Active Inference?
```

---

## 🎓 Aprender del Proyecto

### Patrones Encontrados en Codebase

**Type hints:**
```python
def extract_features(frame: np.ndarray) -> Tuple[np.ndarray, dict]:
    ...
```

**Docstrings (Google style):**
```python
def compute_free_energy(q, mu, sigma):
    """Calcula energía libre variacional.
    
    Args:
        q: Vector de estado.
        mu: Predicción.
        sigma: Varianza.
        
    Returns:
        Escalar F.
    """
```

**Logging, no print:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
```

**PyTorch patterns:**
```python
model.train()  # Antes de training
model.eval()   # Antes de eval/inference
with torch.no_grad():
    pred = model(x)
```

**Testing (TDD):**
1. Escribe test que falla
2. Implementa lo mínimo para pasar
3. Refactoriza manteniendo test verde

---

## 📚 Referencia Rápida

| Necesito... | Leo... | O corro... |
|-------------|--------|-----------|
| Empezar YA | QUICK-START.md | `make help` |
| Saber cómo hacer X | ENGINEERING-GUIDELINES.md | Busca en índice |
| Entender arquitectura | GAZE-INFERENCE-ROADMAP.md | Lee secciones 1-2 |
| Ver ejemplos de código | tests-conftest.py | Busca `# EXAMPLE` |
| Instalar deps | requirements.txt | `pip install -r` |
| Configuración de tests | pyproject.toml | Sección `[tool.pytest]` |

---

## 🚨 Reglas Irrompibles

1. **Nunca commits directo a `main` o `develop`**  
   → Siempre via Pull Request con review

2. **Tests pasan antes de push**  
   → `pytest` + `make lint`

3. **Commits descriptivos**  
   → `feat(scope): description`, no "fixed stuff"

4. **Code review ≤ 24h**  
   → No dejes PR colgando más de 1 día

5. **No hardcodes**  
   → Todo en `config.py`

6. **No credentials en repo**  
   → `.env` y `.gitignore`

---

## 💬 Si Te Atascas

1. **Está en ENGINEERING-GUIDELINES.md?**  
   → Busca por palabra clave

2. **Alguien más lo hizo antes?**  
   → Busca en `git log` o issues cerradas

3. **Es un bug? ¿Feature request?**  
   → Abre issue en GitHub con template

4. **Necesitas ayuda urgente?**  
   → Comenta en issue + @ mention a otro ingeniero

---

## ✨ Tips de Pro

- **Bookmark `ENGINEERING-GUIDELINES.md`** → Lo usarás 50x al día
- **`make test-fast`** → Corre tests rápidos mientras codeas
- **`git log --oneline -5`** → Siempre antes de push para revisar
- **`pytest -k "test_name"` → Corre solo tests que matchean patrón
- **Pytest fixtures en `conftest.py`** → Reutilizable en todos los tests
- **Pre-commit hooks** → `pre-commit install` corre linting automático antes de commit

---

## 🎉 Eso es Todo

**Eres listo para ser un Gaze-Inference Engineer.**

Próximo paso: Ve a `QUICK-START.md` y empieza tu primer task. 💪

---

**¿Más dudas?** Lee ENGINEERING-GUIDELINES.md (es muy completo).  
**¿Primer día?** Sigue QUICK-START.md paso a paso.  
**¿Bloqueado?** Abre un GitHub issue.

---

Last updated: 2026-04-13  
Status: Ready for Phase 0 🟢
