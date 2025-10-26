from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import markdown
import pdfkit
from datetime import datetime
import tempfile

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.knowledge_base import KnowledgeBase
from rag.vector_store import PropertyVectorStore
from rag.query_engine import PropertyQueryEngine
from agents.orchestrator import PropertyOrchestrator
from reports.final_report_generator import FinalReportGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize property analysis system
knowledge_base = KnowledgeBase("knowledge_base")
vector_store = PropertyVectorStore()
query_engine = PropertyQueryEngine(vector_store)
orchestrator = PropertyOrchestrator(query_engine)

# Load knowledge base on startup
knowledge_base.load_knowledge_base()
for category, docs in knowledge_base.documents.items():
    if docs:
        vector_store.add_documents(docs, [category] * len(docs))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def query_property():
    data = request.json
    question = data.get('question', '')
    query_type = data.get('query_type', 'general')
    
    try:
        result = query_engine.query_with_context(question, query_type)
        
        # Format response as markdown
        markdown_response = f"""# Property Analysis Report

## Question
{question}

## Answer
{result['answer']}

## Sources
- {len(result.get('source_documents', []))} documents referenced
- Query type: {query_type}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return jsonify({
            'success': True,
            'markdown': markdown_response,
            'html': markdown.markdown(markdown_response),
            'raw_result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze', methods=['POST'])
def analyze_images():
    try:
        # Handle file uploads
        files = request.files.getlist('images')
        image_paths = []
        
        for file in files:
            if file.filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                image_paths.append(filepath)
        
        analysis_type = request.form.get('analysis_type', 'full')
        address = request.form.get('address', '')
        property_info = {'address': address} if address else None
        
        # Mock analysis for now (since CV models not available)
        result = {
            'summary': {
                'overall_condition': 'good',
                'estimated_value': 275000,
                'insurance_risk': 'low'
            },
            'recommendations': [
                'Regular roof maintenance recommended',
                'Consider updating electrical system',
                'Foundation appears stable'
            ]
        }
        
        # Format as markdown
        markdown_response = f"""# Property Analysis Report

## Property Information
- **Address**: {address or 'Not provided'}
- **Analysis Type**: {analysis_type}
- **Images Analyzed**: {len(image_paths)}
- **Report Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Overall Condition**: {result['summary']['overall_condition']}
- **Estimated Value**: ${result['summary']['estimated_value']:,}
- **Insurance Risk**: {result['summary']['insurance_risk']}

## Recommendations
"""
        for i, rec in enumerate(result['recommendations'], 1):
            markdown_response += f"{i}. {rec}\n"
        
        return jsonify({
            'success': True,
            'markdown': markdown_response,
            'html': markdown.markdown(markdown_response),
            'result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/final-report', methods=['POST'])
def generate_final_report():
    try:
        from reports.final_report_generator import FinalReportGenerator
        
        # Initialize report generator
        report_generator = FinalReportGenerator(query_engine, orchestrator)
        
        # Generate comprehensive report
        markdown_report = report_generator.generate_comprehensive_report()
        html_report = markdown.markdown(markdown_report)
        
        return jsonify({
            'success': True,
            'markdown': markdown_report,
            'html': html_report
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        markdown_content = data.get('markdown', '')
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Create full HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Property Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            try:
                pdfkit.from_string(full_html, tmp_file.name)
                return send_file(tmp_file.name, as_attachment=True, 
                               download_name=f'property_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
            except Exception as e:
                # Fallback: save as HTML if wkhtmltopdf not available
                html_file = tmp_file.name.replace('.pdf', '.html')
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                return send_file(html_file, as_attachment=True,
                               download_name=f'property_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)