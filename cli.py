"""
Interactive CLI for GitHub Repository Agent Workflow

This provides a user-friendly command-line interface for:
1. Processing GitHub repositories
2. Asking questions about the code
3. Managing analysis sessions
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from github_agent_workflow import GitHubAgentWorkflow
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class InteractiveCLI:
    """Interactive command-line interface"""
    
    def __init__(self, gemini_api_key: str, github_token: str = None):
        self.workflow = GitHubAgentWorkflow(gemini_api_key, github_token)
        self.current_repo = None
    
    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🤖 GitHub Repository Agentic Workflow")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def print_menu(self):
        """Print main menu"""
        print(f"\n{Fore.YELLOW}Available Commands:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}1.{Style.RESET_ALL} Process new repository")
        print(f"  {Fore.GREEN}2.{Style.RESET_ALL} Load existing summary")
        print(f"  {Fore.GREEN}3.{Style.RESET_ALL} Ask a question")
        print(f"  {Fore.GREEN}4.{Style.RESET_ALL} Show repository stats")
        print(f"  {Fore.GREEN}5.{Style.RESET_ALL} Exit")
        print()
    
    async def process_repo_interactive(self):
        """Interactive repository processing"""
        repo_url = input(f"{Fore.CYAN}Enter GitHub repository URL: {Style.RESET_ALL}").strip()
        
        if not repo_url:
            print(f"{Fore.RED}❌ Invalid URL{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}⏳ Processing repository... This may take a few minutes.{Style.RESET_ALL}\n")
        
        try:
            summary_path = await self.workflow.process_repository(repo_url)
            self.current_repo = repo_url
            print(f"\n{Fore.GREEN}✅ Repository processed successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Summary saved to: {summary_path}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error processing repository: {e}{Style.RESET_ALL}")
    
    def load_summary_interactive(self):
        """Interactive summary loading"""
        summary_path = input(f"{Fore.CYAN}Enter path to summary file: {Style.RESET_ALL}").strip()
        
        if not os.path.exists(summary_path):
            print(f"{Fore.RED}❌ File not found{Style.RESET_ALL}")
            return
        
        try:
            self.workflow.load_existing_summary(summary_path)
            print(f"{Fore.GREEN}✅ Summary loaded successfully!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading summary: {e}{Style.RESET_ALL}")
    
    async def ask_question_interactive(self):
        """Interactive question asking"""
        if self.workflow.summaries is None:
            print(f"{Fore.RED}❌ Please process a repository or load a summary first{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.YELLOW}💡 Tips for better questions:{Style.RESET_ALL}")
        print(f"  - Be specific about what you want to know")
        print(f"  - Ask about implementation details, architecture, or usage")
        print(f"  - Mention specific features or components if known\n")
        
        question = input(f"{Fore.CYAN}Your question: {Style.RESET_ALL}").strip()
        
        if not question:
            print(f"{Fore.RED}❌ Please enter a question{Style.RESET_ALL}")
            return
        
        try:
            # Ask about number of files to analyze
            top_k_input = input(f"{Fore.CYAN}How many files to analyze? (default: 10): {Style.RESET_ALL}").strip()
            top_k = int(top_k_input) if top_k_input else 10
            
            result = await self.workflow.ask_question(question, top_k=top_k)
            
            # Save individual Q&A
            if self.workflow.summary_path:
                qa_dir = os.path.dirname(self.workflow.summary_path)
                qa_file = os.path.join(qa_dir, f"qa_{len(os.listdir(qa_dir))}.txt")
                
                with open(qa_file, 'w', encoding='utf-8') as f:
                    f.write(f"Question: {result['question']}\n\n")
                    f.write(f"Selected Files:\n")
                    for path in result['selected_files']:
                        f.write(f"  - {path}\n")
                    f.write(f"\nAnswer:\n{result['answer']}\n")
                
                print(f"\n{Fore.CYAN}💾 Q&A saved to: {qa_file}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error answering question: {e}{Style.RESET_ALL}")
    
    def show_stats(self):
        """Show repository statistics"""
        if self.workflow.summaries is None:
            print(f"{Fore.RED}❌ No repository loaded{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}📊 Repository Statistics{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # Count by language
        lang_count = {}
        for summary in self.workflow.summaries:
            lang = summary.language or "Unknown"
            lang_count[lang] = lang_count.get(lang, 0) + 1
        
        print(f"\n{Fore.YELLOW}Files by Language:{Style.RESET_ALL}")
        for lang, count in sorted(lang_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {count}")
        
        print(f"\n{Fore.YELLOW}Total Files:{Style.RESET_ALL} {len(self.workflow.summaries)}")
        
        if self.workflow.repo_data:
            metadata = self.workflow.repo_data['metadata']
            print(f"{Fore.YELLOW}Total Size:{Style.RESET_ALL} {metadata['total_size'] / 1024:.2f} KB")
            print(f"{Fore.YELLOW}Processing Time:{Style.RESET_ALL} {metadata['processing_time']:.2f}s")
        
        print()
    
    async def run(self):
        """Main interactive loop"""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = input(f"{Fore.CYAN}Select an option (1-5): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                await self.process_repo_interactive()
            elif choice == '2':
                self.load_summary_interactive()
            elif choice == '3':
                await self.ask_question_interactive()
            elif choice == '4':
                self.show_stats()
            elif choice == '5':
                print(f"\n{Fore.GREEN}👋 Goodbye!{Style.RESET_ALL}\n")
                break
            else:
                print(f"{Fore.RED}❌ Invalid choice. Please select 1-5.{Style.RESET_ALL}")


async def batch_mode(args):
    """Batch mode for processing and answering questions"""
    workflow = GitHubAgentWorkflow(args.api_key, args.github_token)
    
    # Process repository
    if args.repo_url:
        print(f"{Fore.YELLOW}Processing repository...{Style.RESET_ALL}")
        summary_path = await workflow.process_repository(args.repo_url, args.output_dir)
    elif args.summary_file:
        workflow.load_existing_summary(args.summary_file)
    else:
        print(f"{Fore.RED}❌ Please provide either --repo-url or --summary-file{Style.RESET_ALL}")
        return
    
    # Answer questions from file
    if args.questions_file:
        with open(args.questions_file, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
        
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n{Fore.CYAN}Question {i}/{len(questions)}{Style.RESET_ALL}")
            result = await workflow.ask_question(question, top_k=args.top_k)
            results.append(result)
        
        # Save results
        import json
        output_file = os.path.join(args.output_dir, "batch_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}✅ Results saved to: {output_file}{Style.RESET_ALL}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub Repository Agentic Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python cli.py --api-key YOUR_API_KEY
  
  # Batch mode - process repo and answer questions
  python cli.py --api-key YOUR_API_KEY --repo-url https://github.com/user/repo --questions-file questions.txt
  
  # Use existing summary
  python cli.py --api-key YOUR_API_KEY --summary-file repo_summary.json --questions-file questions.txt
        """
    )
    
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--github-token', help='GitHub token (optional, or set GITHUB_TOKEN env var)')
    parser.add_argument('--repo-url', help='GitHub repository URL to process')
    parser.add_argument('--summary-file', help='Path to existing summary file')
    parser.add_argument('--questions-file', help='File containing questions (one per line)')
    parser.add_argument('--output-dir', default='./repo_analysis', help='Output directory')
    parser.add_argument('--top-k', type=int, default=10, help='Number of files to analyze per question')
    parser.add_argument('--batch', action='store_true', help='Run in batch mode (non-interactive)')
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print(f"{Fore.RED}❌ Please provide Gemini API key via --api-key or GEMINI_API_KEY env var{Style.RESET_ALL}")
        sys.exit(1)
    
    github_token = args.github_token or os.getenv('GITHUB_TOKEN')
    
    # Run appropriate mode
    if args.batch or args.questions_file:
        asyncio.run(batch_mode(args))
    else:
        cli = InteractiveCLI(api_key, github_token)
        asyncio.run(cli.run())


if __name__ == "__main__":
    main()
