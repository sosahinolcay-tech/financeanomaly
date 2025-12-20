"""Setup script for anomaly platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="anomaly-platform",
    version="0.1.0",
    author="Your Name",
    description="Real-time Financial Anomaly & Explainability Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "shap>=0.42.0",
        "river>=0.20.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
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
            "anomaly-cli=ap.cli:main",
        ],
    },
)

