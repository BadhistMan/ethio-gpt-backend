from flask import Blueprint, request, jsonify
from flask_limiter import limiter
from utils.hf_client import HFClient
import uuid
import os

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
        
        if len(topic) > 500:
            return jsonify({"error": "Topic too long. Maximum 500 characters."}), 400
        
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
def generate_resume():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('email'):
            return jsonify({"error": "Name and email are required fields"}), 400
        
        # Create simple HTML resume (no external CSS, no complex styling)
        html_content = create_simple_html_resume(data)
        
        # Generate a unique filename
        filename = f"resume_{data.get('name', 'unknown').replace(' ', '_')}.html"
        
        return jsonify({
            "success": True,
            "message": "Resume generated successfully",
            "html_content": html_content,
            "filename": filename,
            "instructions": "Download the HTML file and open it in your browser. Use Ctrl+P to print as PDF."
        })
        
    except Exception as e:
        return jsonify({"error": f"Resume generation failed: {str(e)}"}), 500

def create_simple_html_resume(data):
    """Create a simple HTML resume without external dependencies"""
    
    name = data.get('name', 'Your Name')
    email = data.get('email', '')
    phone = data.get('phone', '')
    location = data.get('location', '')
    summary = data.get('summary', '')
    experience = data.get('experience', '')
    education = data.get('education', '')
    skills = data.get('skills', '')
    
    # Simple HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Resume - {name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #078C03;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .name {{
                font-size: 28px;
                font-weight: bold;
                color: #1a202c;
                margin-bottom: 10px;
            }}
            .contact {{
                color: #666;
                margin-bottom: 5px;
            }}
            .section {{
                margin-top: 25px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                color: #078C03;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }}
            .skills {{
                margin-top: 5px;
            }}
            .skill {{
                display: inline-block;
                background: #078C03;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 13px;
                margin-right: 8px;
                margin-bottom: 8px;
            }}
            @media print {{
                body {{
                    margin: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{name}</div>
            <div class="contact">{email}</div>
            <div class="contact">{phone}</div>
            <div class="contact">{location}</div>
        </div>
        
        {f'<div class="section"><div class="section-title">Professional Summary</div><div>{summary}</div></div>' if summary else ''}
        
        {f'<div class="section"><div class="section-title">Work Experience</div><div>{experience.replace(chr(10), "<br>")}</div></div>' if experience else ''}
        
        {f'<div class="section"><div class="section-title">Education</div><div>{education.replace(chr(10), "<br>")}</div></div>' if education else ''}
        
        {f'<div class="section"><div class="section-title">Skills</div><div class="skills">{"".join([f"<span class=\"skill\">{skill.strip()}</span>" for skill in skills.split(",") if skill.strip()])}</div></div>' if skills else ''}
        
        <div style="margin-top: 40px; text-align: center; color: #666; font-size: 12px;">
            Generated with Ethio GPT Tools
        </div>
    </body>
    </html>
    """
    
    return html
