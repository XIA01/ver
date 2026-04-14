# tests/conftest.py
# Fixtures compartidas para todos los tests
# Se cargan automáticamente por pytest

import pytest
import torch
import numpy as np
from pathlib import Path
import tempfile
from unittest.mock import Mock


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
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def seed():
    """Seed para reproducibilidad."""
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
    return torch.randn(16, dtype=torch.float32)


@pytest.fixture
def dummy_batch(device):
    """Batch de datos dummy para training.

    Returns:
        Tupla (x, y) donde:
        - x: (batch_size=32, 16) features
        - y: (batch_size=32, 2) targets (X, Y en pantalla)
    """
    x = torch.randn(32, 16, dtype=torch.float32, device=device)
    y = torch.randint(0, 1920, (32, 2), dtype=torch.float32, device=device)
    return x, y


@pytest.fixture
def dummy_dataset():
    """Dataset dummy con 100 muestras."""
    from torch.utils.data import TensorDataset

    X = torch.randn(100, 16)
    y = torch.randint(0, 1920, (100, 2), dtype=torch.float32)

    return TensorDataset(X, y)


@pytest.fixture
def dummy_dataloader(dummy_dataset):
    """DataLoader dummy con batch_size=8."""
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
    from src.brain.kan_model import KANModel

    model = KANModel(input_dim=16, output_dim=2)
    model.to(device)
    return model


@pytest.fixture
def trained_kan_model(kan_model, dummy_dataloader, device):
    """Modelo KAN pre-entrenado en dummy data (5 épocas)."""
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
# PARAMETRIZATION: Common combinations
# ============================================================================

@pytest.fixture(params=[0.001, 0.01, 0.1])
def learning_rates(request):
    """Parametrización: diferentes learning rates."""
    return request.param


@pytest.fixture(params=[
    (480, 640),
    (720, 1280),
    (1080, 1920),
])
def frame_shapes(request):
    """Parametrización: diferentes resoluciones de frame."""
    return request.param


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


# ============================================================================
# UTILITY FUNCTIONS: Helpers para tests
# ============================================================================

def create_dummy_checkpoint(path, model, optimizer, epoch=1, loss=0.5):
    """Crear un checkpoint dummy para testing."""
    import torch

    checkpoint = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "epoch": epoch,
        "loss": loss,
    }

    torch.save(checkpoint, path)
    return checkpoint


def assert_latency(func, max_ms=50):
    """Assert que función ejecute en menos de max_ms milliseconds.

    Usage:
        assert_latency(lambda: model(x), max_ms=10)
    """
    import time

    start = time.perf_counter()
    func()
    elapsed = (time.perf_counter() - start) * 1000

    assert elapsed < max_ms, f"Latency {elapsed:.2f}ms exceeds {max_ms}ms"


# ============================================================================
# EXAMPLE USAGE IN TESTS
# ============================================================================

"""
# En tu test file:

def test_model_forward(kan_model, dummy_batch):
    '''Test forward pass.'''
    x, _ = dummy_batch
    output = kan_model(x)
    assert output.shape == (32, 2)


def test_training_loss_decreases(trained_kan_model, dummy_dataloader, device):
    '''Test que loss disminuye después de training.'''
    criterion = torch.nn.MSELoss()

    # Evaluar en datos
    losses = []
    with torch.no_grad():
        for x, y in dummy_dataloader:
            x, y = x.to(device), y.to(device)
            pred = trained_kan_model(x)
            loss = criterion(pred, y)
            losses.append(loss.item())

    # El modelo pre-entrenado debe tener loss bajo
    assert np.mean(losses) < 1000  # Scales depende de dataset


@pytest.mark.benchmark
def test_model_latency(kan_model, device):
    '''Test que forward pass es rápido.'''
    x = torch.randn(1, 16, device=device)

    assert_latency(lambda: kan_model(x), max_ms=10)


@pytest.mark.parametrize("lr", [0.001, 0.01])
def test_different_learning_rates(kan_model, lr, dummy_dataloader, device):
    '''Parametrizado: probar diferentes LRs.'''
    optimizer = torch.optim.Adam(kan_model.parameters(), lr=lr)
    # ... training loop ...


def test_with_config(config):
    '''Usar config dummy.'''
    assert config.roi_size == 64
    assert config.batch_size == 32


def test_with_mock_camera(mock_camera):
    '''Usar mock en lugar de hardware real.'''
    frame = mock_camera.read()
    assert frame.shape == (480, 640, 3)


def test_with_temp_files(tmp_data_dir):
    '''Usar directorio temporal.'''
    checkpoint_path = tmp_data_dir / "checkpoint.pt"
    # ... guardar/cargar checkpoint ...
    assert checkpoint_path.exists()
"""
