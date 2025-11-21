"""Pytest configuration and fixtures."""
import os
import sys
import pathlib
import pytest


@pytest.fixture(scope="session", autouse=True)
def enable_subprocess_coverage(tmp_path_factory):
    """Enable coverage measurement for subprocess calls.
    
    This creates a .pth file in site-packages that enables coverage
    for subprocesses, allowing us to measure CLI coverage properly.
    """
    # Only enable if running with coverage
    if "COV_CORE_SOURCE" in os.environ or "COVERAGE_PROCESS_START" in os.environ or "--cov" in sys.argv:
        # Get site-packages directory
        site_packages = None
        for path in sys.path:
            if "site-packages" in path:
                site_packages = pathlib.Path(path)
                break
        
        if site_packages and site_packages.exists():
            # Create coverage startup file
            cov_pth = site_packages / "cov.pth"
            cov_pth.write_text("import coverage; coverage.process_startup()")
            
            # Set environment variable for subprocess coverage
            os.environ["COVERAGE_PROCESS_START"] = str(pathlib.Path(__file__).parent.parent / ".coveragerc")
            
            yield
            
            # Cleanup
            if cov_pth.exists():
                cov_pth.unlink()
        else:
            yield
    else:
        yield

