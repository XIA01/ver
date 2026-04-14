# ⚡ QUICK START - Proyecto GAZE-INFERENCE

**Para ingenieros distribuidos que quieren empezar YA**

---

## Día 1: Setup (15 minutos)

```bash
# 1. Clonar
git clone <URL-del-repo>
cd gaze-inference

# 2. Python + venv
python3.10 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate en Windows

# 3. Dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Pre-commit hooks (auto-formatting)
pre-commit install

# 5. Verificar que todo anda
pytest tests/test_latency.py -v
```

**✅ Si todo pasa, estás listo.**

---

## Día 1-2: Tu Primer Task

### 1️⃣ Elegir un issue

Abre GitHub → Issues → Filtra por `priority:high` + `phase:phase-0`

Ejemplo:
- "Implement camera capture via OpenCV" (Fase 0)
- "Add feature extractor unit tests" (Fase 0)

### 2️⃣ Crear rama

```bash
git checkout develop
git pull origin develop
git checkout -b feature/camera-capture  # Ej: feature/tu-feature

# Alternativa: bugfix/issue-123
git checkout -b fix/mediapipe-crash
```

### 3️⃣ Escribir test primero

```python
# tests/unit/test_camera.py
import pytest
from src.sensorium.camera import CameraCapture

def test_camera_init():
    """Debe inicializar sin errores."""
    cam = CameraCapture(device_id=0)
    assert cam is not None

def test_camera_read_frame():
    """Debe capturar frame de 480x640."""
    cam = CameraCapture()
    frame = cam.read()
    assert frame.shape == (480, 640, 3)
```

### 4️⃣ Implementar código

```python
# src/sensorium/camera.py
import cv2
import numpy as np

class CameraCapture:
    def __init__(self, device_id: int = 0):
        self.cap = cv2.VideoCapture(device_id)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
    
    def read(self) -> np.ndarray:
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame")
        return cv2.resize(frame, (640, 480))
    
    def release(self):
        self.cap.release()
```

### 5️⃣ Pasar tests

```bash
pytest tests/unit/test_camera.py -v
```

Output esperado:
```
tests/unit/test_camera.py::test_camera_init PASSED
tests/unit/test_camera.py::test_camera_read_frame PASSED

====== 2 passed in 0.15s ======
```

### 6️⃣ Format + Lint

```bash
# Black (formatter automático)
black src/sensorium/camera.py

# Lint (verificar calidad)
pylint src/sensorium/camera.py

# Output esperado: score 9.5-10/10
```

O simplemente:

```bash
make lint
make format
```

### 7️⃣ Commit

```bash
git add src/sensorium/camera.py tests/unit/test_camera.py
git commit -m "feat(sensorium): implement camera capture via OpenCV

- Initialize VideoCapture with device_id 0
- Read and resize frames to 480x640
- Raise RuntimeError on failures
- Add unit tests for init and read

Closes #42"
```

**Formato importante:**
```
type(scope): subject    ← Corta, descriptiva

body                    ← Detalles (opcional)
- Punto 1
- Punto 2

Closes #123            ← Enlaza a issue (GitHub cierra automático)
```

### 8️⃣ Push

```bash
git push -u origin feature/camera-capture
```

Output:
```
...
remote: Create a pull request for 'feature/camera-capture' on GitHub by visiting:
remote: https://github.com/tu-org/gaze-inference/pull/new/feature/camera-capture
```

### 9️⃣ Pull Request

1. Copia el link anterior
2. Llena el template automático
3. Espera review (máx 24h)

---

## Patrón Diario

```
Mañana:
  [1] git checkout develop && git pull
  [2] Crea rama feature/tu-feature
  [3] Escribe test + código
  [4] pytest && make lint
  [5] Commit + push
  [6] PR en GitHub

Tarde:
  [1] Revisa PRs de otros ingenieros
  [2] Approba o pide cambios
  [3] Merge cuando CI pase + 1 approval
```

---

## Comandos Salvavidas

```bash
# ¿Qué rama estoy?
git branch

# ¿Cambios sin hacer commit?
git status

# ¿Últimos commits?
git log --oneline -5

# ¿Diff con develop?
git diff develop

# ¿Descartar cambios locales? (⚠️ Peligroso)
git checkout -- src/

# ¿Volver commit anterior?
git revert HEAD

# ¿Todos los tests?
pytest -v

# ¿Un solo test?
pytest tests/unit/test_camera.py::test_camera_init -v

# ¿Tests rápidos? (skip slowest)
pytest -m "not slow" -v

# ¿Coverage?
pytest --cov=src

# ¿Latencia?
make benchmark
```

---

## Archivos Importantes

| Archivo | Qué es | Lee si |
|---------|--------|--------|
| `ENGINEERING-GUIDELINES.md` | **Tu biblia** | Quieres saber cómo hacer algo |
| `GAZE-INFERENCE-ROADMAP.md` | Qué fases existen | Necesitas contexto del proyecto |
| `Makefile` | Tasks comunes | Quieres correr tests/lint rápido |
| `pyproject.toml` | Configuración | Entiendes que existen configs |
| `requirements.txt` | Dependencias | Necesitas instalar paquete nuevo |

---

## Requisitos Mínimos de Hardware

- ✅ RTX 3060 (o similar GPU NVIDIA)
- ✅ Webcam C920 (o USB 3.0)
- ✅ 8GB RAM (16GB mejor)
- ✅ Linux (Ubuntu 22.04+, Fedora 39+)

---

## FAQ

### "Mi test falla en CI pero pasa localmente"

Causas comunes:
- ❌ Seed aleatorio → ✅ Usar `set_seed(42)` en inicio
- ❌ Paths absolutos → ✅ Usar `Path(__file__).parent`
- ❌ GPU no disponible en CI → ✅ Forzar `device='cpu'` en test

### "¿Dónde reporto bugs?"

GitHub Issues → Usa template automático:
```
Title: [BUG] Camera crashes on startup

Description:
- What I did: ...
- What happened: ...
- Expected: ...
- Logs: [paste error]
```

### "¿Cómo actualizo dependencias?"

```bash
pip install --upgrade torch jax mediapipe
pip freeze > requirements.txt  # Pinea versiones
git add requirements.txt
git commit -m "chore: upgrade dependencies"
```

### "¿Puedo trabajar sin GPU?"

Sí, pero más lento:
```python
device = torch.device("cpu")  # Fuerza CPU
model.to(device)
```

### "¿Qué pasa si me equivoco en el commit?"

No problem, puedes revertir:
```bash
git revert HEAD  # Crea nuevo commit que deshace el anterior
git push origin feature/mi-feature
```

### "¿Debo hacer rebase?"

En 90% de casos, NO. GitHub maneja merges automático.

Solo si tu branch está atrás de develop:
```bash
git fetch origin
git rebase origin/develop
git push -f origin feature/tu-feature  # ⚠️ Force push
```

---

## Checklist Pre-Push (copy-paste)

```bash
# Antes de: git push

# 1. Tests pasan?
pytest tests/unit/ -v

# 2. Lint pasa?
pylint src/

# 3. Code formateado?
black src/

# 4. ¿Hay secretos?
git diff --staged | grep -E "(password|key|token)" && echo "❌ SECRETS!" || echo "✅ OK"

# 5. Commits claros?
git log origin/develop..HEAD --oneline

# 6. Ready?
git push
```

---

## Contacto Inter-Pueblos

**Reunión semanal:** Lunes 10:00 UTC (asíncrona en GitHub)

**Status format:**
```
**Tu Nombre (Pueblo X):**
- ✅ Completado: Feature X (PR #45)
- 🚧 Working: Feature Y (ETA: Viernes)
- ❓ Blocker: Issue #67 (esperando review)
```

**Code reviews:** Máximo 24h respuesta

---

## 🚀 ¡Ya estás listo!

**Siguiente paso:** Ve a Issues, elige un `phase-0` y abre una rama.

Preguntas? Lee `ENGINEERING-GUIDELINES.md` (seccion: Buenas Prácticas).

¡A codear! 💪
