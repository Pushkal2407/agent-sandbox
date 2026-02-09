"""AgentBox setup configuration."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentbox",
    version="0.1.0",
    description="AI agent runtime with policy-based execution constraints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AgentBox Contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["examples", "tests"]),
    entry_points={
        "console_scripts": [
            "agentbox=agentbox.cli:main",
        ],
    },
    install_requires=[
        "openai>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
