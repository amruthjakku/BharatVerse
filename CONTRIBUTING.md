# Contributing to BharatVerse 🇮🇳

Thank you for your interest in contributing to BharatVerse! We're excited to have you join our mission to preserve India's rich cultural heritage through technology.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Respect cultural sensitivities when handling cultural content
- Give credit where credit is due
- Focus on constructive criticism

### Unacceptable Behavior
- Harassment, discrimination, or hate speech
- Misrepresentation or misappropriation of cultural content
- Trolling or insulting/derogatory comments
- Public or private harassment
- Publishing others' private information without permission

## How Can I Contribute?

### 1. 📝 Content Contributions
- **Audio**: Record folk songs, stories, or oral traditions
- **Text**: Document recipes, customs, proverbs, or stories
- **Images**: Upload photos of festivals, art, architecture
- **Translations**: Help translate content to preserve accessibility

### 2. 🐛 Bug Reports
Before submitting a bug report:
- Check if the issue already exists
- Try to reproduce the issue
- Collect relevant information (OS, browser, error messages)

Create an issue with:
```markdown
**Description**: Clear description of the bug
**Steps to Reproduce**: 
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**: What should happen
**Actual Behavior**: What actually happens
**Screenshots**: If applicable
**Environment**: OS, Browser, Version
```

### 3. ✨ Feature Requests
We love new ideas! When suggesting features:
- Check existing issues first
- Explain the problem your feature solves
- Describe your proposed solution
- Consider cultural impact and inclusivity

### 4. 💻 Code Contributions
Areas where we need help:
- **Frontend**: Streamlit UI improvements, new visualizations
- **Backend**: API endpoints, database optimization
- **AI/ML**: Improving transcription, translation, and analysis models
- **DevOps**: Docker, CI/CD, deployment automation
- **Documentation**: Tutorials, API docs, user guides

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend development)
- Docker (optional, for containerized development)
- Git

### Local Setup
```bash
# Clone the repository
git clone https://github.com/bharatverse/bharatverse.git
cd bharatverse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init_db.py

# Run the application
streamlit run streamlit_app/app.py
```

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application at http://localhost:8501
```

## Making Changes

### 1. Fork and Branch
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/bharatverse.git

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Development Workflow
- Write clean, documented code
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow the style guidelines

### 3. Commit Messages
Use conventional commits:
```
feat: add Hindi language support for audio transcription
fix: resolve database connection timeout issue
docs: update API documentation for search endpoint
style: format code according to PEP8
test: add unit tests for image captioning
chore: update dependencies
```

### 4. Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_audio.py

# Run with coverage
pytest --cov=bharatverse

# Run linting
flake8 .
black . --check
```

## Submitting Changes

### 1. Pull Request Process
1. Update your branch with the latest main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/videos if UI changes
   - Test results

### 2. PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### 3. Review Process
- PRs require at least one approval
- Address review comments promptly
- Keep PRs focused and reasonably sized
- Be patient and respectful during reviews

## Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names

```python
# Good
def transcribe_audio(
    file_path: str, 
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transcribe audio file using Whisper model.
    
    Args:
        file_path: Path to audio file
        language: ISO language code (e.g., 'hi', 'bn')
        
    Returns:
        Dictionary containing transcription and metadata
    """
    # Implementation
```

### Frontend Style
- Use consistent component structure
- Follow Streamlit best practices
- Keep components modular and reusable
- Use meaningful session state keys

### Documentation Style
- Use clear, simple language
- Include code examples
- Add screenshots for UI features
- Keep README and docs updated

## Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Email**: team@bharatverse.org
- **Discord**: [Join our server](https://discord.gg/bharatverse)

### Recognition
Contributors will be:
- Listed in our CONTRIBUTORS.md file
- Mentioned in release notes
- Invited to contributor meetings
- Given special badges on Discord

### Resources
- [Project Roadmap](https://github.com/bharatverse/bharatverse/projects)
- [API Documentation](https://docs.bharatverse.org)
- [Development Blog](https://blog.bharatverse.org)
- [Cultural Guidelines](docs/cultural-guidelines.md)

## Questions?

Feel free to:
- Open an issue for questions
- Join our Discord community
- Email us at team@bharatverse.org

Thank you for helping preserve India's cultural heritage! 🙏

---

Made with ❤️ by the BharatVerse community
