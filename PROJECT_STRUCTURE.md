# Project Structure 📁

Complete overview of the GitHub Agent Workflow system.

## Core Files

### Main System Files

**`github_agent_workflow.py`** (Main workflow system)
- **GitHubFetcher**: Fetches repository files via GitHub API
- **SummarizerAgent**: AI-powered async file summarization
- **DeciderAgent**: Intelligent file selection based on questions
- **AnsweringAgent**: Generates grounded answers from code
- **GitHubAgentWorkflow**: Main orchestrator class

**`cli.py`** (Command-line interface)
- Interactive mode for user-friendly experience
- Batch mode for automated processing
- Colorized output with progress indicators
- Session management and statistics

**`utils.py`** (Utility functions)
- **SummaryAnalyzer**: Analyze and visualize summaries
- **FileFilter**: Advanced file filtering utilities
- **ExportUtilities**: Export to Markdown/CSV
- Helper functions for common tasks

**`example.py`** (Usage examples)
- Full example with comprehensive Q&A
- Quick example for faster testing
- Demonstrates all major features
- Commented code for learning

### Configuration Files

**`requirements.txt`**
- All Python dependencies
- Versioned for stability
- Comments for optional packages

**`.env.template`**
- Environment variable template
- Configuration options
- API key placeholders

### Documentation Files

**`README.md`**
- Comprehensive documentation
- Installation instructions
- Usage examples and tips
- Troubleshooting guide
- API reference

**`QUICKSTART.md`**
- 5-minute getting started guide
- Step-by-step instructions
- Common use cases
- Pro tips and tricks

**`PROJECT_STRUCTURE.md`** (this file)
- Complete project overview
- File descriptions
- Architecture explanation
- Development guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (GitHub URL)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                   1. FETCHER AGENT                           │
│  • Parse GitHub URL                                          │
│  • Fetch repository tree                                     │
│  • Download all file contents asynchronously                 │
│  • Filter by size and type                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                   2. SUMMARIZER AGENT                        │
│  • Process all files in parallel (async)                     │
│  • Extract: summary, key concepts, dependencies              │
│  • Identify: functions, classes, purpose                     │
│  • Use Gemini AI for intelligent analysis                    │
│  • Save structured summaries to JSON                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                  SUMMARY STORAGE (JSON)                      │
│  • metadata: repo info, stats, timestamp                     │
│  • summaries: array of FileSummary objects                   │
│  • Persistent for reuse                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                    User Question                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                   3. DECIDER AGENT                           │
│  • Analyze question intent                                   │
│  • Match against file summaries                              │
│  • Score relevance using Gemini AI                           │
│  • Select top-k most relevant files                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                   4. ANSWERING AGENT                         │
│  • Retrieve selected file contents                           │
│  • Build comprehensive context                               │
│  • Generate answer using Gemini AI                           │
│  • Include file references and code snippets                 │
│  • Apply anti-hallucination measures                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                    Answer + Metadata                         │
│  • answer: detailed response                                 │
│  • selected_files: files used                                │
│  • timestamp: when answered                                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Structures

### FileSummary
```python
{
    "path": "src/main.py",
    "file_type": ".py",
    "language": "Python",
    "size": 5432,
    "summary": "Brief description of file purpose",
    "key_concepts": ["FastAPI", "async", "dependency injection"],
    "dependencies": ["fastapi", "uvicorn"],
    "functions_classes": ["create_app", "startup_event"],
    "purpose": "Application initialization",
    "timestamp": "2024-01-01T12:00:00"
}
```

### RepoMetadata
```python
{
    "repo_url": "https://github.com/owner/repo",
    "total_files": 156,
    "file_types": {".py": 120, ".md": 15},
    "total_size": 2458672,
    "processing_time": 45.23,
    "timestamp": "2024-01-01T12:00:00"
}
```

### QuestionResult
```python
{
    "question": "How does authentication work?",
    "selected_files": ["src/auth.py", "src/middleware.py"],
    "answer": "Detailed answer with code references...",
    "timestamp": "2024-01-01T12:05:00"
}
```

## Key Features Explained

### 1. Async Summarization
- Uses `asyncio.gather()` for parallel processing
- Semaphore limits concurrent Gemini API calls (default: 10)
- Processes hundreds of files in minutes instead of hours
- Automatic retry on failures

### 2. Intelligent File Selection
- Uses Gemini AI to understand question intent
- Scores all files against the question
- Considers: path, summary, purpose, concepts, dependencies
- Returns top-k most relevant files (user configurable)

### 3. Hallucination Prevention
- Answers ONLY based on provided file contents
- Explicit file references required
- Uncertainty expression when info unavailable
- No assumptions beyond code
- Context limits prevent information overload

### 4. Rich Summarization
Each file summary includes:
- **Summary**: 2-3 sentence overview
- **Key Concepts**: Algorithms, patterns, frameworks used
- **Dependencies**: Imports and external libraries
- **Functions/Classes**: Main code structures
- **Purpose**: Specific problem solved
- **Metadata**: Language, size, type

## Directory Structure (Runtime)

```
project_root/
├── github_agent_workflow.py    # Main system
├── cli.py                      # Interactive CLI
├── example.py                  # Usage examples
├── utils.py                    # Utility functions
├── requirements.txt            # Dependencies
├── .env.template              # Config template
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide
├── PROJECT_STRUCTURE.md      # This file
│
└── repo_analysis/            # Generated during runtime
    ├── repo_summary_20240101_120000.json
    ├── qa_results.json
    ├── qa_1.txt
    ├── qa_2.txt
    └── report.txt
```

## Development Guide

### Adding a New Agent

1. Create a new class inheriting from base agent pattern
2. Implement required methods
3. Add to `GitHubAgentWorkflow` orchestrator
4. Update CLI to expose new functionality

Example:
```python
class NewAgent:
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    async def process(self, data):
        # Your logic here
        pass
```

### Adding New Export Formats

Add methods to `ExportUtilities` class in `utils.py`:

```python
@staticmethod
def export_to_html(summary_path: str, output_path: str):
    analyzer = SummaryAnalyzer(summary_path)
    # Generate HTML...
```

### Customizing Summarization

Modify the prompt in `SummarizerAgent.summarize_file()`:

```python
prompt = f"""Your custom prompt here
File: {path}
Content: {content}
...
"""
```

### Adding New Filters

Add methods to `FileFilter` class in `utils.py`:

```python
@staticmethod
def custom_filter(files: List[Dict]) -> List[Dict]:
    return [f for f in files if your_condition(f)]
```

## API Reference

### GitHubAgentWorkflow

**`__init__(gemini_api_key, github_token=None)`**
Initialize the workflow with API credentials.

**`async process_repository(repo_url, output_dir='./repo_analysis')`**
Fetch and summarize a GitHub repository.
- Returns: Path to saved summary file

**`async ask_question(question, top_k=10)`**
Ask a question about the repository.
- Returns: Dictionary with answer and metadata

**`load_existing_summary(summary_path)`**
Load previously saved summary.

### CLI Commands

**Interactive Mode:**
```bash
python cli.py --api-key YOUR_KEY
```

**Batch Mode:**
```bash
python cli.py --api-key YOUR_KEY \
  --repo-url GITHUB_URL \
  --questions-file questions.txt \
  --batch
```

**Options:**
- `--api-key`: Gemini API key
- `--github-token`: GitHub token (optional)
- `--repo-url`: Repository to analyze
- `--summary-file`: Use existing summary
- `--questions-file`: File with questions
- `--output-dir`: Output directory
- `--top-k`: Files per question
- `--batch`: Non-interactive mode

## Performance Considerations

### Memory Usage
- Scales with repository size
- Large files (>100KB) are truncated
- Summary storage is JSON-based (minimal overhead)

### API Rate Limits
- **GitHub**: 60/hour (no token), 5000/hour (with token)
- **Gemini**: Based on your API tier
- Semaphore prevents overwhelming Gemini API

### Processing Time
- Small repo (<50 files): 1-2 minutes
- Medium repo (100-200 files): 3-5 minutes
- Large repo (500+ files): 10-20 minutes
- Scales linearly with file count

### Optimization Tips
1. Use GitHub token for faster fetching
2. Adjust semaphore for your API limits
3. Filter unnecessary files early
4. Reuse summaries when possible
5. Use batch mode for multiple questions

## Testing

### Test Individual Components
```python
# Test fetcher
fetcher = GitHubFetcher()
repo_data = await fetcher.fetch_repository(url)

# Test summarizer
summarizer = SummarizerAgent(api_key)
summaries = await summarizer.summarize_all_files(files)

# Test decider
decider = DeciderAgent(api_key)
selected = await decider.select_relevant_files(question, summaries)
```

### Integration Test
Run the example script:
```bash
python example.py
```

## Contributing Ideas

- Add more export formats (HTML, PDF)
- Implement caching layer for API responses
- Add support for GitLab and Bitbucket
- Create web UI using Streamlit or Flask
- Add code visualization features
- Implement semantic code search
- Add multi-repository comparison
- Support for private repositories
- Plugin system for custom agents

## License

MIT License - Use and modify freely

## Support

For issues, questions, or contributions:
1. Check documentation in README.md
2. Review example scripts
3. Examine the code comments
4. Test with smaller repositories first

---

**Happy Coding! 🚀**
