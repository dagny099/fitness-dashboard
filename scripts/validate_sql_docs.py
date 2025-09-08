#!/usr/bin/env python3
"""
SQL Documentation Validation Script

This script validates all SQL queries in the MkDocs documentation by:
1. Extracting SQL code blocks from markdown files
2. Testing each query against the database
3. Reporting failures and successes
4. Providing fixes for common issues

Usage:
    python scripts/validate_sql_docs.py
    python scripts/validate_sql_docs.py --fix-common-issues
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pymysql
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.config.database import DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLValidator:
    """Validates SQL queries extracted from documentation."""
    
    def __init__(self, db_config: DatabaseConfig):
        """Initialize with database configuration."""
        self.db_config = db_config
        self.connection = None
        self.reserved_words = {
            'current_time', 'current_date', 'current_timestamp', 
            'date', 'time', 'timestamp', 'user', 'order', 'group'
        }
        
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = pymysql.connect(
                host=self.db_config.host,
                user=self.db_config.username,
                password=self.db_config.password,
                database=self.db_config.database,
                port=self.db_config.port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"Connected to MySQL {self.get_mysql_version()}")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_mysql_version(self) -> str:
        """Get MySQL version."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('SELECT VERSION();')
                result = cursor.fetchone()
                return result['VERSION()']
        except:
            return "Unknown"
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def extract_sql_blocks(self, file_path: str) -> List[Tuple[int, str]]:
        """Extract SQL code blocks from markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find SQL code blocks with line numbers
        sql_blocks = []
        lines = content.split('\n')
        in_sql_block = False
        current_sql = []
        start_line = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip() == '```sql':
                in_sql_block = True
                start_line = i + 1
                current_sql = []
            elif line.strip() == '```' and in_sql_block:
                if current_sql:
                    sql_content = '\n'.join(current_sql)
                    sql_blocks.append((start_line, sql_content))
                in_sql_block = False
            elif in_sql_block:
                current_sql.append(line)
        
        return sql_blocks
    
    def validate_query(self, query: str) -> Dict:
        """Validate a single SQL query."""
        result = {
            'success': False,
            'error': None,
            'row_count': 0,
            'execution_time': 0,
            'warnings': []
        }
        
        try:
            # Clean the query (remove comments and extra whitespace)
            query = self._clean_query(query)
            if not query.strip():
                result['warnings'].append('Empty query after cleaning')
                return result
            
            import time
            start_time = time.time()
            
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                result['row_count'] = len(rows)
                result['execution_time'] = time.time() - start_time
                result['success'] = True
                
        except Exception as e:
            result['error'] = str(e)
            
            # Analyze error and provide suggestions
            error_msg = str(e).lower()
            if 'only_full_group_by' in error_msg:
                result['suggestions'] = [
                    'Add all non-aggregated columns to GROUP BY clause',
                    'Use ANY_VALUE() for non-deterministic columns',
                    'Consider if the query logic is correct'
                ]
            elif 'syntax error' in error_msg:
                result['suggestions'] = [
                    'Check for reserved word usage in column aliases',
                    'Quote column aliases with backticks or single quotes',
                    'Verify SQL syntax is valid for MySQL'
                ]
        
        return result
    
    def _clean_query(self, query: str) -> str:
        """Clean query by removing comments and normalizing whitespace."""
        # Remove SQL comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        
        # Remove empty lines and normalize whitespace
        lines = [line.strip() for line in query.split('\n') if line.strip()]
        return ' '.join(lines)
    
    def suggest_fixes(self, query: str, error: str) -> List[str]:
        """Suggest fixes for common SQL errors."""
        suggestions = []
        
        if 'only_full_group_by' in error.lower():
            suggestions.append("Fix GROUP BY clause to include all non-aggregated columns")
            
            # Find GROUP BY clause
            group_by_match = re.search(r'GROUP BY\s+(.+?)(?:ORDER BY|HAVING|$)', query, re.IGNORECASE | re.DOTALL)
            if group_by_match:
                suggestions.append(f"Current GROUP BY: {group_by_match.group(1).strip()}")
        
        if 'syntax error' in error.lower() and ('current_time' in query or 'current_date' in query):
            suggestions.append("Quote reserved word aliases: 'current_time', 'current_date'")
        
        return suggestions
    
    def fix_common_issues(self, query: str) -> str:
        """Automatically fix common issues in SQL queries."""
        fixed_query = query
        
        # Fix reserved word aliases
        reserved_patterns = [
            (r'\bas current_time\b', "as 'current_time'"),
            (r'\bas current_date\b', "as 'current_date'"),
        ]
        
        for pattern, replacement in reserved_patterns:
            fixed_query = re.sub(pattern, replacement, fixed_query, flags=re.IGNORECASE)
        
        return fixed_query


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description='Validate SQL queries in documentation')
    parser.add_argument('--fix-common-issues', action='store_true', 
                       help='Attempt to automatically fix common issues')
    parser.add_argument('--docs-dir', default='docs', 
                       help='Documentation directory to scan (default: docs)')
    args = parser.parse_args()
    
    # Initialize database configuration
    db_config = DatabaseConfig.from_environment()
    if not db_config.validate():
        logger.error("Database configuration is incomplete")
        sys.exit(1)
    
    # Initialize validator
    validator = SQLValidator(db_config)
    if not validator.connect():
        sys.exit(1)
    
    try:
        # Find all markdown files in docs directory
        docs_dir = Path(args.docs_dir)
        if not docs_dir.exists():
            logger.error(f"Documentation directory not found: {docs_dir}")
            sys.exit(1)
        
        markdown_files = list(docs_dir.rglob('*.md'))
        logger.info(f"Found {len(markdown_files)} markdown files")
        
        total_queries = 0
        failed_queries = 0
        validation_results = []
        
        # Process each markdown file
        for md_file in markdown_files:
            logger.info(f"Processing: {md_file}")
            
            sql_blocks = validator.extract_sql_blocks(str(md_file))
            if not sql_blocks:
                continue
                
            logger.info(f"  Found {len(sql_blocks)} SQL blocks")
            
            for line_num, sql_content in sql_blocks:
                # Split multiple statements
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for stmt_idx, statement in enumerate(statements, 1):
                    total_queries += 1
                    
                    # Validate the query
                    result = validator.validate_query(statement)
                    
                    validation_results.append({
                        'file': str(md_file),
                        'line': line_num,
                        'statement': stmt_idx,
                        'query': statement[:100] + ('...' if len(statement) > 100 else ''),
                        'result': result
                    })
                    
                    if not result['success']:
                        failed_queries += 1
                        error_msg = result.get('error', 'Unknown error')
                        logger.error(f"  ❌ Line {line_num}, Statement {stmt_idx}: {str(error_msg)[:80]}...")
                        
                        if args.fix_common_issues:
                            fixed_query = validator.fix_common_issues(statement)
                            if fixed_query != statement:
                                logger.info(f"    🔧 Attempting fix...")
                                fix_result = validator.validate_query(fixed_query)
                                if fix_result['success']:
                                    logger.info(f"    ✅ Fix successful!")
                                else:
                                    logger.info(f"    ❌ Fix failed: {fix_result['error'][:50]}...")
                    else:
                        logger.info(f"  ✅ Line {line_num}, Statement {stmt_idx}: OK ({result['row_count']} rows)")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total queries tested: {total_queries}")
        print(f"Successful queries: {total_queries - failed_queries}")
        print(f"Failed queries: {failed_queries}")
        print(f"Success rate: {((total_queries - failed_queries) / total_queries * 100):.1f}%")
        
        if failed_queries > 0:
            print(f"\n{'='*60}")
            print(f"FAILED QUERIES DETAILS")
            print(f"{'='*60}")
            
            for result in validation_results:
                if not result['result']['success']:
                    print(f"\nFile: {result['file']}")
                    print(f"Line: {result['line']}, Statement: {result['statement']}")
                    print(f"Query: {result['query']}")
                    print(f"Error: {result['result']['error']}")
                    
                    if 'suggestions' in result['result']:
                        print("Suggestions:")
                        for suggestion in result['result']['suggestions']:
                            print(f"  - {suggestion}")
            
            sys.exit(1)
        else:
            print(f"\n🎉 All queries validated successfully!")
            
    finally:
        validator.disconnect()


if __name__ == '__main__':
    main()