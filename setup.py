"""Setup script for market intelligence platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="market-intelligence-platform",
    version="0.2.0",
    author="Your Name",
    description="Real-time market surveillance and anomaly detection system with explainable AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.6.0",
        "pydantic-settings>=2.0.0",
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "scikit-learn>=1.4.0",
        "river>=0.21.0",
        "shap>=0.44.0",
        "websockets>=12.0",
        "httpx>=0.26.0",
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "requests>=2.31.0",
        "pyyaml>=6.0.0",
        "prometheus-client>=0.19.0",
        "structlog>=24.1.0",
        "redis>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mip-cli=apps.cli.main:main",
        ],
    },
)

