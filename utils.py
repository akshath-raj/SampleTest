"""
Utility functions for the GitHub Agent Workflow

This module provides helper functions for:
- Advanced file filtering
- Summary analysis
- Visualization of results
- Export to different formats
"""

import json
import os
from typing import List, Dict, Optional
from collections import Counter
from datetime import datetime
from pathlib import Path


class SummaryAnalyzer:
    """Analyze and visualize repository summaries"""
    
    def __init__(self, summary_path: str):
        """Load summary data"""
        with open(summary_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.metadata = self.data.get('metadata', {})
        self.summaries = self.data.get('summaries', [])
    
    def get_language_distribution(self) -> Dict[str, int]:
        """Get count of files by programming language"""
        languages = [s['language'] for s in self.summaries if s.get('language')]
        return dict(Counter(languages))
    
    def get_top_dependencies(self, top_n: int = 10) -> List[tuple]:
        """Get most common dependencies across all files"""
        all_deps = []
        for summary in self.summaries:
            all_deps.extend(summary.get('dependencies', []))
        
        dep_counts = Counter(all_deps)
        return dep_counts.most_common(top_n)
    
    def get_top_concepts(self, top_n: int = 20) -> List[tuple]:
        """Get most common key concepts"""
        all_concepts = []
        for summary in self.summaries:
            all_concepts.extend(summary.get('key_concepts', []))
        
        concept_counts = Counter(all_concepts)
        return concept_counts.most_common(top_n)
    
    def search_summaries(self, keyword: str) -> List[Dict]:
        """Search for files containing a keyword"""
        keyword_lower = keyword.lower()
        matching = []
        
        for summary in self.summaries:
            searchable = f"{summary['path']} {summary['summary']} {summary['purpose']}".lower()
            if keyword_lower in searchable:
                matching.append(summary)
        
        return matching
    
    def get_files_by_size(self, min_size: int = 0, max_size: int = float('inf')) -> List[Dict]:
        """Get files within a size range"""
        return [
            s for s in self.summaries 
            if min_size <= s['size'] <= max_size
        ]
    
    def get_largest_files(self, top_n: int = 10) -> List[Dict]:
        """Get largest files"""
        sorted_files = sorted(self.summaries, key=lambda x: x['size'], reverse=True)
        return sorted_files[:top_n]
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate a comprehensive analysis report"""
        report_lines = []
        
        # Header
        report_lines.append("="*80)
        report_lines.append("GitHub Repository Analysis Report")
        report_lines.append("="*80)
        report_lines.append(f"\nRepository: {self.metadata.get('repo_url', 'Unknown')}")
        report_lines.append(f"Analysis Date: {self.metadata.get('timestamp', 'Unknown')}")
        report_lines.append(f"Total Files: {self.metadata.get('total_files', 0)}")
        report_lines.append(f"Total Size: {self.metadata.get('total_size', 0) / 1024:.2f} KB")
        report_lines.append(f"Processing Time: {self.metadata.get('processing_time', 0):.2f}s")
        
        # Language distribution
        report_lines.append("\n" + "="*80)
        report_lines.append("Language Distribution")
        report_lines.append("="*80)
        lang_dist = self.get_language_distribution()
        for lang, count in sorted(lang_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.summaries)) * 100
            report_lines.append(f"{lang:20s}: {count:4d} files ({percentage:5.1f}%)")
        
        # Top dependencies
        report_lines.append("\n" + "="*80)
        report_lines.append("Top 10 Dependencies")
        report_lines.append("="*80)
        top_deps = self.get_top_dependencies(10)
        for dep, count in top_deps:
            report_lines.append(f"{dep:30s}: {count:3d} occurrences")
        
        # Top concepts
        report_lines.append("\n" + "="*80)
        report_lines.append("Top 20 Key Concepts")
        report_lines.append("="*80)
        top_concepts = self.get_top_concepts(20)
        for concept, count in top_concepts:
            report_lines.append(f"{concept:30s}: {count:3d} files")
        
        # Largest files
        report_lines.append("\n" + "="*80)
        report_lines.append("10 Largest Files")
        report_lines.append("="*80)
        largest = self.get_largest_files(10)
        for f in largest:
            size_kb = f['size'] / 1024
            report_lines.append(f"{f['path']:50s}: {size_kb:8.2f} KB")
        
        # File type distribution
        report_lines.append("\n" + "="*80)
        report_lines.append("File Type Distribution")
        report_lines.append("="*80)
        file_types = self.metadata.get('file_types', {})
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"{ext:20s}: {count:4d} files")
        
        report = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report


class FileFilter:
    """Advanced file filtering utilities"""
    
    @staticmethod
    def filter_by_extension(files: List[Dict], extensions: List[str]) -> List[Dict]:
        """Filter files by extension"""
        return [
            f for f in files 
            if any(f['path'].endswith(ext) for ext in extensions)
        ]
    
    @staticmethod
    def filter_by_directory(files: List[Dict], directory: str) -> List[Dict]:
        """Filter files in a specific directory"""
        return [
            f for f in files 
            if f['path'].startswith(directory)
        ]
    
    @staticmethod
    def filter_by_language(summaries: List[Dict], language: str) -> List[Dict]:
        """Filter summaries by programming language"""
        return [
            s for s in summaries 
            if s.get('language', '').lower() == language.lower()
        ]
    
    @staticmethod
    def exclude_tests(files: List[Dict]) -> List[Dict]:
        """Exclude test files"""
        test_patterns = ['test_', '_test.', '/tests/', '/test/']
        return [
            f for f in files 
            if not any(pattern in f['path'].lower() for pattern in test_patterns)
        ]
    
    @staticmethod
    def exclude_config(files: List[Dict]) -> List[Dict]:
        """Exclude configuration files"""
        config_exts = ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']
        return [
            f for f in files 
            if not any(f['path'].endswith(ext) for ext in config_exts)
        ]
    
    @staticmethod
    def only_source_code(files: List[Dict]) -> List[Dict]:
        """Keep only source code files"""
        source_exts = [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', 
            '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala'
        ]
        return FileFilter.filter_by_extension(files, source_exts)


class ExportUtilities:
    """Export summaries and results to different formats"""
    
    @staticmethod
    def export_to_markdown(summary_path: str, output_path: str):
        """Export summary to Markdown format"""
        analyzer = SummaryAnalyzer(summary_path)
        
        md_lines = []
        md_lines.append(f"# Repository Analysis: {analyzer.metadata.get('repo_url', 'Unknown')}\n")
        md_lines.append(f"**Analysis Date**: {analyzer.metadata.get('timestamp', 'Unknown')}\n")
        md_lines.append(f"**Total Files**: {analyzer.metadata.get('total_files', 0)}\n")
        
        md_lines.append("\n## Language Distribution\n")
        lang_dist = analyzer.get_language_distribution()
        for lang, count in sorted(lang_dist.items(), key=lambda x: x[1], reverse=True):
            md_lines.append(f"- **{lang}**: {count} files")
        
        md_lines.append("\n## Top Dependencies\n")
        top_deps = analyzer.get_top_dependencies(15)
        for dep, count in top_deps:
            md_lines.append(f"- `{dep}`: {count} occurrences")
        
        md_lines.append("\n## File Summaries\n")
        for summary in analyzer.summaries[:50]:  # Limit to first 50
            md_lines.append(f"\n### {summary['path']}\n")
            md_lines.append(f"**Language**: {summary.get('language', 'Unknown')}\n")
            md_lines.append(f"**Purpose**: {summary.get('purpose', 'Unknown')}\n")
            md_lines.append(f"**Summary**: {summary.get('summary', 'No summary')}\n")
            
            if summary.get('key_concepts'):
                md_lines.append(f"**Key Concepts**: {', '.join(summary['key_concepts'][:5])}\n")
        
        md_content = "\n".join(md_lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown report exported to: {output_path}")
    
    @staticmethod
    def export_to_csv(summary_path: str, output_path: str):
        """Export basic summary information to CSV"""
        analyzer = SummaryAnalyzer(summary_path)
        
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Path', 'Language', 'Size', 'Purpose', 'Key Concepts'])
            
            for summary in analyzer.summaries:
                writer.writerow([
                    summary['path'],
                    summary.get('language', ''),
                    summary['size'],
                    summary.get('purpose', ''),
                    ', '.join(summary.get('key_concepts', [])[:3])
                ])
        
        print(f"✅ CSV exported to: {output_path}")


def compare_repositories(summary_path1: str, summary_path2: str) -> Dict:
    """Compare two repositories"""
    analyzer1 = SummaryAnalyzer(summary_path1)
    analyzer2 = SummaryAnalyzer(summary_path2)
    
    comparison = {
        'repo1': {
            'url': analyzer1.metadata.get('repo_url'),
            'total_files': len(analyzer1.summaries),
            'languages': analyzer1.get_language_distribution(),
            'top_concepts': dict(analyzer1.get_top_concepts(10))
        },
        'repo2': {
            'url': analyzer2.metadata.get('repo_url'),
            'total_files': len(analyzer2.summaries),
            'languages': analyzer2.get_language_distribution(),
            'top_concepts': dict(analyzer2.get_top_concepts(10))
        }
    }
    
    # Find common concepts
    concepts1 = set(analyzer1.get_top_concepts(50))
    concepts2 = set(analyzer2.get_top_concepts(50))
    comparison['common_concepts'] = list(concepts1.intersection(concepts2))
    
    return comparison


def create_question_templates(domain: str) -> List[str]:
    """Generate question templates for common domains"""
    templates = {
        'api': [
            "How do I authenticate with this API?",
            "What endpoints are available?",
            "How do I handle errors in API calls?",
            "What rate limiting is implemented?",
            "How do I make async requests?"
        ],
        'web_framework': [
            "How is routing configured?",
            "What middleware is used?",
            "How are templates rendered?",
            "How is database integration handled?",
            "What authentication methods are supported?"
        ],
        'library': [
            "What are the main classes and their purposes?",
            "How do I install and import this library?",
            "What are some usage examples?",
            "How is error handling implemented?",
            "What dependencies does this library have?"
        ],
        'cli_tool': [
            "What command-line options are available?",
            "How do I configure this tool?",
            "What are the main commands?",
            "How do I extend this tool?",
            "What output formats are supported?"
        ],
        'general': [
            "What is the purpose of this project?",
            "How is the project structured?",
            "What are the main features?",
            "How do I contribute to this project?",
            "What testing framework is used?"
        ]
    }
    
    return templates.get(domain, templates['general'])


if __name__ == "__main__":
    # Example usage
    print("🔧 Utility Module for GitHub Agent Workflow")
    print("\nThis module provides:")
    print("  - SummaryAnalyzer: Analyze and visualize summaries")
    print("  - FileFilter: Advanced file filtering")
    print("  - ExportUtilities: Export to Markdown/CSV")
    print("  - Helper functions for common tasks")
