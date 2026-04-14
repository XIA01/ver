# Proyecto GAZE-INFERENCE - Roadmap Técnico

**Codename:** Soria-Gaze 2026  
**Framework:** Active Inference (Friston) + Deep Learning (PyTorch/KAN)  
**Entorno:** Linux (X11/Wayland)  
**Hardware:** RTX 3060 + Webcam C920  
**Target Latencia:** < 15ms  

---

## 📋 Visión General

Sistema inteligente de seguimiento de mirada que no solo detecta dónde miras, sino que **entiende tu intención**. El cuadro verde en pantalla se mueve suavemente hacia donde tus ojos "quieren" ir, filtrando el ruido natural de la mirada humana mediante minimización de Energía Libre Variacional (Active Inference de Friston).

---

## 🏗️ Arquitectura del Sistema (3 Capas Desacopladas)

### A. Capa de Percepción (Sensorium)
**Responsabilidad:** Extraer biometría de la mirada en tiempo real

- **Detector de Landmarks:** MediaPipe → 468 puntos faciales
- **ROI Extracción:** Recortes de 64×64 píxeles centrados en pupilas
- **Vector de Características:**
  - Coordenadas (x, y, z) de párpados
  - Orientación de cabeza (Head Pose)
  - Centroide de pupila (CNN local en PyTorch)
- **Frecuencia:** 30/60 fps desde C920 vía OpenCV

### B. Capa de Inferencia (The Brain)
**Responsabilidad:** Predicción inteligente + aprendizaje online

- **Modelo Regresor:** Kolmogorov-Arnold Network (KAN)
  - Mapeo: vector de características → coordenadas (X, Y) en escritorio
  - Ventaja: Aprende funciones no-lineales complejas con pocos datos
- **Bucle Active Inference (Friston):**
  - Minimización: $\frac{dq}{dt} = -\frac{\partial F}{\partial q}$
  - El cuadro verde se mueve hacia predicción, no salta
  - Filtra sacádicos naturales de la mirada humana
- **Adaptación Incertidumbre:**
  - Baja luz o ojos erráticos → cuadro más grande (↑ incertidumbre)
  - Fijación estable → cuadro preciso (↓ incertidumbre)

### C. Capa de Interfaz (Overlay)
**Responsabilidad:** Renderizado transparente sobre cualquier aplicación

- **Framework:** PyQt6
- **Flags:** `Qt.WindowStaysOnTopHint` + `Qt.WA_TransparentForMouseEvents`
- **Comportamiento:** Visualiza cuadros sin bloquear clics del usuario
- **Elementos Visuales:**
  - Cuadro rojo: target de calibración
  - Cuadro verde: predicción en tiempo real
  - Indicador de confianza (tamaño/opacidad)

---

## 🛠️ Stack Técnico

| Capa | Módulo | Tecnología | Función |
|------|--------|-----------|---------|
| **Percepción** | Vision API | MediaPipe | Detección de landmarks (468 pts) |
| | Captura de Video | OpenCV | Streaming C920 a 30-60 fps |
| **Inferencia** | Modelo Regresor | PyTorch + JAX | Entrenamiento online KAN |
| | Active Inference | JAX | Bucle de minimización variacional |
| | Optimización | TensorRT | Ejecución ultra-rápida en RTX 3060 |
| **Interfaz** | Overlay | PyQt6 | Renderizado transparente en X11/Wayland |
| **Validación** | Testing | pytest + OpenCV | Latencia y precisión |

---

## 🎯 Roadmap de Implementación

### **Fase 0: Validación Básica de Latencia** (1-2 semanas)
**Objetivo:** Verificar que el stack funciona sin cuellos de botella

**Entregables:**
- [ ] Script de validación: punto en pantalla sigue nariz (MediaPipe + PyQt6)
- [ ] Medición de latencia (< 50ms acceptable para MVP)
- [ ] Configuración OpenCV + C920
- [ ] Pruebas de buffer de frames

**Checklist Técnico:**
- [ ] OpenCV lee frames de C920 a 30 fps
- [ ] MediaPipe procesa landmarks en < 30ms
- [ ] PyQt6 renderiza en pantalla sin parpadeos
- [ ] Latencia total medible y documentada

**Criterio de éxito:** Punto rojo sigue nariz suavemente, sin lag perceptible

---

### **Fase 1: Calibración Online (Training Mode)** (2-3 semanas)
**Objetivo:** Sistema aprende tu geometría facial individual

**Entregables:**
- [ ] Modo de calibración interactivo (5-10 minutos)
- [ ] Generador de targets aleatorios (cuadro rojo)
- [ ] Captura de pares (entrada: estado ojos, label: posición pantalla)
- [ ] Dataset persistente (SQLite o JSON)

**Arquitectura:**
```
Loop de Calibración:
1. Dibujar target rojo en (X_random, Y_random)
2. Usuario fija mirada durante 1 seg
3. Capturar vector de características + timestamp
4. Almacenar par (features, X, Y)
5. Visualizar feedback ("Éxito" / "Reintenta")
6. Repetir 20-30 veces (coverage: 4 cuadrantes + centro)
```

**Checklist:**
- [ ] MediaPipe extrae coordenadas (x, y, z) párpados + head pose
- [ ] CNN pequeña localiza centroide pupila (retrain each session)
- [ ] Dataset > 100 samples sin artefactos
- [ ] Validación: cross-validation del regresor

**Criterio de éxito:** Modelo KAN entrenado, MSE < 50 píxeles

---

### **Fase 2: Regresor KAN (Base de Predicción)** (2-3 semanas)
**Objetivo:** Modelo que mapea características oculares → coordenadas pantalla

**Entregables:**
- [ ] Arquitectura KAN inicial (2-3 capas, 64 neuronas)
- [ ] Dataloader PyTorch (batch = 32)
- [ ] Loop de entrenamiento (SGD/Adam, 50 épocas)
- [ ] Validación: métricas L1/L2 error en píxeles
- [ ] Exportación a TensorRT para RTX 3060

**Especificaciones:**
- **Input:** Vector de 12-16 features (ojos + cabeza + pupila)
- **Output:** (X_pred, Y_pred) en rango [0, width] × [0, height]
- **Loss Function:** SmoothL1Loss (robusto a outliers)
- **Regularización:** L2 (λ=0.001) para evitar overfitting

**Checklist:**
- [ ] Arquitectura KAN definida y documentada
- [ ] Dataloaders con augmentation (pequeña rotación/ruido)
- [ ] Training loop con logging (W&B o TensorBoard)
- [ ] Validación en datos held-out (20% del dataset)
- [ ] TensorRT model compatible con RTX 3060

**Criterio de éxito:** MSE < 30 píxeles, inferencia < 10ms

---

### **Fase 3: Active Inference (Friston Loop)** (3-4 semanas)
**Objetivo:** Integrar minimización variacional para movimiento suave

**Entregables:**
- [ ] Modelo generativo (Gaussian belief sobre posición real)
- [ ] Cálculo de Energía Libre Variacional (F)
- [ ] Integrador ODE: $\frac{dq}{dt} = -\frac{\partial F}{\partial q}$
- [ ] Parámetros dinámicos: varianza (↑ en incertidumbre)

**Lógica del Bucle:**
```python
# Pseudocódigo
q = [0.5 * width, 0.5 * height]  # Estado actual del cuadro
variance = 1.0  # Incertidumbre inicial

while true:
    features = extract_from_webcam()
    mu_pred = kaned_model(features)  # Predicción puntual
    
    # Actualizar varianza según calidad de features
    confidence = evaluate_feature_quality(features)
    variance = 1.0 + (1 - confidence) * 5  # 1.0 a 6.0
    
    # Gradiente de energía libre
    grad_F = (q - mu_pred) / variance
    
    # Actualizar posición (Euler integrator)
    q = q - learning_rate * grad_F
    
    # Renderizar cuadro en posición q
    render_overlay(q, size=sqrt(variance))
```

**Checklist:**
- [ ] Modelo generativo con media/varianza
- [ ] Función de energía libre implementada (JAX)
- [ ] Integrador numérico estable (RK4 o similar)
- [ ] Parámetros ajustables: inertia, damping, variance_scale
- [ ] Visualización: cuadro cambia tamaño según confianza

**Criterio de éxito:** Cuadro sigue movimiento natural, filtra sacádicos, latencia < 15ms

---

### **Fase 4: Entrenamiento Online (Hot Training)** (2 semanas)
**Objetivo:** El modelo se adapta mientras usas el sistema

**Entregables:**
- [ ] Buffer circular de últimas 100 capturas
- [ ] Mini-batch training asíncrono (cada 500ms)
- [ ] Detección de drift (error creciente → reentrenamiento)
- [ ] Persistencia de pesos (checkpoint cada 5 minutos)

**Arquitectura:**
```
Thread de Captura → Cola de características
                  ↓
            Buffer (últimas 100)
                  ↓
Thread de Training → Mini-batches (32) → Actualizar pesos KAN
                                      → Actualizar dataloaders
```

**Checklist:**
- [ ] Queue thread-safe para características
- [ ] Mini-batch SGD con learning rate adaptativo
- [ ] Monitoreo de overfitting (validación en frames antiguos)
- [ ] Fallback a pesos anteriores si error sube

**Criterio de éxito:** Modelo se adapta a cambios de iluminación, ángulo cabeza

---

### **Fase 5: Interfaz Pulida y Configuración** (2 semanas)
**Objetivo:** UX profesional, ajustes finos de rendimiento

**Entregables:**
- [ ] UI de configuración (sensibilidad, tamaño cuadro, colores)
- [ ] Indicador de estado (calibración, entrenando, listo)
- [ ] Logs en archivo (debugging)
- [ ] Tema oscuro/claro según preferencia Linux
- [ ] Documentación de usuario

**Características Opcionales (MVP+):**
- [ ] Historial de puntos (trail del cuadro)
- [ ] Estadísticas de precisión en tiempo real
- [ ] Modo "foco" (bloquea cuadro en región)
- [ ] Hotkeys para calibración rápida

---

## ⚡ Requisitos de Hardware y Software

### Hardware
- **GPU:** NVIDIA RTX 3060 (cuota de 4GB suficiente)
- **Cámara:** Logitech C920 (USB 3.0 recomendado)
- **CPU:** 4+ cores (para MediaPipe + PyTorch simultáneamente)
- **RAM:** 8GB mínimo, 16GB recomendado

### Software Mínimo
```bash
Python 3.10+
torch==2.1.0
jax==0.4.11
pytorch-lightning==2.0  # Opcional pero recomendado
mediapipe==0.10
opencv-python==4.8
PyQt6==6.4
tensorrt==8.6  # Para RTX 3060
pytest==7.4
```

### SO y Display Server
- Linux (Ubuntu 22.04+ o Fedora 39+)
- X11 o Wayland (PyQt6 soporta ambos)
- Permisos de /dev/video0 para la cámara

---

## 📊 Métricas de Éxito

| Hito | Métrica | Target |
|------|---------|--------|
| **Fase 0** | Latencia punto-nariz | < 50ms |
| **Fase 1** | Dataset de calibración | > 100 muestras, MSE < 100px |
| **Fase 2** | Precisión regresor KAN | MSE < 30px, inferencia < 10ms |
| **Fase 3** | Suavidad movimiento | Sin saltos, filtrado de sacádicos |
| **Fase 4** | Adaptación online | Error ↓ 10% tras 5 min uso |
| **Fase 5** | Latencia end-to-end | < 15ms (medido en pantalla) |

---

## 🚀 Próximos Pasos Inmediatos

### Semana 1: Setup de Fase 0
1. **Clonar repositorio e instalar dependencias**
   ```bash
   pip install opencv-python PyQt6 mediapipe torch
   ```

2. **Script de validación básica** (`scripts/validate_latency.py`)
   - Capturar frames de C920 vía OpenCV
   - Detectar nariz con MediaPipe
   - Renderizar punto rojo en PyQt6
   - Medir latencia frame → pantalla

3. **Testing en hardware real**
   - Verificar que no hay lag perceptible
   - Documentar latencias observadas

### Semana 2-3: Preparación Fase 1
- Diseño de dataset y estructura de almacenamiento
- UI mockup para modo calibración
- Prototipo de captura de características

---

## 📁 Estructura de Directorios Sugerida

```
gaze-inference/
├── data/
│   ├── calibration/          # Datasets de usuario
│   └── models/               # Checkpoints KAN
├── src/
│   ├── sensorium/            # Percepción (MediaPipe, OpenCV)
│   ├── brain/                # Modelos KAN + Active Inference
│   ├── overlay/              # PyQt6 interface
│   └── utils/                # Helpers, logging
├── scripts/
│   ├── validate_latency.py
│   ├── calibrate.py
│   └── run.py                # App principal
├── tests/
│   ├── test_latency.py
│   └── test_kan_model.py
├── docs/
│   └── ARCHITECTURE.md
└── requirements.txt
```

---

## 🔗 Referencias y Conceptos

- **Active Inference:** Friston, K. (2010) "The Free-Energy Principle"
- **KAN:** Liu et al. "Kolmogorov-Arnold Networks"
- **MediaPipe Landmarks:** [Google MediaPipe Docs](https://mediapipe.dev)
- **PyQt6:** Documentación oficial de Riverbank
- **TensorRT:** Optimization guide para NVIDIA

---

**Última actualización:** 2026-04-13  
**Estado:** 🟡 Ready for Phase 0 (Latency Validation)
