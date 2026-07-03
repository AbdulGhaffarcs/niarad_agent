# Contributing to NIARAD

Thank you for your interest in contributing to NIARAD! This document outlines our contribution guidelines and development workflow.

---

## **Getting Started**

1. **Fork the repository** and clone your fork
2. **Create a feature branch** from `main`
3. **Follow the tech stack:** FastAPI (backend) + Next.js (frontend)
4. **Write tests** for new features
5. **Submit a Pull Request** with a clear description

---

## **Development Setup**

### **Backend**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### **Frontend**

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

---

## **Code Standards**

### **Python (Backend)**

- Format with `black` and `isort`
- Type hints required (Pydantic models for API)
- Docstrings for all public functions
- Linting with `flake8`

### **TypeScript (Frontend)**

- Strict mode enabled in `tsconfig.json`
- ESLint configured for code quality
- Prettier for code formatting
- 80-character line limit for readability

---

## **Commit Message Format**

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Example:**
```
feat(srs): implement SM-2 algorithm improvements

Added support for custom difficulty multipliers and improved
rescheduling logic for edge cases. Maintains backward compatibility.

Closes #42
```

---

## **Areas for Contribution**

### **Backend**

- [ ] Additional tool implementations (calculator, image analysis, etc.)
- [ ] Advanced SM-2 variants (SuperMemo 17, ANKI)
- [ ] Multi-user support
- [ ] Performance optimizations (vectorized embeddings, caching)

### **Frontend**

- [ ] Mobile UI (React Native)
- [ ] Dark/light theme toggle
- [ ] Advanced analytics dashboard
- [ ] Export to Anki/Quizlet

### **General**

- [ ] Documentation improvements
- [ ] Bug reports and fixes
- [ ] Performance profiling
- [ ] Test coverage

---

## **Pull Request Process**

1. Update documentation if needed
2. Add tests for new features
3. Ensure CI passes (linting, type checking, tests)
4. Request review from maintainers
5. Address feedback and re-request review
6. Squash commits before merging

---

## **Questions?**

Open an issue or start a discussion. We're here to help!

---

**Thank you for contributing to NIARAD! 🎓**