# 🎓 EduMentor AI - Personalized Learning Assistant

[![Kaggle](https://img.shields.io/badge/Kaggle-Competition-20BEFF?logo=kaggle)](https://kaggle.com/competitions/agents-intensive-capstone-project)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A multi-agent AI system that provides personalized tutoring, adaptive practice problems, and learning progress tracking - making quality education accessible to everyone.

## 🌟 Project Overview

**Track:** Agents for Good (Education)

**Problem:** Quality tutoring is expensive and inaccessible to millions of students. Traditional classroom teaching cannot adapt to individual learning speeds and styles.

**Solution:** EduMentor AI uses a sophisticated multi-agent architecture to provide 24/7 personalized educational support that adapts to each student's needs.

## ✨ Features

- 🤖 **Multi-Agent System**: Specialized agents for tutoring, quizzes, progress tracking, and concept explanation
- 🧠 **Long-Term Memory**: Remembers each student's learning history, strengths, and gaps
- 📊 **Progress Analytics**: Real-time insights into learning patterns and mastery
- 🎯 **Adaptive Learning**: Adjusts difficulty and teaching style based on performance
- 🔧 **MCP Tools**: Knowledge base retrieval and custom assessment tools
- 📝 **Socratic Method**: Guides students to discover answers themselves
- 🌐 **24/7 Availability**: Always available to help with homework and studying

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│        Main Orchestrator Agent          │
│     (Sequential Coordination)           │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼─────┐
│ Router │          │ Session  │
│ Logic  │          │ Manager  │
└───┬────┘          └────┬─────┘
    │                    │
    │    ┌───────────────┴────────┐
    │    │                        │
┌───▼────▼───┐            ┌──────▼──────┐
│  Parallel  │◄──────────►│   Memory    │
│   Agents   │            │    Bank     │
└────┬───────┘            └─────────────┘
     │
     ├─── Tutor Agent (Personalized)
     ├─── Quiz Generator (Adaptive)
     ├─── Progress Tracker (Analytics)
     └─── Concept Explainer (Visual)
          │
          │ Uses Tools
          │
     ┌────▼───────────────┐
     │ Knowledge Base MCP │
     │ Assessment Tool    │
     │ Progress Storage   │
     └────────────────────┘
```

### Agent Descriptions

1. **Orchestrator Agent** - Routes queries and coordinates sub-agents
2. **Tutor Agent** - Provides Socratic-method tutoring
3. **Quiz Generator** - Creates adaptive practice problems
4. **Progress Tracker** - Analyzes learning patterns
5. **Concept Explainer** - Breaks down complex topics

## 🛠️ ADK Features Implemented

This project demonstrates the following ADK concepts from the 5-Day AI Agents Intensive Course:

- ✅ **Multi-agent System** (Sequential + Parallel agents)
- ✅ **MCP Tools** (Knowledge base retrieval)
- ✅ **Custom Tools** (Assessment & Progress storage)
- ✅ **Built-in Tools** (Google Search for research)
- ✅ **Long-term Memory** (Memory Bank for student context)
- ✅ **Session Management** (InMemorySessionService pattern)
- ✅ **Context Engineering** (Context compaction for long conversations)
- ✅ **Observability** (Structured logging, tracing, metrics)
- ✅ **Agent Evaluation** (Performance tracking & assessment)

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Google API key with Gemini API access

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/lakaThabrew/edumentor-ai.git
cd edumentor-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

5. **Create data directories**
```bash
mkdir -p data/progress data/memory logs
```

## 🚀 Usage

### Interactive Mode (CLI)

```bash
python main.py
```

This starts an interactive session where you can:
- Ask questions about any subject
- Request practice quizzes
- Get concept explanations
- Check your learning progress

### Example Interactions

**Homework Help:**
```
You: I don't understand how photosynthesis works
🤖 EduMentor: Let me help you understand! First, what do you 
already know about how plants get energy?
```

**Practice Problems:**
```
You: I need practice with quadratic equations
🤖 EduMentor: Great! I'll create some practice problems for you...
[Generates adaptive quiz]
```

**Progress Check:**
```
You: progress
🤖 EduMentor: 📊 PROGRESS REPORT
Overall: You've completed 15 sessions...
Topics Mastered: Algebra basics, Cell biology...
```

## 📁 Project Structure

```
edumentor-ai/
├── main.py                    # Main orchestrator
├── agents/
│   ├── tutor_agent.py        # Socratic tutoring
│   ├── quiz_generator_agent.py
│   ├── progress_tracker_agent.py
│   └── concept_explainer_agent.py
├── tools/
│   ├── knowledge_base_tool.py    # MCP integration
│   ├── assessment_tool.py        # Custom grading
│   └── progress_storage_tool.py
├── config/
│   ├── agent_config.py
│   └── prompts.py
├── memory_bank.py             # Long-term memory
├── session_manager.py         # Session state
├── observability.py           # Logging & metrics
├── requirements.txt
├── .env.example
├── README.md
└── WRITEUP.md                 # Competition submission
```

## 🧪 Testing

Run the interactive demo:
```bash
python main.py
```

Test individual agents:
```python
from agents.tutor_agent import TutorAgent
from google import genai

client = genai.Client(api_key="your_key")
tutor = TutorAgent(client, memory_bank)
response = await tutor.teach("Explain photosynthesis", "test_student")
```

## 📊 Metrics & Observability

View logs:
```bash
tail -f logs/edumentor_YYYYMMDD.log
```

Check metrics:
```python
from observability import ObservabilityManager
obs = ObservabilityManager()
report = obs.get_performance_report()
```

## 🎯 Use Cases

### For Students
- **Homework Help**: Get unstuck on difficult problems
- **Exam Prep**: Generate practice tests
- **Concept Review**: Understand difficult topics
- **Progress Tracking**: See your improvement over time

### For Teachers
- **Student Insights**: Understand where students struggle
- **Supplemental Support**: 24/7 tutoring assistance
- **Assessment Creation**: Generate practice problems
- **Progress Monitoring**: Track class-wide trends

### For Parents
- **Learning Support**: Help with subjects you don't remember
- **Progress Visibility**: See what your child is learning
- **Engagement**: Keep students motivated with adaptive challenges

## 🌍 Social Impact

**Accessibility**: Provides free, quality tutoring to underserved communities

**Equity**: Bridges the gap between students with and without private tutors

**Scalability**: Can support unlimited students simultaneously

**Global Reach**: Accessible anywhere with internet connection

## 🛣️ Roadmap

- [ ] Voice interface for younger students
- [ ] Visual diagram generation
- [ ] Multi-language support
- [ ] Parent dashboard
- [ ] LMS integration (Canvas, Moodle)
- [ ] A2A protocol for agent collaboration
- [ ] Mobile app
- [ ] Deployment to Google Cloud (Agent Engine)

## 🤝 Contributing

This is a competition submission, but feedback and suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🏆 Competition Details

**Competition**: Agents Intensive Capstone Project  
**Track**: Agents for Good (Education)  
**Submission Date**: December 1, 2025  
**Platform**: Kaggle

## 👥 Team

- **Lakmana Thabrew** - Lead Developer

## 🙏 Acknowledgments

- Google AI Agents Intensive Course
- Kaggle community
- Test users who provided feedback

## 📧 Contact

- **Email**: chulankalakmana@example.com
- **Kaggle**: [Chulanka Lakmana](https://www.kaggle.com/chulankalakmana)
- **GitHub**: [Lakmana Thabrew](https://github.com/lakaThabrew/)

---

**Made with ❤️ for learners everywhere**