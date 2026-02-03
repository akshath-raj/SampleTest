"""
Simple example demonstrating the GitHub Agent Workflow

This script shows how to:
1. Process a repository
2. Ask questions about it
3. Save results
"""

import asyncio
import os
from github_agent_workflow import GitHubAgentWorkflow


async def analyze_repository():
    """Example: Analyze a GitHub repository and ask questions"""
    
    # Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Optional
    
    # Initialize the workflow
    print("🚀 Initializing GitHub Agent Workflow...")
    workflow = GitHubAgentWorkflow(
        gemini_api_key=GEMINI_API_KEY,
        github_token=GITHUB_TOKEN
    )
    
    # Example 1: Analyze a popular repository
    # You can replace this with any public GitHub repository
    repo_url = "https://github.com/fastapi/fastapi"
    
    print(f"\n📦 Processing repository: {repo_url}")
    print("⏳ This will take a few minutes...\n")
    
    # Process the repository (fetch + summarize)
    summary_path = await workflow.process_repository(
        repo_url=repo_url,
        output_dir="./my_analysis"
    )
    
    print(f"\n✅ Repository processed!")
    print(f"📄 Summary saved to: {summary_path}")
    
    # Example 2: Ask questions about the repository
    print("\n" + "="*80)
    print("🤔 Now asking questions about the repository...")
    print("="*80 + "\n")
    
    questions = [
        "What is FastAPI and what are its main features?",
        "How does FastAPI handle dependency injection?",
        "What testing framework does FastAPI use?",
        "How is routing implemented in FastAPI?",
    ]
    
    all_results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"Question {i}/{len(questions)}: {question}")
        print(f"{'='*80}")
        
        # Ask the question (decider selects files, answerer generates response)
        result = await workflow.ask_question(
            question=question,
            top_k=8  # Analyze top 8 most relevant files
        )
        
        all_results.append(result)
        
        print(f"\n📁 Files analyzed:")
        for file_path in result['selected_files']:
            print(f"   - {file_path}")
        
        print(f"\n💡 Answer:")
        print(f"{result['answer']}\n")
    
    # Example 3: Save all Q&A results
    import json
    qa_output_path = "./my_analysis/qa_results.json"
    
    with open(qa_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ All Q&A results saved to: {qa_output_path}")
    
    # Example 4: Demonstrate loading existing summary
    print("\n" + "="*80)
    print("💾 You can also load previously saved summaries...")
    print("="*80 + "\n")
    
    # Create a new workflow instance
    workflow2 = GitHubAgentWorkflow(
        gemini_api_key=GEMINI_API_KEY,
        github_token=GITHUB_TOKEN
    )
    
    # Load the summary we just created
    workflow2.load_existing_summary(summary_path)
    
    # Ask a new question using the loaded summary
    new_question = "How does FastAPI achieve high performance?"
    print(f"Question: {new_question}\n")
    
    result = await workflow2.ask_question(new_question, top_k=5)
    
    print(f"Answer: {result['answer']}\n")
    
    print("="*80)
    print("✨ Example completed successfully!")
    print("="*80)


async def quick_example():
    """Quick example with a smaller repository"""
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    workflow = GitHubAgentWorkflow(GEMINI_API_KEY, GITHUB_TOKEN)
    
    # Use a smaller repository for faster processing
    repo_url = "https://github.com/anthropics/anthropic-sdk-python"
    
    print(f"🚀 Quick example with: {repo_url}\n")
    
    # Process repository
    await workflow.process_repository(repo_url)
    
    # Ask a single question
    question = "How do I authenticate with the Anthropic API?"
    result = await workflow.ask_question(question)
    
    print(f"\n❓ {question}")
    print(f"\n✅ {result['answer']}")


def main():
    """Main entry point"""
    import sys
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your-api-key-here':
        print("⚠️  WARNING: Please set your GEMINI_API_KEY environment variable")
        print("   export GEMINI_API_KEY='your-api-key'")
        print("\n   Or replace 'your-api-key-here' in this script\n")
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print("\nSelect example to run:")
    print("1. Full example (comprehensive, ~5-10 minutes)")
    print("2. Quick example (faster, ~2-3 minutes)")
    
    choice = input("\nChoice (1 or 2): ").strip()
    
    if choice == '1':
        asyncio.run(analyze_repository())
    elif choice == '2':
        asyncio.run(quick_example())
    else:
        print("Invalid choice. Please select 1 or 2.")


if __name__ == "__main__":
    main()
