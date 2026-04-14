# 📑 Índice de Documentación - Proyecto GAZE-INFERENCE

**Guía rápida de dónde está cada cosa**

---

## 📄 Documentos Principales

### 1. **START-HERE.md** ⭐
**Para:** Ingeniero nuevo que llega hoy  
**Lee primero:** Sí, ahora mismo  
**Tiempo:** 5 minutos  
**Qué hace:**
- Mapa de documentación
- Flujo de trabajo diario
- Checklist esencial
- FAQ rápidas

---

### 2. **QUICK-START.md**
**Para:** "Quiero empezar a codear YA"  
**Cuándo:** Después de START-HERE.md  
**Tiempo:** 15 minutos de setup + 1 hora primer task  
**Qué hace:**
- Setup del venv (comando a comando)
- Primer task completo (ejemplo real)
- Patrón diario de trabajo
- Comandos salvavidas
- Checklist pre-push

---

### 3. **ENGINEERING-GUIDELINES.md** 📖
**Para:** "¿Cómo se hace X en este proyecto?"  
**Cuándo:** Constantemente (bookmark)  
**Tiempo:** 30-60 min lectura completa, 2-5 min por consulta  
**Qué cubre:**
- Estructura de directorios canónica
- Convenciones de nombres
- Git workflow completo (branches, commits, PRs)
- Estándares de código (Python, PyTorch, JAX)
- Testing (TDD, unit, integration, latency)
- Documentación (docstrings, README, API)
- Buenas prácticas (config, logging, error handling)
- Debugging y profiling

**Secciones principales:**
1. Estructura del Proyecto
2. Workflow Git
3. Estándares de Código
4. Testing
5. Documentación
6. Comunicación y Tracking
7. Buenas Prácticas
8. Debugging y Logs

---

### 4. **GAZE-INFERENCE-ROADMAP.md**
**Para:** Entender el proyecto a nivel arquitecto  
**Cuándo:** Primer día, luego ocasionalmente  
**Tiempo:** 15 minutos  
**Qué cubre:**
- Visión general del proyecto
- Arquitectura de 3 capas (Percepción, Inferencia, Interfaz)
- Stack técnico completo
- 5 fases de implementación (Fase 0 a Fase 5)
- Requisitos de hardware y software
- Métricas de éxito
- Timeline esperado

---

## 🔧 Configuración y Setup

### 5. **Makefile**
**Qué es:** Tareas comunes automáticas  
**Úsalo:** `make <task>`  
**Tareas disponibles:**
```bash
make help           # Ver todas las tareas
make install        # Instalar deps producción
make install-dev    # Instalar deps desarrollo
make test           # Correr tests
make lint           # Verificar código
make format         # Formatear automático
make run-app        # Ejecutar app
make benchmark      # Tests de latencia
make ci             # Simular CI localmente
```

---

### 6. **pyproject.toml**
**Qué es:** Configuración centralizada del proyecto  
**Secciones:**
- `[project]`: Metadatos (nombre, versión, deps)
- `[tool.black]`: Configuración de formatter
- `[tool.isort]`: Configuración de import sorting
- `[tool.pylint]`: Configuración de linting
- `[tool.pytest.ini_options]`: Configuración de tests
- `[tool.coverage.run]`: Configuración de cobertura

**Nunca edites:** A menos que agregues nueva dependencia

---

### 7. **requirements.txt**
**Qué es:** Dependencias de producción (pinned versions)  
**Cuándo editar:** Cuando necesites nuevo paquete  
**Comando:**
```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- PyTorch + Torchvision
- JAX + JAXlib
- MediaPipe
- OpenCV
- PyQt6
- TensorRT

---

### 8. **requirements-dev.txt**
**Qué es:** Dependencias solo para desarrollo  
**Cuándo editar:** Herramientas de testing/linting  
**Comando:**
```bash
pip install -r requirements-dev.txt
```

**Herramientas incluidas:**
- pytest (testing)
- black, pylint, isort (code quality)
- mypy (type checking)
- pre-commit (git hooks)

---

### 9. **.pre-commit-config.yaml**
**Qué es:** Hooks que se ejecutan automáticamente antes de commit  
**Setup:** `pre-commit install`  
**Qué hace:**
- ✅ Detecta secrets
- ✅ Formatea código (black)
- ✅ Organiza imports (isort)
- ✅ Lint básico
- ✅ Type checking (mypy)

---

### 10. **.gitignore**
**Qué es:** Archivos que NO deben commiterse  
**Incluye:**
- `__pycache__/`, `*.pyc` (Python)
- `*.egg-info/`, `dist/`, `build/` (packaging)
- `.venv/`, `venv/` (virtual envs)
- `.vscode/`, `.idea/` (IDEs)
- `logs/`, `*.log` (logging)
- `data/models/`, `data/calibration/` (data local)
- Credentials, configs locales

---

## 🧪 Testing

### 11. **tests-conftest.py** (→ `tests/conftest.py`)
**Qué es:** Fixtures compartidas para todos los tests  
**Cómo usarlo:** Copy a `tests/conftest.py`  
**Qué proporciona:**

**Fixtures útiles:**
- `dummy_frame`: Frame 480x640x3
- `dummy_features`: Vector 16D
- `dummy_batch`: Batch (32, 16) y (32, 2)
- `dummy_dataloader`: DataLoader para training
- `kan_model`: Modelo KAN dummy
- `trained_kan_model`: Modelo pre-entrenado 5 épocas
- `mock_camera`: Mock sin hardware
- `mock_mediapipe`: Mock de MediaPipe
- `device`: GPU o CPU (automático)
- `tmp_data_dir`: Directorio temporal

**Helpers:**
- `create_dummy_checkpoint()`: Crear checkpoint
- `assert_latency()`: Verificar < N ms
- `pytest_configure()`: Registrar markers
- `pytest_collection_modifyitems()`: Auto-markers

---

## 📁 Estructura de Código

**Directorios a crear:**

```
src/
├── __init__.py
├── config.py           # Configuración (desde pyproject.toml)
├── logger.py           # Logging centralizado
├── sensorium/          # Capa de Percepción
├── brain/              # Capa de Inferencia
├── overlay/            # Capa de Interfaz
└── utils/              # Helpers

data/
├── calibration/        # Datasets de usuario
├── models/             # Checkpoints
└── raw/                # Datos sin procesar

tests/
├── __init__.py
├── conftest.py         # Fixtures (copiar tests-conftest.py aquí)
├── unit/               # Tests unitarios
├── integration/        # Tests multi-componente
└── e2e/                # Tests usuario completo

scripts/
├── validate_latency.py # Validación Fase 0
├── calibrate.py        # Modo training
├── run.py              # App principal
└── benchmark.py        # Profiling
```

---

## 🚀 Cómo Empezar

### Ingeniero Nuevo (Día 1)

1. **Lee START-HERE.md** (5 min)
2. **Lee QUICK-START.md** (15 min)
3. **Setup** (15 min):
   ```bash
   git clone <repo>
   cd gaze-inference
   python -m venv venv && source venv/bin/activate
   pip install -r requirements-dev.txt
   pre-commit install
   pytest -v  # Verificar todo anda
   ```
4. **Elige tu primer task** (en GitHub Issues)
5. **Sigue QUICK-START.md → Día 1-2: Tu Primer Task**

---

### Consulta Rápida (Después)

**"¿Cómo hago X?"**

1. Busca en `ENGINEERING-GUIDELINES.md` índice
2. Jump a sección relevante
3. Copia-pega patrón

**"¿Qué estructura tiene el proyecto?"**

1. Lee sección "Estructura del Proyecto" en ENGINEERING-GUIDELINES.md
2. Mira `src/` en repo

**"¿Cuál es el task principal?"**

1. Lee GAZE-INFERENCE-ROADMAP.md
2. Mira fase actual (probablemente Fase 0)

---

## 📊 Referencia por Rol

### Backend Engineer (PyTorch/JAX)
- Estudia: `ENGINEERING-GUIDELINES.md` → Estándares de Código (PyTorch/JAX)
- Testing: Usa fixtures de `tests-conftest.py`
- Modelo: Sigue patrón en `tests-conftest.py` → `kan_model`

### Frontend Engineer (PyQt6)
- Estudia: `ENGINEERING-GUIDELINES.md` → Testing (UI)
- Componentes: `src/overlay/widgets.py`
- Styling: `src/overlay/styles.py` (QSS)

### DevOps / Testing
- Todo: `ENGINEERING-GUIDELINES.md` → Testing (completo)
- CI/CD: `.github/workflows/` (no creado, pero config en pyproject.toml)
- Hooks: `.pre-commit-config.yaml`

### Arquitecto / Lead
- Roadmap: `GAZE-INFERENCE-ROADMAP.md`
- Decisiones: `ENGINEERING-GUIDELINES.md` → Filosofía (TDD, etc)
- Métricas: `GAZE-INFERENCE-ROADMAP.md` → Métricas de Éxito

---

## 🔍 Buscar Algo Específico

### "¿Cómo manejo errores?"
→ ENGINEERING-GUIDELINES.md → Buenas Prácticas → "Error Handling Específico"

### "¿Cuál es el formato de commit?"
→ ENGINEERING-GUIDELINES.md → Workflow Git → "Formato de Commits"

### "¿Cómo runneo un test específico?"
→ QUICK-START.md → "Comandos Salvavidas"

### "¿Qué pasa en Fase 2?"
→ GAZE-INFERENCE-ROADMAP.md → "Fase 2: Regresor KAN"

### "¿Cómo profiling?"
→ ENGINEERING-GUIDELINES.md → Buenas Prácticas → "Performance Profiling"

---

## ✅ Checklist Completo para Nuevo Ingeniero

- [ ] Leí START-HERE.md
- [ ] Leí QUICK-START.md
- [ ] Instalé venv y deps (`make install-dev`)
- [ ] Cloné repo y hice `pytest`
- [ ] Bookmarkeé ENGINEERING-GUIDELINES.md
- [ ] Entiendo estructura en GAZE-INFERENCE-ROADMAP.md
- [ ] Entiendo Fase 0 (latency validation)
- [ ] Creé mi primera rama (`git checkout -b feature/...`)
- [ ] Escribí mi primer test
- [ ] Implementé código que pase test
- [ ] Corrí `make lint && make format`
- [ ] Hice mi primer commit
- [ ] Hice mi primer push y PR
- [ ] Leí alguien else's PR y comenté

---

## 🔗 Quick Links

**Setup rápido:**
```bash
make install-dev          # Instalar todo
make test                 # Correr tests
make lint && make format  # Verificar + arreglar
```

**Git rápido:**
```bash
git checkout develop      # Cambiar a develop
git pull origin develop   # Actualizar
git checkout -b feature/x # Nueva rama
git push -u origin ...    # Push nueva rama
```

**Testing rápido:**
```bash
pytest -v                 # Verbose
pytest -k pattern         # Solo tests con patrón
pytest --cov=src          # Con cobertura
pytest -m "not slow"      # Sin tests lentos
```

---

**Última actualización:** 2026-04-13  
**Documentación versión:** 1.0  
**Status:** 🟢 Ready for Phase 0
