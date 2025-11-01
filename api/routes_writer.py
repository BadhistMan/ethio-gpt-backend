from flask import Blueprint, request, jsonify
from flask_limiter import limiter
from utils.hf_client import HFClient
from xhtml2pdf import pisa
from io import BytesIO

writer_bp = Blueprint('writer', __name__)
hf_client = HFClient()

@writer_bp.route('/write', methods=['POST'])
@limiter.limit("20 per hour")
def generate_content():
    try:
        data = request.get_json()
        content_type = data.get('type', 'blog')
        topic = data.get('topic', '').strip()
        length = data.get('length', 'medium')
        tone = data.get('tone', 'professional')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Create enhanced prompt based on type
        prompts = {
            'blog': f"Write a {tone} blog post about: {topic}. Length: {length}",
            'resume': f"Write a {tone} professional resume summary for: {topic}",
            'cover_letter': f"Write a {tone} cover letter for: {topic}",
            'social': f"Write a {tone} social media post about: {topic}. Length: {length}"
        }
        
        prompt = prompts.get(content_type, f"Write about: {topic}")
        
        # Generate content
        content = hf_client.chat_completion(prompt)
        
        return jsonify({
            "content": content,
            "type": content_type,
            "topic": topic,
            "length": length,
            "tone": tone
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@writer_bp.route('/generate_resume', methods=['POST'])
def generate_resume_pdf():
    try:
        data = request.get_json()
        
        # Create HTML resume
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
                .name {{ font-size: 28px; font-weight: bold; color: #2c5aa0; }}
                .contact {{ margin-top: 10px; font-size: 14px; color: #666; }}
                .section {{ margin-top: 25px; }}
                .section-title {{ font-size: 18px; font-weight: bold; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 10px; color: #2c5aa0; }}
                .experience-item {{ margin-bottom: 15px; }}
                .date {{ color: #666; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="name">{data.get('name', 'Your Name')}</div>
                <div class="contact">
                    {data.get('email', '')} | {data.get('phone', '')} | {data.get('location', '')}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Professional Summary</div>
                <p>{data.get('summary', 'Experienced professional seeking new opportunities.')}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Work Experience</div>
                <div class="experience-item">{data.get('experience', 'Add your work experience here.')}</div>
            </div>
            
            <div class="section">
                <div class="section-title">Education</div>
                <div class="experience-item">{data.get('education', 'Add your education background here.')}</div>
            </div>
            
            <div class="section">
                <div class="section-title">Skills</div>
                <p>{data.get('skills', 'Add your skills here.')}</p>
            </div>
        </body>
        </html>
        """
        
        # Create PDF
        pdf = BytesIO()
        pisa.CreatePDF(html_content, dest=pdf)
        
        pdf_data = pdf.getvalue()
        filename = f"resume_{data.get('name', 'unknown').replace(' ', '_')}.pdf"
        
        return jsonify({
            "pdf_data": pdf_data.hex(),
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500
