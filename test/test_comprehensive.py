"""Comprehensive test suite for qqgjyx."""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Mock torch for testing
try:
    import torch
    from torch.utils.data import Dataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create mock classes
    class MockTorch:
        class device:
            def __init__(self, device_type):
                self.type = device_type
            def __repr__(self):
                return f"device('{self.type}')"
    
    torch = MockTorch()
    
    class Dataset:
        pass
    
    class Subset:
        def __init__(self, dataset, indices):
            self.dataset = dataset
            self.indices = indices
            self._len = len(indices)
        
        def __len__(self):
            return self._len
    
    torch.utils = MagicMock()
    torch.utils.data = MagicMock()
    torch.utils.data.Dataset = Dataset
    torch.utils.data.Subset = Subset


class MockDataset(Dataset):
    """Mock dataset for testing."""
    def __init__(self, size=100):
        self.data = torch.randn(size, 5)
        self.labels = torch.randint(0, 3, (size,))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


class TestQQClass:
    """Test the main QQ class interface."""
    
    def test_qq_import(self):
        """Test QQ class can be imported."""
        from qqgjyx import QQ
        assert QQ is not None
        assert hasattr(QQ, 'help')
        assert hasattr(QQ, 'env')
        assert hasattr(QQ, 'dev')
        assert hasattr(QQ, 'seed')
        assert hasattr(QQ, 'style')
        assert hasattr(QQ, 'split')
    
    def test_qq_help(self, capsys):
        """Test QQ.help() function."""
        from qqgjyx import QQ
        QQ.help()
        captured = capsys.readouterr()
        assert "QQ Utilities:" in captured.out
        assert "QQ.env()" in captured.out
        assert "QQ.dev()" in captured.out
        assert "QQ.seed(n)" in captured.out
        assert "QQ.style()" in captured.out
        assert "QQ.split(d)" in captured.out
    
    def test_qq_env(self, capsys):
        """Test QQ.env() function."""
        from qqgjyx import QQ
        with patch('qqgjyx.helper.env') as mock_env:
            QQ.env()
            mock_env.assert_called_once()
    
    def test_qq_dev(self):
        """Test QQ.dev() function."""
        from qqgjyx import QQ
        with patch('qqgjyx.helper.dev') as mock_dev:
            mock_dev.return_value = torch.device('cpu')
            result = QQ.dev()
            mock_dev.assert_called_once()
            assert result == torch.device('cpu')
    
    def test_qq_seed(self):
        """Test QQ.seed() function."""
        from qqgjyx import QQ
        with patch('qqgjyx.helper.seed') as mock_seed:
            mock_seed.return_value = 42
            result = QQ.seed(42)
            mock_seed.assert_called_once_with(42)
            assert result == 42
    
    def test_qq_style(self):
        """Test QQ.style() function."""
        from qqgjyx import QQ
        with patch('qqgjyx.visual.style') as mock_style:
            QQ.style()
            mock_style.assert_called_once()
    
    def test_qq_split(self):
        """Test QQ.split() function."""
        from qqgjyx import QQ
        dataset = MockDataset(100)
        with patch('qqgjyx.data.split') as mock_split:
            mock_split.return_value = (dataset, dataset)
            train, val = QQ.split(dataset, val_ratio=0.2, seed=42)
            mock_split.assert_called_once_with(dataset, val_ratio=0.2, seed=42)
            assert train == dataset
            assert val == dataset


class TestHelperModule:
    """Test helper module functions."""
    
    def test_env_function(self, capsys):
        """Test env() function."""
        from qqgjyx.helper import env
        with patch('qqgjyx.helper.np') as mock_np, \
             patch('qqgjyx.helper.torch') as mock_torch:
            mock_np.__version__ = '1.21.0'
            mock_torch.__version__ = '1.9.0'
            env()
            captured = capsys.readouterr()
            assert "Environment Information" in captured.out
            assert "Python version:" in captured.out
    
    def test_dev_function(self, capsys):
        """Test dev() function."""
        from qqgjyx.helper import dev
        with patch('qqgjyx.helper.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = False
            mock_torch.device.return_value = torch.device('cpu')
            result = dev()
            captured = capsys.readouterr()
            assert "Device Information" in captured.out
            assert result == torch.device('cpu')
    
    def test_seed_function(self, capsys):
        """Test seed() function."""
        from qqgjyx.helper import seed
        with patch('qqgjyx.helper.torch') as mock_torch, \
             patch('qqgjyx.helper.np') as mock_np, \
             patch('qqgjyx.helper.pl') as mock_pl:
            result = seed(42)
            captured = capsys.readouterr()
            assert "Setting Random Seeds" in captured.out
            assert result == 42
            mock_torch.manual_seed.assert_called_with(42)
            mock_np.random.seed.assert_called_with(42)
            mock_pl.seed_everything.assert_called_with(42, workers=True)
    
    def test_backward_compatibility(self):
        """Test backward compatibility aliases."""
        from qqgjyx.helper import print_environment_info, get_device_info, set_all_seeds
        from qqgjyx.helper import env, dev, seed
        
        # Test that aliases point to new functions
        assert print_environment_info == env
        assert get_device_info == dev
        assert set_all_seeds == seed


class TestVisualModule:
    """Test visual module functions."""
    
    def test_style_function(self):
        """Test style() function."""
        from qqgjyx.visual import style
        with patch('qqgjyx.visual.plt') as mock_plt:
            style()
            mock_plt.style.use.assert_called_with('science')
            mock_plt.rcParams.update.assert_called_once()
    
    def test_backward_compatibility(self):
        """Test backward compatibility aliases."""
        from qqgjyx.visual import set_plt_style, style
        assert set_plt_style == style


class TestDataModule:
    """Test data module functions."""
    
    def test_split_function(self):
        """Test split() function."""
        from qqgjyx.data import split
        dataset = MockDataset(100)
        train_set, val_set = split(dataset, val_ratio=0.2, seed=42)
        
        assert len(train_set) == 80  # 80% of 100
        assert len(val_set) == 20    # 20% of 100
        assert isinstance(train_set, torch.utils.data.Subset)
        assert isinstance(val_set, torch.utils.data.Subset)
    
    def test_split_edge_cases(self):
        """Test split() edge cases."""
        from qqgjyx.data import split
        dataset = MockDataset(10)
        
        # Test 0% validation
        train_set, val_set = split(dataset, val_ratio=0.0, seed=42)
        assert len(train_set) == 10
        assert len(val_set) == 0
        
        # Test 100% validation
        train_set, val_set = split(dataset, val_ratio=1.0, seed=42)
        assert len(train_set) == 0
        assert len(val_set) == 10
    
    def test_backward_compatibility(self):
        """Test backward compatibility aliases."""
        from qqgjyx.data import train_val_split, split
        assert train_val_split == split


class TestValidatorModule:
    """Test validator module functions."""
    
    def test_ensure_between_valid(self):
        """Test ensure_between with valid values."""
        from qqgjyx.validator import ensure_between
        
        assert ensure_between(5, 0, 10) == 5
        assert ensure_between(0, 0, 10) == 0
        assert ensure_between(10, 0, 10) == 10
        assert ensure_between(0.5, 0.0, 1.0) == 0.5
    
    def test_ensure_between_invalid(self):
        """Test ensure_between with invalid values."""
        from qqgjyx.validator import ensure_between
        
        with pytest.raises(ValueError, match="value must be between 0 and 10"):
            ensure_between(-1, 0, 10)
        
        with pytest.raises(ValueError, match="value must be between 0 and 10"):
            ensure_between(11, 0, 10)
        
        with pytest.raises(ValueError, match="custom must be between 0 and 10"):
            ensure_between(5, 0, 10, "custom")


class TestExceptorModule:
    """Test exceptor module."""
    
    def test_qqgjyx_error(self):
        """Test QQGJYXError exception."""
        from qqgjyx.exceptor import QQGJYXError
        
        with pytest.raises(QQGJYXError):
            raise QQGJYXError("Test error")
        
        error = QQGJYXError("Test message")
        assert str(error) == "Test message"


class TestPackageStructure:
    """Test package structure and imports."""
    
    def test_package_imports(self):
        """Test all package imports work."""
        import qqgjyx
        from qqgjyx import QQ
        from qqgjyx.helper import env, dev, seed
        from qqgjyx.visual import style
        from qqgjyx.data import split
        from qqgjyx.validator import ensure_between
        from qqgjyx.exceptor import QQGJYXError
        
        assert qqgjyx.__version__ == "0.1.2"
        assert QQ is not None
    
    def test_subpackage_imports(self):
        """Test subpackage imports."""
        import qqgjyx.graph
        import qqgjyx.model
        import qqgjyx.visual
        import qqgjyx.data
        
        # Test that subpackages exist
        assert hasattr(qqgjyx, 'graph')
        assert hasattr(qqgjyx, 'model')
        assert hasattr(qqgjyx, 'visual')
        assert hasattr(qqgjyx, 'data')
    
    def test_version_consistency(self):
        """Test version consistency across modules."""
        import qqgjyx
        from qqgjyx import __version__
        
        assert qqgjyx.__version__ == __version__
        assert __version__ == "0.1.2"


class TestIntegration:
    """Integration tests."""
    
    def test_complete_workflow(self):
        """Test a complete workflow."""
        from qqgjyx import QQ
        
        # Create dataset
        dataset = MockDataset(100)
        
        # Use QQ interface
        QQ.seed(42)
        train_set, val_set = QQ.split(dataset, val_ratio=0.2)
        
        assert len(train_set) == 80
        assert len(val_set) == 20
    
    def test_mixed_imports(self):
        """Test mixing QQ class and direct imports."""
        from qqgjyx import QQ
        from qqgjyx.helper import seed
        from qqgjyx.data import split
        
        dataset = MockDataset(50)
        
        # Mix QQ and direct imports
        QQ.seed(123)
        train, val = split(dataset, val_ratio=0.3)
        
        assert len(train) == 35
        assert len(val) == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
