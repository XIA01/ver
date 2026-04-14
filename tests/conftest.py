# tests/conftest.py
# Fixtures compartidas para todos los tests
# Se cargan automáticamente por pytest

import pytest
import numpy as np
from pathlib import Path
import tempfile
from unittest.mock import Mock

# Lazy imports para evitar problemas con CUDA en CI/CD
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None


# ============================================================================
# FIXTURES: General
# ============================================================================

@pytest.fixture
def tmp_data_dir():
    """Directorio temporal para datos de test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def device():
    """Device para PyTorch (GPU si disponible, sino CPU)."""
    if TORCH_AVAILABLE:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return "cpu"


@pytest.fixture
def seed():
    """Seed para reproducibilidad."""
    if TORCH_AVAILABLE:
        torch.manual_seed(42)
    np.random.seed(42)
    return 42


# ============================================================================
# FIXTURES: Datos Dummy
# ============================================================================

@pytest.fixture
def dummy_frame():
    """Frame dummy (480x640x3, RGB)."""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def dummy_features():
    """Vector de características dummy (16,)."""
    if TORCH_AVAILABLE:
        return torch.randn(16, dtype=torch.float32)
    return np.random.randn(16).astype(np.float32)


@pytest.fixture
def dummy_batch(device):
    """Batch de datos dummy para training.

    Returns:
        Tupla (x, y) donde:
        - x: (batch_size=32, 16) features
        - y: (batch_size=32, 2) targets (X, Y en pantalla)
    """
    if not TORCH_AVAILABLE:
        pytest.skip("PyTorch not available")

    x = torch.randn(32, 16, dtype=torch.float32, device=device)
    y = torch.randint(0, 1920, (32, 2), dtype=torch.float32, device=device)
    return x, y


@pytest.fixture
def dummy_dataset():
    """Dataset dummy con 100 muestras."""
    if not TORCH_AVAILABLE:
        pytest.skip("PyTorch not available")

    from torch.utils.data import TensorDataset

    X = torch.randn(100, 16)
    y = torch.randint(0, 1920, (100, 2), dtype=torch.float32)

    return TensorDataset(X, y)


@pytest.fixture
def dummy_dataloader(dummy_dataset):
    """DataLoader dummy con batch_size=8."""
    if not TORCH_AVAILABLE:
        pytest.skip("PyTorch not available")

    from torch.utils.data import DataLoader

    return DataLoader(dummy_dataset, batch_size=8, shuffle=True)


# ============================================================================
# FIXTURES: Modelos
# ============================================================================

@pytest.fixture
def kan_model(device):
    """Modelo KAN dummy para testing.

    Input: (batch, 16)
    Output: (batch, 2)
    """
    if not TORCH_AVAILABLE:
        pytest.skip("PyTorch not available")

    from src.brain.kan_model import KANModel

    model = KANModel(input_dim=16, output_dim=2)
    model.to(device)
    return model


@pytest.fixture
def trained_kan_model(kan_model, dummy_dataloader, device):
    """Modelo KAN pre-entrenado en dummy data (5 épocas)."""
    if not TORCH_AVAILABLE:
        pytest.skip("PyTorch not available")

    import torch.optim as optim

    model = kan_model
    model.train()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()

    for _ in range(5):
        for x, y in dummy_dataloader:
            x, y = x.to(device), y.to(device)

            optimizer.zero_grad()
            pred = model(x)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()

    model.eval()
    return model


# ============================================================================
# FIXTURES: Mocks (para tests sin hardware real)
# ============================================================================

@pytest.fixture
def mock_camera():
    """Mock de cámara (no requiere hardware real)."""
    mock = Mock()
    mock.read.return_value = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    mock.is_opened.return_value = True
    return mock


@pytest.fixture
def mock_mediapipe():
    """Mock de MediaPipe face detection."""
    mock = Mock()

    # Simular detección de cara
    face_mock = Mock()
    face_mock.landmark = [Mock(x=0.5, y=0.5, z=0.5) for _ in range(468)]

    results_mock = Mock()
    results_mock.multi_face_landmarks = [face_mock]

    mock.process.return_value = results_mock
    mock.FACE_CONNECTIONS = []

    return mock


# ============================================================================
# FIXTURES: Config
# ============================================================================

@pytest.fixture
def config():
    """Config dummy para testing."""
    from dataclasses import dataclass

    @dataclass
    class TestConfig:
        roi_size: int = 64
        confidence_threshold: float = 0.7
        learning_rate: float = 0.001
        batch_size: int = 32
        max_epochs: int = 100

    return TestConfig()


# ============================================================================
# MARKERS: Custom markers para organizar tests
# ============================================================================

def pytest_configure(config):
    """Registrar custom markers."""
    config.addinivalue_line(
        "markers", "slow: tests que toman > 5 segundos"
    )
    config.addinivalue_line(
        "markers", "requires_real_camera: requieren C920 conectada"
    )
    config.addinivalue_line(
        "markers", "benchmark: tests de latencia/performance"
    )
    config.addinivalue_line(
        "markers", "integration: tests de múltiples componentes"
    )


# ============================================================================
# HOOKS: Ejecución especial
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Aplicar markers automáticamente."""
    for item in items:
        # Si el nombre tiene "slow", marcar como slow
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)

        # Si requiere cámara
        if "camera" in item.nodeid and "mock" not in item.nodeid:
            item.add_marker(pytest.mark.requires_real_camera)

        # Si es benchmark
        if "latency" in item.nodeid or "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.benchmark)

        # Si es integration test
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
