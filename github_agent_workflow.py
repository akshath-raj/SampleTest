"""
GitHub Repository Agentic Workflow System

This system implements a multi-agent pipeline for analyzing GitHub repositories:
1. Fetcher Agent: Retrieves all files from a GitHub repository
2. Summarizer Agent: Asynchronously summarizes each file with meaningful context
3. Decider Agent: Intelligently selects relevant files based on user questions
4. Answering Agent: Provides accurate answers using selected file contents

Features:
- Async summarization for faster processing
- Intelligent file filtering and selection
- Context-aware summarization with code understanding
- Hallucination prevention through grounded responses
"""

import os
import json
import asyncio
import aiohttp
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
from pathlib import Path
import google.generativeai as genai


@dataclass
class FileSummary:
    """Structured file summary with metadata"""
    path: str
    file_type: str
    language: Optional[str]
    size: int
    summary: str
    key_concepts: List[str]
    dependencies: List[str]
    functions_classes: List[str]
    purpose: str
    timestamp: str


@dataclass
class RepoMetadata:
    """Repository metadata"""
    repo_url: str
    total_files: int
    file_types: Dict[str, int]
    total_size: int
    processing_time: float
    timestamp: str


class GitHubFetcher:
    """Agent 1: Fetches repository content from GitHub"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
    
    def parse_github_url(self, url: str) -> Tuple[str, str, str]:
        """Extract owner, repo, and branch from GitHub URL"""
        # Handle various GitHub URL formats
        url = url.rstrip('/')
        parts = url.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
        
        owner = parts[0]
        repo = parts[1]
        branch = 'main'  # Default branch
        
        if len(parts) > 3 and parts[2] == 'tree':
            branch = parts[3]
        
        return owner, repo, branch
    
    async def get_repo_tree(self, owner: str, repo: str, branch: str) -> List[Dict]:
        """Get the entire repository tree recursively"""
        url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch repo tree: {response.status}")
                data = await response.json()
                return data.get('tree', [])
    
    async def get_file_content(self, owner: str, repo: str, path: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Fetch content of a single file"""
        url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                
                # Decode base64 content
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
        except Exception as e:
            print(f"Error fetching {path}: {e}")
            return None
    
    async def fetch_repository(self, repo_url: str, max_file_size: int = 1_000_000) -> Dict:
        """Fetch all files from the repository"""
        print(f"🔍 Fetching repository: {repo_url}")
        start_time = datetime.now()
        
        owner, repo, branch = self.parse_github_url(repo_url)
        print(f"   Owner: {owner}, Repo: {repo}, Branch: {branch}")
        
        # Get repository tree
        tree = await self.get_repo_tree(owner, repo, branch)
        
        # Filter only files (not directories) and limit size
        files = [
            item for item in tree 
            if item['type'] == 'blob' and item['size'] < max_file_size
        ]
        
        print(f"📁 Found {len(files)} files to process")
        
        # Fetch file contents asynchronously
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [
                self._fetch_file_with_metadata(owner, repo, file_item, session)
                for file_item in files
            ]
            file_contents = await asyncio.gather(*tasks)
        
        # Filter out failed fetches
        file_contents = [f for f in file_contents if f is not None]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate statistics
        file_types = {}
        total_size = 0
        for file in file_contents:
            ext = Path(file['path']).suffix or 'no_extension'
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += file['size']
        
        metadata = RepoMetadata(
            repo_url=repo_url,
            total_files=len(file_contents),
            file_types=file_types,
            total_size=total_size,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
        print(f"✅ Fetched {len(file_contents)} files in {processing_time:.2f}s")
        
        return {
            'metadata': asdict(metadata),
            'files': file_contents
        }
    
    async def _fetch_file_with_metadata(self, owner: str, repo: str, file_item: Dict, session: aiohttp.ClientSession) -> Optional[Dict]:
        """Fetch file with metadata"""
        content = await self.get_file_content(owner, repo, file_item['path'], session)
        
        if content is None:
            return None
        
        return {
            'path': file_item['path'],
            'size': file_item['size'],
            'sha': file_item['sha'],
            'content': content
        }


class SummarizerAgent:
    """Agent 2: Asynchronously summarizes files with meaningful context"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    def _get_language(self, file_path: str) -> Optional[str]:
        """Determine programming language from file extension"""
        ext_to_lang = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
            '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
            '.swift': 'Swift', '.kt': 'Kotlin', '.scala': 'Scala',
            '.html': 'HTML', '.css': 'CSS', '.jsx': 'React JSX',
            '.tsx': 'React TSX', '.vue': 'Vue', '.md': 'Markdown',
            '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
            '.xml': 'XML', '.sql': 'SQL', '.sh': 'Shell',
        }
        ext = Path(file_path).suffix.lower()
        return ext_to_lang.get(ext, 'Unknown')
    
    async def summarize_file(self, file_data: Dict) -> FileSummary:
        """Summarize a single file with rich context"""
        async with self.semaphore:
            path = file_data['path']
            content = file_data['content']
            size = file_data['size']
            
            # Skip binary or very large files
            if size > 100000:  # Limit content size for summarization
                content = content[:100000] + "\n... (truncated)"
            
            language = self._get_language(path)
            file_type = Path(path).suffix or 'no_extension'
            
            # Create comprehensive summarization prompt
            prompt = f"""Analyze this file and provide a detailed, structured summary.

File Path: {path}
Language: {language}
Size: {size} bytes

Content:
```
{content}
```

Provide your response in the following JSON format:
{{
    "summary": "A concise 2-3 sentence summary of what this file does",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "dependencies": ["dependency1", "dependency2"],
    "functions_classes": ["function/class names"],
    "purpose": "The main purpose/role of this file in the project"
}}

Key concepts should include: algorithms used, design patterns, data structures, APIs, frameworks.
Dependencies should include: imports, external libraries, related files mentioned.
Functions/classes should list the main ones (up to 10 most important).
Purpose should be specific about what problem this file solves.

Return ONLY valid JSON, no markdown formatting."""

            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                
                # Parse JSON response
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                analysis = json.loads(response_text.strip())
                
                return FileSummary(
                    path=path,
                    file_type=file_type,
                    language=language,
                    size=size,
                    summary=analysis.get('summary', 'No summary available'),
                    key_concepts=analysis.get('key_concepts', []),
                    dependencies=analysis.get('dependencies', []),
                    functions_classes=analysis.get('functions_classes', []),
                    purpose=analysis.get('purpose', 'Unknown purpose'),
                    timestamp=datetime.now().isoformat()
                )
                
            except Exception as e:
                print(f"❌ Error summarizing {path}: {e}")
                # Return a basic summary on error
                return FileSummary(
                    path=path,
                    file_type=file_type,
                    language=language,
                    size=size,
                    summary=f"File of type {file_type}",
                    key_concepts=[],
                    dependencies=[],
                    functions_classes=[],
                    purpose="Unknown",
                    timestamp=datetime.now().isoformat()
                )
    
    async def summarize_all_files(self, files: List[Dict]) -> List[FileSummary]:
        """Asynchronously summarize all files"""
        print(f"🤖 Summarizing {len(files)} files asynchronously...")
        start_time = datetime.now()
        
        tasks = [self.summarize_file(file_data) for file_data in files]
        summaries = await asyncio.gather(*tasks)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Completed summarization in {processing_time:.2f}s")
        
        return summaries


class DeciderAgent:
    """Agent 3: Intelligently selects relevant files based on user questions"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    async def select_relevant_files(self, question: str, summaries: List[FileSummary], top_k: int = 10) -> List[str]:
        """Select the most relevant files for answering the question"""
        print(f"🎯 Selecting relevant files for question: {question[:100]}...")
        
        # Create a comprehensive summary index
        summary_index = []
        for i, summary in enumerate(summaries):
            summary_text = f"""
File {i}: {summary.path}
Language: {summary.language}
Summary: {summary.summary}
Purpose: {summary.purpose}
Key Concepts: {', '.join(summary.key_concepts[:5])}
Functions/Classes: {', '.join(summary.functions_classes[:5])}
"""
            summary_index.append(summary_text.strip())
        
        full_index = "\n\n".join(summary_index)
        
        # Prompt for file selection
        prompt = f"""You are an intelligent file selector. Given a user's question and summaries of files in a repository, select the most relevant files that would help answer the question.

User Question: {question}

File Summaries:
{full_index}

Analyze the question and select the TOP {top_k} most relevant files. Consider:
1. Direct relevance to the question topic
2. Files that implement the functionality asked about
3. Configuration files if the question is about setup/config
4. Documentation files if the question is about usage
5. Test files if the question is about testing or examples

Return your response as a JSON array of file indices (0-based):
{{"selected_files": [0, 3, 7, ...]}}

Return ONLY valid JSON, no explanation or markdown."""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            response_text = response.text.strip()
            # Clean up response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            selected_indices = result.get('selected_files', [])
            
            # Get file paths
            selected_paths = [summaries[i].path for i in selected_indices if i < len(summaries)]
            
            print(f"✅ Selected {len(selected_paths)} files")
            for path in selected_paths[:5]:
                print(f"   - {path}")
            if len(selected_paths) > 5:
                print(f"   ... and {len(selected_paths) - 5} more")
            
            return selected_paths
            
        except Exception as e:
            print(f"❌ Error in file selection: {e}")
            # Fallback: select files based on keyword matching
            keywords = question.lower().split()
            scored_files = []
            
            for i, summary in enumerate(summaries):
                score = 0
                summary_text = f"{summary.path} {summary.summary} {summary.purpose}".lower()
                for keyword in keywords:
                    if keyword in summary_text:
                        score += 1
                scored_files.append((score, summary.path))
            
            scored_files.sort(reverse=True, key=lambda x: x[0])
            return [path for score, path in scored_files[:top_k] if score > 0]


class AnsweringAgent:
    """Agent 4: Provides accurate, grounded answers using selected files"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    async def answer_question(self, question: str, selected_files: List[Dict], summaries: List[FileSummary]) -> str:
        """Answer the question using selected file contents"""
        print(f"💬 Generating answer...")
        
        # Build context from selected files
        context_parts = []
        for file_data in selected_files:
            path = file_data['path']
            content = file_data['content']
            
            # Find corresponding summary
            summary = next((s for s in summaries if s.path == path), None)
            
            context_part = f"""
=== File: {path} ===
Summary: {summary.summary if summary else 'N/A'}
Purpose: {summary.purpose if summary else 'N/A'}

Content:
{content[:5000]}  # Limit content length
{'... (truncated)' if len(content) > 5000 else ''}
"""
            context_parts.append(context_part.strip())
        
        full_context = "\n\n".join(context_parts)
        
        # Create answering prompt with anti-hallucination measures
        prompt = f"""You are a helpful assistant analyzing a GitHub repository. Answer the user's question based ONLY on the provided file contents.

CRITICAL INSTRUCTIONS:
1. Base your answer ONLY on the provided file contents
2. If the information is not in the files, say "I don't have enough information in the provided files to answer this"
3. Quote specific file names and line numbers when referencing information
4. If you're uncertain, express that uncertainty
5. Do not make assumptions or add information not present in the files

User Question: {question}

Repository File Contents:
{full_context}

Provide a detailed, accurate answer based on the file contents above. Include:
- Direct references to specific files
- Code snippets if relevant (keep them short)
- Explanations grounded in the actual code
- If multiple files are relevant, explain how they work together

Your answer:"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            answer = response.text.strip()
            print(f"✅ Answer generated ({len(answer)} characters)")
            
            return answer
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return f"I encountered an error while generating the answer: {str(e)}"


class GitHubAgentWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self, gemini_api_key: str, github_token: Optional[str] = None):
        self.fetcher = GitHubFetcher(github_token)
        self.summarizer = SummarizerAgent(gemini_api_key)
        self.decider = DeciderAgent(gemini_api_key)
        self.answerer = AnsweringAgent(gemini_api_key)
        
        self.repo_data = None
        self.summaries = None
        self.summary_path = None
    
    async def process_repository(self, repo_url: str, output_dir: str = "./repo_analysis") -> str:
        """Process the entire repository and create summaries"""
        print("=" * 80)
        print("🚀 GITHUB REPOSITORY AGENT WORKFLOW")
        print("=" * 80)
        
        # Step 1: Fetch repository
        self.repo_data = await self.fetcher.fetch_repository(repo_url)
        
        # Step 2: Summarize all files asynchronously
        self.summaries = await self.summarizer.summarize_all_files(self.repo_data['files'])
        
        # Step 3: Save summaries to file
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"repo_summary_{timestamp}.json"
        self.summary_path = os.path.join(output_dir, summary_filename)
        
        summary_data = {
            'metadata': self.repo_data['metadata'],
            'summaries': [asdict(s) for s in self.summaries]
        }
        
        with open(self.summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Summary saved to: {self.summary_path}")
        print("=" * 80)
        
        return self.summary_path
    
    async def ask_question(self, question: str, top_k: int = 10) -> Dict:
        """Ask a question about the repository"""
        if self.summaries is None:
            raise ValueError("Repository not processed yet. Call process_repository() first.")
        
        print("\n" + "=" * 80)
        print(f"❓ QUESTION: {question}")
        print("=" * 80)
        
        # Step 1: Select relevant files
        selected_paths = await self.decider.select_relevant_files(question, self.summaries, top_k)
        
        # Step 2: Get full content of selected files
        selected_files = [
            file_data for file_data in self.repo_data['files']
            if file_data['path'] in selected_paths
        ]
        
        # Step 3: Generate answer
        answer = await self.answerer.answer_question(question, selected_files, self.summaries)
        
        result = {
            'question': question,
            'selected_files': selected_paths,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n" + "=" * 80)
        print("📝 ANSWER:")
        print("=" * 80)
        print(answer)
        print("=" * 80)
        
        return result
    
    def load_existing_summary(self, summary_path: str):
        """Load previously created summary"""
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.summaries = [FileSummary(**s) for s in data['summaries']]
        self.summary_path = summary_path
        print(f"✅ Loaded {len(self.summaries)} file summaries from {summary_path}")


# Example usage
async def main():
    """Example usage of the workflow"""
    
    # Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Optional, but recommended for rate limits
    
    # Initialize workflow
    workflow = GitHubAgentWorkflow(
        gemini_api_key=GEMINI_API_KEY,
        github_token=GITHUB_TOKEN
    )
    
    # Example 1: Process a repository
    repo_url = "https://github.com/anthropics/anthropic-sdk-python"
    summary_path = await workflow.process_repository(repo_url)
    
    # Example 2: Ask questions
    questions = [
        "How do I authenticate with the Anthropic API using this SDK?",
        "What are the main classes and their purposes?",
        "How do I handle streaming responses?",
        "What error handling mechanisms are implemented?",
    ]
    
    results = []
    for question in questions:
        result = await workflow.ask_question(question, top_k=8)
        results.append(result)
        print("\n")
    
    # Save Q&A results
    qa_path = summary_path.replace('repo_summary', 'qa_results')
    with open(qa_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Q&A results saved to: {qa_path}")


if __name__ == "__main__":
    asyncio.run(main())
