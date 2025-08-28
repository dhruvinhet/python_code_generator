try:
    import pandas as pd
    import numpy as np
    import json
    from typing import Dict, List, Any, Tuple
    import re
    from datetime import datetime
    import io
    import csv
    from werkzeug.datastructures import FileStorage
    import google.generativeai as genai
    from config import Config
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    import base64
    
    PANDAS_AVAILABLE = True
except ImportError as e:
    PANDAS_AVAILABLE = False
    IMPORT_ERROR = str(e)

class DataCleaner:
    """AI-powered data cleaning service"""
    
    def __init__(self):
        if not PANDAS_AVAILABLE:
            raise ImportError(f"Required dependencies not available: {IMPORT_ERROR}")
        
        # Configure Gemini AI
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.ai_available = True
        else:
            self.ai_available = False
            
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json']
    
    def generate_data_quality_graphs(self, file: FileStorage) -> Dict[str, Any]:
        """Generate matplotlib/seaborn graphs for data quality visualization"""
        try:
            # Read data
            filename = file.filename.lower()
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file.stream)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.stream)
            elif filename.endswith('.json'):
                data = json.load(file.stream)
                df = pd.json_normalize(data)
            else:
                raise ValueError("Unsupported file format")
            
            # Set style for better graphs
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Make graphs smaller and more compact
            plt.rcParams.update({
                'figure.figsize': (8, 6),
                'font.size': 10,
                'axes.titlesize': 12,
                'axes.labelsize': 10,
                'xtick.labelsize': 8,
                'ytick.labelsize': 8,
                'legend.fontsize': 9
            })
            
            graphs = {}
            
            # 1. Missing Values Heatmap
            if df.isnull().any().any():
                plt.figure(figsize=(12, 8))
                missing_data = df.isnull()
                
                # Create a more informative heatmap
                sns.heatmap(missing_data, 
                           cbar=True, 
                           cmap='RdYlBu_r',  # Better color scheme
                           yticklabels=False, 
                           xticklabels=True,
                           cbar_kws={'label': 'Missing Values (White=Missing, Blue=Present)'},
                           linewidths=0.1,
                           linecolor='gray')
                
                plt.title('Missing Values Pattern Analysis', fontsize=14, pad=20)
                plt.xlabel('Column Names', fontsize=12)
                plt.ylabel(f'Rows (Total: {len(df):,})', fontsize=12)
                plt.xticks(rotation=45, ha='right', fontsize=10)
                
                # Add summary text
                missing_summary = f"Total Missing: {df.isnull().sum().sum():,} cells ({(df.isnull().sum().sum()/(df.shape[0]*df.shape[1])*100):.1f}%)"
                plt.figtext(0.02, 0.02, missing_summary, fontsize=10, 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
                
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
                buffer.seek(0)
                graphs['missing_values_heatmap'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # 2. Data Types Distribution
            plt.figure(figsize=(8, 6))
            type_counts = df.dtypes.value_counts()
            colors = sns.color_palette("husl", len(type_counts))
            plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', 
                   startangle=90, colors=colors)
            plt.title('Data Types Distribution', fontsize=12, pad=20)
            plt.axis('equal')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            graphs['data_types_distribution'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # 3. Missing Values Bar Chart
            missing_counts = df.isnull().sum()
            missing_counts = missing_counts[missing_counts > 0]
            if len(missing_counts) > 0:
                plt.figure(figsize=(10, 5))
                bars = missing_counts.plot(kind='bar', color='salmon', alpha=0.7)
                plt.title('Missing Values Count by Column', fontsize=12, pad=20)
                plt.xlabel('Columns')
                plt.ylabel('Missing Values Count')
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate(missing_counts.values):
                    plt.text(i, v + 0.1, str(v), ha='center', va='bottom')
                
                plt.tight_layout()
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                graphs['missing_values_bar'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # 4. Data Completeness
            plt.figure(figsize=(6, 6))
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            complete_cells = total_cells - missing_cells
            
            sizes = [complete_cells, missing_cells]
            labels = ['Complete Data', 'Missing Data']
            colors = ['lightgreen', 'lightcoral']
            explode = (0.1, 0)  # explode the missing data slice
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
                   startangle=90, explode=explode, shadow=True)
            plt.title('Overall Data Completeness', fontsize=12, pad=20)
            plt.axis('equal')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            graphs['data_completeness'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # 5. Numeric Columns Distribution
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                n_cols = min(4, len(numeric_columns))
                plt.figure(figsize=(15, 4))
                for i, col in enumerate(numeric_columns[:n_cols]):
                    plt.subplot(1, n_cols, i+1)
                    df[col].hist(bins=20, alpha=0.7, color=f'C{i}', edgecolor='black')
                    plt.title(f'{col}', fontsize=10)
                    plt.xlabel(col, fontsize=9)
                    plt.ylabel('Frequency', fontsize=9)
                    plt.grid(alpha=0.3)
                
                plt.suptitle('Numeric Columns Distribution', fontsize=12)
                plt.tight_layout()
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                graphs['numeric_distributions'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # 6. Correlation Matrix
            if len(numeric_columns) > 1:
                plt.figure(figsize=(8, 6))
                correlation_matrix = df[numeric_columns].corr()
                mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
                sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', 
                           center=0, square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
                plt.title('Correlation Matrix of Numeric Columns', fontsize=12, pad=20)
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                graphs['correlation_matrix'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # 7. Outliers Detection (Box Plots)
            if len(numeric_columns) > 0:
                n_cols = min(4, len(numeric_columns))
                plt.figure(figsize=(15, 4))
                for i, col in enumerate(numeric_columns[:n_cols]):
                    plt.subplot(1, n_cols, i+1)
                    sns.boxplot(y=df[col], color=f'C{i}')
                    plt.title(f'{col}', fontsize=10)
                    plt.ylabel(col, fontsize=9)
                
                plt.suptitle('Outliers Detection (Box Plots)', fontsize=12)
                plt.tight_layout()
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                graphs['outliers_detection'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # 8. Text Data Analysis (String length distribution)
            text_columns = df.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                plt.figure(figsize=(8, 5))
                for i, col in enumerate(text_columns[:3]):  # Show first 3 text columns
                    lengths = df[col].astype(str).str.len()
                    plt.hist(lengths, bins=20, alpha=0.6, label=col, edgecolor='black')
                
                plt.title('Text Data Length Distribution', fontsize=12, pad=20)
                plt.xlabel('Character Length')
                plt.ylabel('Frequency')
                plt.legend()
                plt.grid(alpha=0.3)
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                graphs['text_analysis'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # 9. Data Quality Heatmap (Missing + Data Types)
            plt.figure(figsize=(10, 6))
            quality_matrix = pd.DataFrame(index=df.columns, columns=['Missing %', 'Data Type'])
            
            for col in df.columns:
                missing_pct = (df[col].isnull().sum() / len(df)) * 100
                quality_matrix.loc[col, 'Missing %'] = missing_pct
                quality_matrix.loc[col, 'Data Type'] = 1 if df[col].dtype == 'object' else 0
            
            quality_matrix = quality_matrix.astype(float)
            sns.heatmap(quality_matrix.T, annot=True, cmap='RdYlBu_r', 
                       cbar_kws={'label': 'Quality Score'}, fmt='.1f')
            plt.title('Data Quality Overview', fontsize=12, pad=20)
            plt.xlabel('Columns')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            graphs['quality_heatmap'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            # 10. Categorical Value Counts
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                plt.figure(figsize=(10, 6))
                col = categorical_cols[0]  # Take first categorical column
                top_values = df[col].value_counts().head(10)
                
                bars = plt.bar(range(len(top_values)), top_values.values, 
                              color=sns.color_palette("viridis", len(top_values)))
                plt.title(f'Top Values in "{col}" Column', fontsize=12, pad=20)
                plt.xlabel('Categories')
                plt.ylabel('Count')
                plt.xticks(range(len(top_values)), top_values.index, rotation=45, ha='right')
                
                # Add value labels on bars
                for i, v in enumerate(top_values.values):
                    plt.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=9)
                
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                buffer.seek(0)
                graphs['categorical_counts'] = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
            
            # Reset file stream
            file.stream.seek(0)
            
            return {
                'success': True,
                'graphs': graphs,
                'stats': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'missing_percentage': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100),
                    'numeric_columns': len(numeric_columns),
                    'categorical_columns': len(categorical_cols),
                    'graphs_generated': len(graphs)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_file(self, file: FileStorage) -> Dict[str, Any]:
        """Analyze uploaded file and return preview with basic stats"""
        try:
            # Determine file type and read data
            filename = file.filename.lower()
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file.stream)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.stream)
            elif filename.endswith('.json'):
                data = json.load(file.stream)
                df = pd.json_normalize(data)
            else:
                raise ValueError("Unsupported file format")
            
            # Reset file stream position
            file.stream.seek(0)
            
            # Basic stats
            rows, columns = df.shape
            column_names = df.columns.tolist()
            
            # Sample data (first 5 rows)
            sample_data = []
            for _, row in df.head(5).iterrows():
                sample_data.append([str(val) if pd.notna(val) else '' for val in row])
            
            return {
                'success': True,
                'filename': file.filename,
                'size': len(file.read()),
                'rows': rows,
                'columns': columns,
                'column_names': column_names,
                'sample_data': sample_data,
                'data_types': df.dtypes.astype(str).to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def ai_analysis(self, file: FileStorage) -> Dict[str, Any]:
        """Perform AI-powered analysis to detect data quality issues"""
        try:
            # Read data
            filename = file.filename.lower()
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file.stream)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.stream)
            elif filename.endswith('.json'):
                data = json.load(file.stream)
                df = pd.json_normalize(data)
            
            # Basic statistics and data overview
            basic_stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': df.dtypes.astype(str).to_dict(),
                'missing_values_per_column': df.isnull().sum().to_dict(),
                'duplicate_rows': int(df.duplicated().sum()),
                'sample_data': df.head(5).fillna('NULL').to_dict('records')
            }
            
            # Use AI to analyze data quality if available
            if self.ai_available:
                ai_analysis = self._get_ai_analysis(df, basic_stats)
                issues = ai_analysis.get('issues', [])
                recommendations = ai_analysis.get('recommendations', [])
                quality_score = ai_analysis.get('quality_score', 80)
            else:
                # Fallback to basic analysis
                issues, recommendations, quality_score = self._basic_analysis(df, basic_stats)
            
            return {
                'success': True,
                'issues': issues,
                'quality_score': quality_score,
                'recommendations': recommendations,
                'analysis_summary': basic_stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_ai_analysis(self, df: pd.DataFrame, basic_stats: Dict) -> Dict[str, Any]:
        """Use Gemini AI to analyze data quality"""
        try:
            # Prepare data summary for AI
            data_summary = f"""
            Dataset Analysis Request:
            
            Dataset Overview:
            - Total Rows: {basic_stats['total_rows']}
            - Total Columns: {basic_stats['total_columns']}
            - Column Names: {', '.join(basic_stats['column_names'])}
            - Data Types: {json.dumps(basic_stats['data_types'], indent=2)}
            - Missing Values: {json.dumps(basic_stats['missing_values_per_column'], indent=2)}
            - Duplicate Rows: {basic_stats['duplicate_rows']}
            
            Sample Data (First 5 rows):
            {json.dumps(basic_stats['sample_data'], indent=2)}
            
            Please analyze this dataset and identify SPECIFIC data quality issues with ACTUAL EXAMPLES from the data. For each issue found, provide:
            1. Issue type (e.g., "Missing Values", "Data Type Inconsistency", "Invalid Format", "Outliers", "Duplicate Data", etc.)
            2. Severity level (high/medium/low)
            3. Column name if applicable  
            4. Description with ACTUAL VALUES found in the data that are problematic
            5. Count of affected items
            6. Specific rows or examples of the problematic data
            
            Also provide:
            - Data quality score (0-100)
            - Specific recommendations for cleaning
            
            IMPORTANT: Look at the actual sample data provided and identify REAL issues. For example:
            - If you see email "invalid@" in the data, report "Invalid email format: 'invalid@' found in email column"
            - If you see country "Atlantis" in the data, report "Invalid country: 'Atlantis' is not a real country"
            - If you see salary "abc" in a numeric column, report "Non-numeric value 'abc' found in salary column"
            - If you see missing values (null/empty), report exactly which fields are missing
            
            Focus on ACTUAL data issues from the sample data shown, not generic possibilities.
            
            Return your analysis in this JSON format:
            {{
                "issues": [
                    {{
                        "type": "Issue Type",
                        "severity": "high/medium/low", 
                        "column": "column_name or null",
                        "description": "SPECIFIC description with actual problematic values from the data",
                        "count": number_of_affected_items,
                        "examples": ["actual problematic value 1", "actual problematic value 2"]
                    }}
                ],
                "quality_score": score_0_to_100,
                "recommendations": [
                    "Specific recommendation based on actual issues found"
                ]
            }}
            """
            
            response = self.model.generate_content(data_summary)
            
            # Try to parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            ai_result = json.loads(response_text)
            return ai_result
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Fallback to basic analysis
            return self._basic_analysis(df, basic_stats)
    
    def _basic_analysis(self, df: pd.DataFrame, basic_stats: Dict) -> Tuple[List[Dict], List[str], int]:
        """Fallback basic analysis when AI is not available"""
        issues = []
        recommendations = []
        
        # Check for missing values
        for col, missing_count in basic_stats['missing_values_per_column'].items():
            if missing_count > 0:
                issues.append({
                    'type': 'Missing Values',
                    'severity': 'medium' if missing_count < len(df) * 0.1 else 'high',
                    'column': col,
                    'description': f'{missing_count} missing values detected in column "{col}"',
                    'count': int(missing_count)
                })
                recommendations.append(f'Handle missing values in "{col}" column')
        
        # Check for duplicates
        if basic_stats['duplicate_rows'] > 0:
            issues.append({
                'type': 'Duplicate Rows',
                'severity': 'medium',
                'column': None,
                'description': f'{basic_stats["duplicate_rows"]} duplicate rows found',
                'count': basic_stats['duplicate_rows']
            })
            recommendations.append('Remove duplicate rows')
        
        # Basic data type checks
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed types in text columns
                unique_types = set(type(val).__name__ for val in df[col].dropna().head(100))
                if len(unique_types) > 1:
                    issues.append({
                        'type': 'Mixed Data Types',
                        'severity': 'medium',
                        'column': col,
                        'description': f'Column "{col}" contains mixed data types',
                        'count': 1
                    })
                    recommendations.append(f'Standardize data types in "{col}" column')
        
        # Calculate quality score
        total_cells = len(df) * len(df.columns)
        issues_count = sum(issue['count'] for issue in issues)
        quality_score = max(0, min(100, int((1 - issues_count / total_cells) * 100)))
        
        if not issues:
            issues.append({
                'type': 'Data Quality Check',
                'severity': 'low',
                'column': None,
                'description': 'No major data quality issues detected in basic analysis',
                'count': 0
            })
            recommendations.append('Data appears to be in good condition')
        
        return issues, recommendations, quality_score
    
    def clean_data(self, file: FileStorage, options: Dict[str, bool]) -> Dict[str, Any]:
        """Clean data based on selected options"""
        try:
            # Read data
            filename = file.filename.lower()
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file.stream)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.stream)
            elif filename.endswith('.json'):
                data = json.load(file.stream)
                df = pd.json_normalize(data)
            
            original_shape = df.shape
            cleaning_log = []
            
            # Remove duplicates
            if options.get('removeDuplicates', True):
                before_dup = len(df)
                df = df.drop_duplicates()
                after_dup = len(df)
                if before_dup != after_dup:
                    cleaning_log.append(f'Removed {before_dup - after_dup} duplicate rows')
            
            # Handle missing values
            if options.get('handleMissingValues', True):
                for col in df.columns:
                    if df[col].dtype in ['object', 'string']:
                        # For text columns, fill with most frequent value
                        mode_val = df[col].mode()
                        if not mode_val.empty:
                            missing_count = df[col].isnull().sum()
                            df[col].fillna(mode_val[0], inplace=True)
                            if missing_count > 0:
                                cleaning_log.append(f'Filled {missing_count} missing values in "{col}" with mode')
                    else:
                        # For numeric columns, fill with median
                        median_val = df[col].median()
                        missing_count = df[col].isnull().sum()
                        df[col].fillna(median_val, inplace=True)
                        if missing_count > 0:
                            cleaning_log.append(f'Filled {missing_count} missing values in "{col}" with median')
            
            # Validate data types
            if options.get('validateDataTypes', True):
                for col in df.columns:
                    if self._should_be_numeric(df[col]):
                        # Convert to numeric, errors='coerce' will turn invalid values to NaN
                        numeric_col = pd.to_numeric(df[col], errors='coerce')
                        invalid_count = df[col].notna().sum() - numeric_col.notna().sum()
                        if invalid_count > 0:
                            df[col] = numeric_col
                            cleaning_log.append(f'Converted {invalid_count} invalid values to NaN in "{col}"')
            
            # Standardize formats
            if options.get('standardizeFormats', True):
                # Standardize email formats
                email_cols = [col for col in df.columns if 'email' in col.lower()]
                for col in email_cols:
                    df[col] = df[col].str.lower().str.strip()
                    cleaning_log.append(f'Standardized email format in "{col}"')
                
                # Standardize country names
                country_cols = [col for col in df.columns if 'country' in col.lower()]
                for col in country_cols:
                    df[col] = df[col].str.title().str.strip()
                    cleaning_log.append(f'Standardized country format in "{col}"')
            
            # Detect and handle outliers
            if options.get('detectOutliers', True):
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    outliers = self._detect_outliers(df[col])
                    if len(outliers) > 0:
                        # Cap outliers at 95th percentile
                        upper_limit = df[col].quantile(0.95)
                        lower_limit = df[col].quantile(0.05)
                        df[col] = df[col].clip(lower=lower_limit, upper=upper_limit)
                        cleaning_log.append(f'Capped {len(outliers)} outliers in "{col}"')
            
            # Generate cleaned data
            output = io.StringIO()
            df.to_csv(output, index=False)
            cleaned_csv = output.getvalue()
            
            return {
                'success': True,
                'cleaned_data': cleaned_csv,
                'cleaning_log': cleaning_log,
                'before_stats': {
                    'rows': original_shape[0],
                    'columns': original_shape[1]
                },
                'after_stats': {
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'filename': f"cleaned_{file.filename}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def manual_clean_data(self, file: FileStorage, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform manual cleaning operations on data"""
        try:
            # Read data
            filename = file.filename.lower()
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file.stream)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.stream)
            elif filename.endswith('.json'):
                data = json.load(file.stream)
                df = pd.json_normalize(data)
            
            original_shape = df.shape
            cleaning_log = []
            
            if operation == 'filter_rows':
                # Filter rows based on conditions
                column = parameters.get('column')
                condition = parameters.get('condition')
                value = parameters.get('value')
                
                if column and condition and value is not None:
                    if condition == 'equals':
                        df = df[df[column] == value]
                    elif condition == 'not_equals':
                        df = df[df[column] != value]
                    elif condition == 'contains':
                        df = df[df[column].astype(str).str.contains(value, na=False)]
                    elif condition == 'greater_than':
                        df = df[pd.to_numeric(df[column], errors='coerce') > float(value)]
                    elif condition == 'less_than':
                        df = df[pd.to_numeric(df[column], errors='coerce') < float(value)]
                    
                    removed_rows = original_shape[0] - len(df)
                    cleaning_log.append(f'Filtered rows: removed {removed_rows} rows based on {column} {condition} {value}')
            
            elif operation == 'find_replace':
                # Find and replace values
                column = parameters.get('column')
                find_value = parameters.get('find_value')
                replace_value = parameters.get('replace_value')
                
                if column and find_value is not None and replace_value is not None:
                    if column in df.columns:
                        count = df[column].astype(str).str.count(find_value).sum()
                        df[column] = df[column].astype(str).str.replace(find_value, replace_value)
                        cleaning_log.append(f'Replaced {count} occurrences of "{find_value}" with "{replace_value}" in {column}')
            
            elif operation == 'remove_columns':
                # Remove specified columns
                columns_to_remove = parameters.get('columns', [])
                existing_columns = [col for col in columns_to_remove if col in df.columns]
                if existing_columns:
                    df = df.drop(columns=existing_columns)
                    cleaning_log.append(f'Removed columns: {", ".join(existing_columns)}')
            
            elif operation == 'transform_data':
                # Data transformations
                column = parameters.get('column')
                transformation = parameters.get('transformation')
                
                if column and transformation and column in df.columns:
                    if transformation == 'uppercase':
                        df[column] = df[column].astype(str).str.upper()
                        cleaning_log.append(f'Converted {column} to uppercase')
                    elif transformation == 'lowercase':
                        df[column] = df[column].astype(str).str.lower()
                        cleaning_log.append(f'Converted {column} to lowercase')
                    elif transformation == 'trim_whitespace':
                        df[column] = df[column].astype(str).str.strip()
                        cleaning_log.append(f'Trimmed whitespace in {column}')
                    elif transformation == 'to_numeric':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                        cleaning_log.append(f'Converted {column} to numeric')
                    elif transformation == 'to_datetime':
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                        cleaning_log.append(f'Converted {column} to datetime')
            
            # Generate cleaned data
            output = io.StringIO()
            df.to_csv(output, index=False)
            cleaned_csv = output.getvalue()
            
            return {
                'success': True,
                'cleaned_data': cleaned_csv,
                'cleaning_log': cleaning_log,
                'before_stats': {
                    'rows': original_shape[0],
                    'columns': original_shape[1]
                },
                'after_stats': {
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'filename': f"manually_cleaned_{file.filename}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _should_be_numeric(self, series: pd.Series) -> bool:
        """Determine if a series should be numeric based on majority of values"""
        try:
            non_null_series = series.dropna()
            if len(non_null_series) == 0:
                return False
            
            # Try to convert to numeric
            numeric_series = pd.to_numeric(non_null_series, errors='coerce')
            numeric_count = numeric_series.notna().sum()
            
            # If more than 80% can be converted to numeric, consider it should be numeric
            return (numeric_count / len(non_null_series)) > 0.8
        except:
            return False

# Global data cleaner instance
try:
    data_cleaner = DataCleaner()
except Exception as e:
    print(f"Error initializing DataCleaner: {e}")
    data_cleaner = None
