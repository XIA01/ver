# 🛠️ ENGINEERING GUIDELINES - Proyecto GAZE-INFERENCE

**Guía práctica de desarrollo para equipo distribuido**  
Última actualización: 2026-04-13

---

## 📌 Índice Rápido

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Workflow Git](#workflow-git)
3. [Estándares de Código](#estándares-de-código)
4. [Testing](#testing)
5. [Documentación](#documentación)
6. [Comunicación y Tracking](#comunicación-y-tracking)
7. [Buenas Prácticas](#buenas-prácticas)
8. [Debugging y Logs](#debugging-y-logs)

---

## 🗂️ Estructura del Proyecto

### Directorios Canónicos

```
gaze-inference/
├── .github/
│   ├── workflows/              # CI/CD (GitHub Actions)
│   │   ├── test.yml
│   │   ├── lint.yml
│   │   └── deploy.yml
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuración centralizada
│   ├── logger.py               # Sistema de logging global
│   │
│   ├── sensorium/              # 🎥 Capa de Percepción
│   │   ├── __init__.py
│   │   ├── camera.py           # Captura de C920
│   │   ├── mediapipe_adapter.py# MediaPipe wrapper
│   │   ├── feature_extractor.py# Vector de características
│   │   └── tests/
│   │       └── test_feature_extractor.py
│   │
│   ├── brain/                  # 🧠 Capa de Inferencia
│   │   ├── __init__.py
│   │   ├── kan_model.py        # Arquitectura KAN
│   │   ├── active_inference.py # Friston loop
│   │   ├── trainer.py          # Training loop
│   │   ├── data.py             # DataLoaders PyTorch
│   │   └── tests/
│   │       ├── test_kan_model.py
│   │       └── test_active_inference.py
│   │
│   ├── overlay/                # 🖥️ Capa de Interfaz
│   │   ├── __init__.py
│   │   ├── qt_app.py           # PyQt6 main window
│   │   ├── widgets.py          # Custom widgets
│   │   ├── styles.py           # QSS (Qt StyleSheets)
│   │   └── tests/
│   │       └── test_overlay.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── metrics.py          # Latencia, precisión
│       ├── validators.py       # Validadores de entrada
│       └── file_io.py          # Persistencia
│
├── data/
│   ├── calibration/            # 📊 Datasets de usuario
│   │   └── .gitkeep
│   ├── models/                 # 🤖 Checkpoints
│   │   └── .gitkeep
│   └── raw/                    # Datos sin procesar
│       └── .gitkeep
│
├── scripts/
│   ├── validate_latency.py     # Testing básico
│   ├── calibrate.py            # Modo training
│   ├── run.py                  # App principal
│   └── benchmark.py            # Profiling
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures de pytest
│   ├── integration/
│   │   └── test_full_pipeline.py
│   └── e2e/
│       └── test_user_flow.py
│
├── docs/
│   ├── ARCHITECTURE.md         # Diseño técnico deep-dive
│   ├── API.md                  # API reference
│   ├── DEPLOYMENT.md           # Cómo hacer deploy
│   └── TROUBLESHOOTING.md      # FAQ de problemas comunes
│
├── notebooks/                  # 📓 Jupyter para análisis
│   ├── .gitignore
│   └── 01_data_exploration.ipynb
│
├── .gitignore                  # ⬇️ Ver sección Git
├── pyproject.toml              # Dependencias + config
├── requirements.txt            # Pinned versions
├── requirements-dev.txt        # Herramientas de desarrollo
├── pytest.ini                  # Config de testing
├── .pylintrc                   # Linting config
├── Makefile                    # Tasks comunes
└── README.md                   # Entry point
```

### Convención de Nombres

```python
# Módulos (snake_case)
feature_extractor.py
active_inference.py

# Clases (PascalCase)
class FeatureExtractor:
class KANModel:
class ActiveInferenceLoop:

# Funciones y métodos (snake_case)
def extract_features(frame):
def compute_free_energy(state):

# Constantes (UPPER_SNAKE_CASE)
MAX_FRAME_BUFFER = 100
DEFAULT_LEARNING_RATE = 0.001

# Variables privadas (_leading underscore)
_internal_state = []
_cached_result = None
```

---

## 🔄 Workflow Git

### Setup Inicial (Cada Ingeniero)

```bash
# 1. Clonar repo
git clone https://github.com/tu-org/gaze-inference.git
cd gaze-inference

# 2. Crear rama local de desarrollo
git checkout -b dev

# 3. Instalar dependencias
python -m venv venv
source venv/bin/activate  # o: venv\Scripts\activate (Windows)
pip install -r requirements-dev.txt

# 4. Configurar git localmente
git config user.name "Tu Nombre"
git config user.email "tu.email@tu-pueblo.com"
```

### Ramas: Convención Strict

```
main              ← Código de producción (protegido, requiere PR)
├── develop       ← Integración continua (rama base para features)
│   ├── feature/latency-validation      ← Nueva característica
│   ├── feature/kan-model               ← Nueva característica
│   ├── fix/mediapipe-crash             ← Bug fix
│   ├── docs/architecture-guide         ← Documentación
│   └── refactor/data-pipeline          ← Refactorización
└── hotfix/gpu-memory-leak              ← Urgente (de main)
```

**Regla de oro:** Nunca commits directos a `main` o `develop`. Todo via Pull Request.

### Flujo de Commits

```bash
# 1. Crear rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/tu-feature

# 2. Hacer cambios en pequeños commits
git add src/module/file.py
git commit -m "type(scope): descripción breve"

# 3. Antes de push, rebase sobre develop (mantener historia limpia)
git fetch origin
git rebase origin/develop
# Si hay conflictos: resolver, git add ., git rebase --continue

# 4. Push a rama remota
git push -u origin feature/tu-feature

# 5. Crear Pull Request en GitHub
# (Link automatizado después del push)
```

### Formato de Commits: Conventional Commits

```
type(scope): subject

body

footer
```

**Tipos válidos:**
- `feat`: Nueva característica
- `fix`: Bug fix
- `docs`: Cambios de documentación
- `style`: Formato, espacios, imports (sin lógica)
- `refactor`: Refactorización de código
- `perf`: Optimización de rendimiento
- `test`: Agregar/modificar tests
- `ci`: Cambios en CI/CD
- `chore`: Mantenimiento (deps, etc)

**Ejemplos reales:**

```bash
# ✅ BUENO
git commit -m "feat(sensorium): add pupil detection via CNN

- Implement 64x64 ROI extraction around eyes
- Train small CNN for pupil centroid localization
- Add unit tests for ROI handling

Closes #42"

# ✅ BUENO
git commit -m "fix(brain): fix gradient explosion in KAN training

Use gradient clipping (max_norm=1.0) to stabilize backprop.

Ref: #57"

# ❌ MALO
git commit -m "updated code"
git commit -m "fixed stuff"
git commit -m "WIP"
```

### Pull Requests: Template Obligatorio

**Crear PR → GitHub usará template automático:**

```markdown
## 📋 Descripción
Una línea clara de qué hace este PR.

## 🎯 Relacionado a
Closes #123 (número de issue)

## 🔍 Cambios principales
- [ ] Cambio 1
- [ ] Cambio 2
- [ ] Test agregado

## ✅ Testing
- [ ] Tests locales pasan (`pytest`)
- [ ] Lint pasa (`pylint`)
- [ ] Latencia verificada (si corresponde)

## 📸 Screenshots/Evidencia
(Si es UI, adjunta antes/después)

## 🚨 Breaking Changes?
No / Sí (describir impacto)
```

**Proceso de revisión:**

1. **Revisor 1** (del otro pueblo) hace review de código
2. **Autor** responde comentarios con commits claros
3. **Revisor 2** (opcional, si es crítico) valida cambios
4. **Merge** solo si CI/CD pasa + al menos 1 aprobación

### Tags y Versioning

```bash
# Al hacer release de fase completada:
git tag -a v0.1.0-phase-1 -m "Phase 1: Latency Validation Complete"
git push origin v0.1.0-phase-1

# Ver tags existentes
git tag -l
```

---

## 💻 Estándares de Código

### Python: Estilo y Formatting

**Enforced by: Black + Pylint**

```bash
# Instalado en requirements-dev.txt
pip install black pylint pytest-pylint

# Antes de cada commit:
black src/
pylint src/
```

**Ejemplo de código correcto:**

```python
"""
module.py: Feature extraction from eye regions.

Implements landmark detection and ROI extraction using MediaPipe.
"""

from typing import Tuple, List, Optional
import numpy as np
import cv2
from mediapipe.python.solutions import face_mesh

# Constantes a nivel módulo
DEFAULT_ROI_SIZE = 64
MAX_LANDMARKS = 468


class FeatureExtractor:
    """Extrae características biométricas de los ojos.
    
    Atributos:
        roi_size (int): Tamaño del recorte alrededor de pupila.
        detector (face_mesh.FaceMesh): Detector de MediaPipe.
    """

    def __init__(self, roi_size: int = DEFAULT_ROI_SIZE):
        """Inicializa el extractor.
        
        Args:
            roi_size: Dimensión del ROI cuadrado (píxeles).
            
        Raises:
            ValueError: Si roi_size < 32.
        """
        if roi_size < 32:
            raise ValueError("roi_size must be >= 32")
        
        self.roi_size = roi_size
        self.detector = face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.7
        )

    def extract_features(
        self, 
        frame: np.ndarray
    ) -> Tuple[Optional[np.ndarray], dict]:
        """Extrae vector de características de un frame.
        
        Args:
            frame: Array OpenCV (H, W, 3) en RGB.
            
        Returns:
            Tupla (features, metadata):
            - features: Array (16,) con coordenadas + head pose
            - metadata: Dict con confianza, validez
            
        Example:
            >>> extractor = FeatureExtractor()
            >>> features, meta = extractor.extract_features(frame)
            >>> if meta['valid']:
            ...     model.predict(features)
        """
        # Detección
        results = self.detector.process(frame)
        
        if not results.multi_face_landmarks:
            return None, {"valid": False, "reason": "no_face"}
        
        face = results.multi_face_landmarks[0]
        
        # Extraer coordenadas
        left_eye = self._get_eye_region(face, indices=[33, 160, 158, 133])
        right_eye = self._get_eye_region(face, indices=[263, 387, 386, 362])
        
        # Head pose (simplificado)
        head_pose = self._estimate_head_pose(face)
        
        # Concatenar vector
        features = np.concatenate([
            left_eye.flatten(),
            right_eye.flatten(),
            head_pose
        ]).astype(np.float32)
        
        return features, {
            "valid": True,
            "confidence": results.multi_face_landmarks[0].landmark[0].z
        }

    def _get_eye_region(
        self, 
        face: "face_mesh.FaceLandmark", 
        indices: List[int]
    ) -> np.ndarray:
        """Extrae región del ojo (4 puntos)."""
        points = np.array([
            [face.landmark[i].x, face.landmark[i].y] 
            for i in indices
        ])
        return points

    def _estimate_head_pose(self, face: "face_mesh.FaceLandmark") -> np.ndarray:
        """Calcula (pitch, yaw, roll) simplificado."""
        # Implementación real usaría geometría 3D
        return np.zeros(3, dtype=np.float32)
```

**Checklist de código:**

- [ ] Docstrings en todas las clases y funciones públicas
- [ ] Type hints en firmas de funciones
- [ ] Sin líneas > 100 caracteres
- [ ] Imports organizados: stdlib → third-party → local
- [ ] No hay `print()`: usar logger
- [ ] No hay `import *`
- [ ] Exceptions específicas, no bare `except:`

### PyTorch: Convenciones

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

class KANModel(nn.Module):
    """Kolmogorov-Arnold Network para regresión de gaze."""
    
    def __init__(self, input_dim: int = 16, output_dim: int = 2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.
        
        Args:
            x: (batch_size, input_dim) tensor
            
        Returns:
            (batch_size, output_dim) predictions
        """
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


# Training loop pattern
def train_epoch(model, dataloader, optimizer, criterion, device):
    """Entrena una época."""
    model.train()
    total_loss = 0.0
    
    for batch_idx, (x, y) in enumerate(dataloader):
        x, y = x.to(device), y.to(device)
        
        optimizer.zero_grad()
        pred = model(x)
        loss = criterion(pred, y)
        loss.backward()
        
        # Gradient clipping para estabilidad
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
        total_loss += loss.item()
    
    return total_loss / len(dataloader)
```

### JAX: Convenciones (Active Inference)

```python
import jax
import jax.numpy as jnp
from jax import grad, jit

@jit  # Compilación JIT para velocidad
def compute_free_energy(q: jnp.ndarray, mu: jnp.ndarray, sigma: float) -> float:
    """Energía libre variacional.
    
    Args:
        q: Estado actual (x, y)
        mu: Media predicha (x, y)
        sigma: Varianza (incertidumbre)
        
    Returns:
        F: Energía libre escalar
    """
    mse = jnp.sum((q - mu) ** 2)
    return mse / (2 * sigma ** 2) + 0.5 * jnp.log(2 * jnp.pi * sigma ** 2)


@jit
def gradient_step(q: jnp.ndarray, mu: jnp.ndarray, sigma: float, dt: float):
    """Un paso del integrador ODE.
    
    dq/dt = -∂F/∂q
    """
    grad_f = grad(compute_free_energy)
    g = grad_f(q, mu, sigma)
    return q - dt * g
```

---

## 🧪 Testing

### Filosofía: Test-Driven Development (TDD)

1. **Escribe test primero** (rojo)
2. **Implementa lo mínimo** para pasar (verde)
3. **Refactoriza** manteniendo tests verdes (azul)

### Estructura de Tests

```
tests/
├── conftest.py          # Fixtures compartidas
├── unit/
│   ├── test_feature_extractor.py
│   ├── test_kan_model.py
│   └── test_active_inference.py
├── integration/
│   └── test_sensorium_to_brain.py
└── e2e/
    └── test_full_pipeline.py
```

### Ejemplo: Unit Test

```python
# tests/unit/test_feature_extractor.py

import pytest
import numpy as np
import cv2
from src.sensorium.feature_extractor import FeatureExtractor


@pytest.fixture
def extractor():
    """Fixture de FeatureExtractor."""
    return FeatureExtractor(roi_size=64)


@pytest.fixture
def dummy_frame():
    """Frame dummy para testing (sin cara real)."""
    return np.zeros((480, 640, 3), dtype=np.uint8)


class TestFeatureExtractor:
    """Suite de tests para FeatureExtractor."""
    
    def test_init_valid_roi_size(self):
        """Test inicialización con ROI válido."""
        extractor = FeatureExtractor(roi_size=64)
        assert extractor.roi_size == 64
    
    def test_init_invalid_roi_size(self):
        """Test inicialización con ROI inválido."""
        with pytest.raises(ValueError, match="roi_size must be >= 32"):
            FeatureExtractor(roi_size=16)
    
    def test_extract_features_no_face(self, extractor, dummy_frame):
        """Test extracción en frame sin cara."""
        features, meta = extractor.extract_features(dummy_frame)
        
        assert features is None
        assert meta["valid"] is False
        assert "no_face" in meta.get("reason", "")
    
    @pytest.mark.requires_real_camera  # Skip en CI
    def test_extract_features_with_face(self, extractor):
        """Test extracción con cara real.
        
        NOTA: Requiere cámara conectada. Skip en CI.
        """
        # Capturar frame real
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            pytest.skip("Camera not available")
        
        features, meta = extractor.extract_features(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        assert meta["valid"]
        assert features is not None
        assert features.shape == (16,)
        assert features.dtype == np.float32
```

### Ejemplo: Integration Test

```python
# tests/integration/test_sensorium_to_brain.py

import pytest
import torch
from src.sensorium.feature_extractor import FeatureExtractor
from src.brain.kan_model import KANModel


class TestSensoriumToBrain:
    """Test pipeline completo: captura → modelo."""
    
    @pytest.fixture
    def pipeline(self):
        extractor = FeatureExtractor()
        model = KANModel(input_dim=16, output_dim=2)
        return extractor, model
    
    def test_feature_to_model_dtype_compatibility(self, pipeline):
        """Test que features de sensorium → model sin casting."""
        extractor, model = pipeline
        
        # Feature mock
        features = torch.randn(1, 16, dtype=torch.float32)
        
        # Forward pass
        output = model(features)
        
        assert output.shape == (1, 2)
        assert output.dtype == torch.float32
```

### Ejemplo: Latency Test

```python
# tests/test_latency.py

import pytest
import time
import numpy as np
from src.sensorium.feature_extractor import FeatureExtractor


class TestLatency:
    """Tests de latencia real."""
    
    @pytest.mark.benchmark
    def test_mediapipe_latency(self, benchmark):
        """MediaPipe debe procesar en < 30ms."""
        extractor = FeatureExtractor()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        def run():
            extractor.extract_features(dummy_frame)
        
        result = benchmark(run)
        
        # Pytest-benchmark reports: mean, stdev, min, max
        assert result.stats.mean < 0.03  # 30ms
```

### Correr Tests Localmente

```bash
# Todos los tests
pytest

# Solo unit tests
pytest tests/unit/

# Con cobertura
pytest --cov=src --cov-report=html

# Modo verbose
pytest -v

# Apenas un test
pytest tests/unit/test_feature_extractor.py::TestFeatureExtractor::test_init_valid_roi_size

# Tests que pasen rápido (skip slowest)
pytest -m "not slow"
```

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: tests que toman > 5 segundos
    requires_real_camera: requieren C920 conectada
    benchmark: tests de latencia/performance
    integration: tests de múltiples componentes
```

---

## 📚 Documentación

### Docstrings: Google Style (Enforced)

```python
def compute_free_energy(
    q: np.ndarray,
    mu: np.ndarray,
    sigma: float
) -> float:
    """Calcula la energía libre variacional.
    
    Implementa la fórmula de Friston para minimización
    de incertidumbre.
    
    Args:
        q: Vector de estado actual (x, y). Shape (2,).
        mu: Predicción del modelo (x, y). Shape (2,).
        sigma: Desviación estándar (escala de incertidumbre).
        
    Returns:
        Energía libre F como escalar float.
        
    Raises:
        ValueError: Si sigma <= 0.
        TypeError: Si shapes incompatibles.
        
    Example:
        >>> q = np.array([100, 200])
        >>> mu = np.array([105, 195])
        >>> F = compute_free_energy(q, mu, sigma=10.0)
        >>> F < 1.0  # Bajo si predicción cercana
        True
        
    Note:
        Fórmula: F = ||q - mu||² / (2σ²) + 0.5 * log(2πσ²)
        
    References:
        Friston, K. (2010). The free-energy principle: a unified brain theory?
    """
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    
    mse = np.sum((q - mu) ** 2)
    return mse / (2 * sigma ** 2) + 0.5 * np.log(2 * np.pi * sigma ** 2)
```

### README.md: Estructura

```markdown
# GAZE-INFERENCE

Brief one-liner descripción.

## Quick Start

## Installation

pip install -r requirements.txt

## Usage

```python
from src.sensorium import FeatureExtractor
extractor = FeatureExtractor()
```

## Architecture

[Link a ARCHITECTURE.md]

## Contributing

[Link a ENGINEERING-GUIDELINES.md]

## License

MIT
```

### API.md: Referencia Completa

```markdown
# API Reference

## sensorium.feature_extractor

### FeatureExtractor

```python
class FeatureExtractor:
    def __init__(self, roi_size: int = 64) -> None: ...
    def extract_features(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]: ...
```

[Detalles...]
```

### ARCHITECTURE.md: Deep Dive (already created)

Enlaza a la documentación técnica detallada.

---

## 💬 Comunicación y Tracking

### Issues: Plantilla Obligatoria

**Bug Report:**
```markdown
### Descripción
[Descripción clara del bug]

### Pasos para reproducir
1. ...
2. ...

### Comportamiento esperado
[Qué debería pasar]

### Comportamiento actual
[Qué pasa]

### Logs/Evidencia
[Adjunta logs, screenshots]

### Información del ambiente
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.10.2]
- GPU: [e.g., RTX 3060]
```

**Feature Request:**
```markdown
### Descripción
[Nueva característica]

### Caso de uso
[Por qué es útil]

### Aceptación
- [ ] Criterio 1
- [ ] Criterio 2

### Estimación
[No binding, solo orientativa]
```

### Tracking: Labels en GitHub

```
type:
  - bug
  - feature
  - documentation
  - refactor
  - performance

priority:
  - critical (bloquea release)
  - high (importante, pero no crítico)
  - medium
  - low (nice-to-have)

component:
  - sensorium
  - brain
  - overlay
  - infrastructure

phase:
  - phase-0-latency
  - phase-1-calibration
  - phase-2-kan
  - phase-3-friston
  - phase-4-online-training
  - phase-5-ui
```

### Reunión Semanal (Asíncrona)

**Lunes 10:00 UTC:**

1. Status updates en un issue pinned (async)
   ```
   **Engineer A (Pueblo X):**
   - ✅ Feature X completado (PR #45)
   - 🚧 Working on Feature Y (blocker: issue #67)
   - 🔍 Questions: [...clarify...]
   
   **Engineer B (Pueblo Y):**
   - ...
   ```

2. Code reviews: turno rápido (máximo 24h respuesta)

3. Issue prioritization: team async-votes con reactions (:+1: :confused:)

---

## ✨ Buenas Prácticas

### 1. No Hardcodes: Usa config.py

```python
# ❌ MALO
class FeatureExtractor:
    def __init__(self):
        self.roi_size = 64
        self.confidence_threshold = 0.7

# ✅ BUENO
from src.config import Config

class FeatureExtractor:
    def __init__(self, config: Config):
        self.roi_size = config.sensorium.roi_size
        self.confidence_threshold = config.sensorium.confidence_threshold
```

**src/config.py:**
```python
from dataclasses import dataclass

@dataclass
class SensoriumConfig:
    roi_size: int = 64
    confidence_threshold: float = 0.7
    camera_index: int = 0

@dataclass
class Config:
    sensorium: SensoriumConfig = dataclass(SensoriumConfig)
    # ... más secciones
```

### 2. Versionado de Modelos

```python
# Siempre guardar metadata
checkpoint = {
    "model_state": model.state_dict(),
    "optimizer_state": optimizer.state_dict(),
    "epoch": epoch,
    "loss": loss,
    "timestamp": datetime.now().isoformat(),
    "git_commit": get_git_commit_hash(),  # Reproducibilidad
    "hyperparams": {
        "lr": 0.001,
        "batch_size": 32,
    }
}

torch.save(checkpoint, "models/kan_v0.1.0-phase2.pt")
```

### 3. Logging, No Print

```python
import logging

logger = logging.getLogger(__name__)

# ❌ MALO
print("Training started")
print(f"Epoch {epoch}, Loss: {loss}")

# ✅ BUENO
logger.info("Training started")
logger.debug(f"Epoch {epoch}, Loss: {loss}")
logger.warning("Low GPU memory detected")
logger.error("Failed to load model: {error}")
```

**Configuración centralizada (src/logger.py):**
```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'detailed',
            'filename': 'logs/app.log',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 4. Type Hints Estrictos

```python
# ❌ MALO
def process(data):
    return data + 1

# ✅ BUENO
from typing import Union

def process(data: Union[int, float]) -> Union[int, float]:
    """Process numeric data."""
    if not isinstance(data, (int, float)):
        raise TypeError(f"Expected numeric, got {type(data)}")
    return data + 1
```

### 5. Error Handling Específico

```python
# ❌ MALO
try:
    model = load_model(path)
except:
    print("Error")

# ✅ BUENO
try:
    model = load_model(path)
except FileNotFoundError:
    logger.error(f"Model not found at {path}")
    raise
except torch.cuda.OutOfMemoryError:
    logger.error("GPU out of memory, trying CPU fallback")
    model = load_model(path, device='cpu')
except Exception as e:
    logger.error(f"Unexpected error loading model: {e}", exc_info=True)
    raise
```

### 6. Performance Profiling

```bash
# PyTorch profiling
python -m cProfile -s cumtime scripts/run.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler scripts/run.py

# GPU profiling (NVIDIA)
pip install nvidia-ml-py
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used --format=csv
```

### 7. Reproducibilidad: Seed Fijo

```python
import random
import numpy as np
import torch

def set_seed(seed: int = 42):
    """Set seed para reproducibilidad."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False  # ⚠️ Más lento pero reproducible

# En main()
if __name__ == "__main__":
    set_seed(42)
    # ... rest of code
```

---

## 🐛 Debugging y Logs

### Logging Levels (Qué usar)

```python
logger.debug("Detailed info, variables intermediate")    # Develop
logger.info("Confirmaciones de progreso normal")          # Production
logger.warning("Algo inesperado, pero sigue funcionando") # Atentar
logger.error("Algo falló, pero continúa")                 # Crítico
logger.critical("Sistema inutilizable")                   # Crash
```

### Ejemplo Real: Pipeline Debugging

```python
def train_step(model, batch, device, logger):
    """Un paso de entrenamiento con logging detallado."""
    
    x, y = batch
    logger.debug(f"Batch shapes: x={x.shape}, y={y.shape}")
    
    x, y = x.to(device), y.to(device)
    logger.debug(f"Moved to device: {device}")
    
    try:
        pred = model(x)
        logger.debug(f"Prediction shape: {pred.shape}")
    except RuntimeError as e:
        logger.error(f"Forward pass failed: {e}", exc_info=True)
        raise
    
    loss = criterion(pred, y)
    logger.debug(f"Loss: {loss.item():.4f}")
    
    if loss.item() > 1e6:
        logger.warning(f"Very high loss detected: {loss.item()}")
    
    loss.backward()
    logger.debug("Backward pass completed")
    
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    logger.debug(f"Gradient norm before clipping: {grad_norm}")
    
    optimizer.step()
    logger.info(f"Epoch {epoch}, Loss: {loss.item():.4f}")
    
    return loss.item()
```

### Dump de Estado para Debugging

```python
def dump_debug_info(model, batch, output_path="debug_dump.pkl"):
    """Guardar estado del sistema para investigación offline."""
    import pickle
    
    debug_dict = {
        "model_state": model.state_dict(),
        "model_config": model.__dict__,
        "batch_input": batch[0].cpu().numpy(),
        "batch_target": batch[1].cpu().numpy(),
        "timestamp": datetime.now().isoformat(),
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(debug_dict, f)
    
    logger.info(f"Debug dump saved to {output_path}")
```

### Checklist Pre-Push

```bash
# Antes de hacer git push:

# 1. Tests locales
pytest -v

# 2. Linting
pylint src/

# 3. Type checking (opcional pero recomendado)
pip install mypy
mypy src/

# 4. No credentials
git diff --staged | grep -E "(password|key|token|secret)" && echo "❌ SECRETS DETECTED!" || echo "✅ No secrets"

# 5. Commits limpios
git log --oneline -5  # Revisar que sean descriptivos

# 6. No conflictos sin resolver
git status | grep "CONFLICT" && echo "❌ Unresolved conflicts" || echo "✅ Clean"
```

---

## 🎬 Quick Cheat Sheet

```bash
# Setup día 1
git clone <repo>
cd gaze-inference
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install  # Si existe pre-commit config

# Día a día
git checkout develop && git pull
git checkout -b feature/my-feature
# ... código ...
pytest
black src/ && pylint src/
git add src/
git commit -m "feat(module): description"
git push -u origin feature/my-feature
# -> Abre PR en GitHub

# Mergear PR (después de review + CI pass)
git checkout develop
git pull origin develop
git merge origin/feature/my-feature
git push origin develop

# Release de fase
git tag -a v0.X.Y-phase-N -m "Description"
git push origin v0.X.Y-phase-N
```

---

## 📋 Checklist para Nueva Tarea

Antes de empezar a codear:

- [ ] Issue creado con descripción clara
- [ ] Rama creada desde `develop` con nombre correcto
- [ ] Dependencias instaladas en venv
- [ ] Test escrito (antes del código)
- [ ] Código implementado
- [ ] Tests pasan (100% de cobertura para new code)
- [ ] Linting pasa
- [ ] Docstrings completos
- [ ] Commit message en Conventional Commits
- [ ] PR creado con template
- [ ] Al menos 1 review antes de merge

---

## 🆘 Problemas Comunes

### "Latencia aumentó después de mi cambio"

1. Ejecuta benchmark:
   ```bash
   pytest tests/test_latency.py -v
   ```

2. Profile el código:
   ```bash
   python -m cProfile -s cumtime scripts/run.py > profile.txt
   cat profile.txt | head -20
   ```

3. Revert y re-apply en pasos:
   ```bash
   git revert HEAD  # Revierte tu último commit
   # Ahora verifica que latencia bajó
   # Luego re-aplica cambios más pequeños
   ```

### "Test falla localmente pero pasa en CI"

- Seed no fijo → `set_seed(42)` en inicio
- Paths absolutos vs relativos → usar `Path(__file__).parent`
- GPU vs CPU → fuerza CPU en test: `device = "cpu"`

### "GPU out of memory"

```python
# Reducir batch size temporalmente
batch_size = 16  # en lugar de 32

# Limpiar cache
torch.cuda.empty_cache()

# Verificar quién usa memoria
import torch
print(torch.cuda.memory_summary())
```

---

**¡Listo para trabajar en equipo distribuido!** 🚀

Last updated: 2026-04-13
