"""Aura-Core: The Universal Context Compiler for AI Agents"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="auralith-aura",
    version="0.2.3",
    description="The Universal Context Compiler for AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Auralith Inc.",
    author_email="info@auralith.org",
    url="https://github.com/Rtalabs-ai/aura-core",
    packages=find_packages(),
    package_data={
        "aura": ["_memory.py", "_memory.pyc"],
    },
    install_requires=[
        "numpy>=1.21.0",
        "msgpack>=1.0.0",
        "safetensors>=0.3.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "docs": [
            "unstructured>=0.10.0",
            "pypdf>=3.0.0",
            "python-docx>=0.8.11",
        ],
        "data": [
            "pandas>=1.3.0",
            "openpyxl>=3.0.0",
            "pyarrow>=10.0.0",
        ],
        "all": [
            "unstructured[all-docs]>=0.10.0",
            "pypdf>=3.0.0",
            "python-docx>=0.8.11",
            "pandas>=1.3.0",
            "openpyxl>=3.0.0",
            "pyarrow>=10.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aura=aura.compiler:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    license="Apache-2.0 AND Proprietary",
    license_files=["LICENSE", "LICENSE-MEMORY"],
    keywords="ai, agent-memory, rag, context-compiler, openclaw, claude-code, codex, gemini-cli, llm, knowledge-base",
)
