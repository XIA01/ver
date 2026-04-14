# 👁️ GAZE-INFERENCE - Active Inference Gaze Tracking System

**Codename:** Soria-Gaze 2026  
**Framework:** Active Inference (Friston) + Deep Learning (PyTorch/KAN)  
**Environment:** Linux (X11/Wayland)  
**Hardware:** NVIDIA RTX 3060 + Logitech C920  
**Target Latency:** < 15ms

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Run tests (verify setup)
pytest tests/

# 3. Run application
python scripts/run.py
```

## 📚 Documentation

**First time here?**
→ Read [`START-HERE.md`](START-HERE.md) (5 minutes)

**Getting started with development?**
→ Read [`QUICK-START.md`](QUICK-START.md) (15 minutes)

**Need to know how to do something?**
→ Search in [`ENGINEERING-GUIDELINES.md`](ENGINEERING-GUIDELINES.md) (the bible)

**Understand the architecture?**
→ Read [`GAZE-INFERENCE-ROADMAP.md`](GAZE-INFERENCE-ROADMAP.md) (15 minutes)

**Lost? See all docs:**
→ Check [`DOCUMENTATION-INDEX.md`](DOCUMENTATION-INDEX.md)

---

## 🏗️ Project Structure

```
gaze-inference/
├── src/                    # Source code (3 layers)
│   ├── sensorium/         # 🎥 Perception (MediaPipe, OpenCV)
│   ├── brain/             # 🧠 Inference (KAN, Friston)
│   ├── overlay/           # 🖥️ Interface (PyQt6)
│   └── utils/             # Helpers
├── tests/                 # Test suite (unit, integration, e2e)
├── scripts/               # Executable scripts
├── data/                  # Datasets and models
├── docs/                  # Architecture docs
└── notebooks/             # Jupyter for analysis
```

---

## 🎯 Current Phase

**Phase 0: Latency Validation**
- ✅ Setup complete
- 🚧 Implement camera capture (validate_latency.py)
- 🚧 MediaPipe integration test
- 🚧 PyQt6 rendering test
- [ ] Full pipeline latency < 50ms

See [`GAZE-INFERENCE-ROADMAP.md`](GAZE-INFERENCE-ROADMAP.md) for full roadmap.

---

## 🛠️ Available Commands

```bash
make test              # Run all tests
make lint              # Check code quality
make format            # Format code automatically
make run-app           # Run application
make benchmark         # Benchmark latency
make clean             # Clean temp files
make help              # See all commands
```

---

## 📋 Contributing

1. Read [`START-HERE.md`](START-HERE.md)
2. Follow [`ENGINEERING-GUIDELINES.md`](ENGINEERING-GUIDELINES.md)
3. Make a branch: `git checkout -b feature/your-feature`
4. Write tests first (TDD)
5. Submit PR with description

---

## 📊 Technology Stack

| Layer | Module | Technology |
|-------|--------|-----------|
| **Perception** | Vision API | MediaPipe |
| | Capture | OpenCV |
| **Inference** | Model | PyTorch KAN |
| | Active Inference | JAX |
| | Optimization | TensorRT |
| **Interface** | Overlay | PyQt6 |

---

## 🧪 Testing

```bash
pytest                   # All tests
pytest -v              # Verbose
pytest tests/unit/     # Unit tests only
pytest -m "not slow"   # Skip slow tests
pytest --cov=src       # With coverage
```

---

## 📞 Support

- **Questions?** → Check [`ENGINEERING-GUIDELINES.md`](ENGINEERING-GUIDELINES.md)
- **Bug?** → Open GitHub issue
- **Stuck?** → See [`START-HERE.md`](START-HERE.md) → FAQ section

---

**Status:** 🟡 Phase 0 (Latency Validation)  
**Last Updated:** 2026-04-13  
**License:** MIT

🚀 Ready to begin Phase 0?
