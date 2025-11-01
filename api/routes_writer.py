from flask import Blueprint, request, jsonify
from flask_limiter import limiter
from utils.hf_client import HFClient
import os
import uuid

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
        
        # Create professional HTML resume
        html_content = create_html_resume(data)
        
        # Generate a unique filename
        filename = f"resume_{data.get('name', 'unknown').replace(' ', '_')}_{uuid.uuid4().hex[:8]}.html"
        
        return jsonify({
            "success": True,
            "message": "Resume generated successfully. Download the HTML file and use your browser's print function to save as PDF.",
            "resume_data": {
                "name": data.get('name', ''),
                "email": data.get('email', ''),
                "phone": data.get('phone', ''),
                "location": data.get('location', ''),
                "summary": data.get('summary', ''),
                "experience": data.get('experience', ''),
                "education": data.get('education', ''),
                "skills": data.get('skills', ''),
                "html_content": html_content
            },
            "filename": filename,
            "instructions": {
                "step1": "Download the HTML file",
                "step2": "Open it in your web browser",
                "step3": "Press Ctrl+P (or Cmd+P on Mac) to print",
                "step4": "Choose 'Save as PDF' as your destination",
                "step5": "Click 'Save' to download your PDF resume"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Resume generation failed: {str(e)}"}), 500

def create_html_resume(data):
    """Create a professional HTML resume"""
    
    # Process skills into list
    skills_list = []
    if data.get('skills'):
        skills_list = [skill.strip() for skill in data.get('skills', '').split(',') if skill.strip()]
    
    # Process experience with bullet points
    experience_html = ""
    if data.get('experience'):
        experience_lines = data.get('experience', '').split('\n')
        for line in experience_lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                experience_html += f'<li>{line[1:].strip()}</li>'
            elif line:
                experience_html += f'<li>{line}</li>'
    
    # Process education with bullet points
    education_html = ""
    if data.get('education'):
        education_lines = data.get('education', '').split('\n')
        for line in education_lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                education_html += f'<li>{line[1:].strip()}</li>'
            elif line:
                education_html += f'<li>{line}</li>'
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume - {data.get('name', 'Your Name')}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                color: #333;
                background: #fff;
                padding: 40px 20px;
            }}
            
            .resume-container {{
                max-width: 210mm;
                min-height: 297mm;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                padding: 40px;
            }}
            
            .header {{
                text-align: center;
                border-bottom: 3px solid #078C03;
                padding-bottom: 25px;
                margin-bottom: 30px;
            }}
            
            .name {{
                font-size: 32px;
                font-weight: 700;
                color: #1a202c;
                margin-bottom: 10px;
            }}
            
            .contact-info {{
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 20px;
                font-size: 14px;
                color: #4a5568;
            }}
            
            .contact-item {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            
            .section {{
                margin-bottom: 25px;
            }}
            
            .section-title {{
                font-size: 18px;
                font-weight: 600;
                color: #078C03;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 8px;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .summary {{
                font-size: 14px;
                line-height: 1.7;
                color: #4a5568;
            }}
            
            .experience-item, .education-item {{
                margin-bottom: 15px;
            }}
            
            .item-title {{
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 5px;
            }}
            
            .item-date {{
                font-style: italic;
                color: #718096;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            
            .item-description {{
                font-size: 14px;
                color: #4a5568;
                margin-left: 15px;
            }}
            
            .item-description ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            
            .item-description li {{
                position: relative;
                padding-left: 15px;
                margin-bottom: 4px;
            }}
            
            .item-description li:before {{
                content: "•";
                color: #078C03;
                font-weight: bold;
                position: absolute;
                left: 0;
            }}
            
            .skills-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            
            .skill-tag {{
                background: #078C03;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
            }}
            
            @media print {{
                body {{
                    padding: 0;
                    background: white;
                }}
                
                .resume-container {{
                    box-shadow: none;
                    padding: 20px;
                    max-width: 100%;
                    min-height: auto;
                }}
                
                .header {{
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                
                .name {{
                    font-size: 28px;
                }}
                
                .section {{
                    margin-bottom: 20px;
                    page-break-inside: avoid;
                }}
            }}
            
            @media (max-width: 768px) {{
                .resume-container {{
                    padding: 20px;
                }}
                
                .contact-info {{
                    flex-direction: column;
                    align-items: center;
                    gap: 10px;
                }}
                
                .name {{
                    font-size: 24px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="resume-container">
            <!-- Header Section -->
            <div class="header">
                <h1 class="name">{data.get('name', 'Your Name')}</h1>
                <div class="contact-info">
                    {f'<div class="contact-item">📧 {data.get("email", "")}</div>' if data.get('email') else ''}
                    {f'<div class="contact-item">📞 {data.get("phone", "")}</div>' if data.get('phone') else ''}
                    {f'<div class="contact-item">📍 {data.get("location", "")}</div>' if data.get('location') else ''}
                </div>
            </div>
            
            <!-- Professional Summary -->
            {f'''
            <div class="section">
                <h2 class="section-title">Professional Summary</h2>
                <p class="summary">{data.get('summary', '')}</p>
            </div>
            ''' if data.get('summary') else ''}
            
            <!-- Work Experience -->
            {f'''
            <div class="section">
                <h2 class="section-title">Work Experience</h2>
                <div class="experience-item">
                    <div class="item-description">
                        <ul>
                            {experience_html}
                        </ul>
                    </div>
                </div>
            </div>
            ''' if data.get('experience') else ''}
            
            <!-- Education -->
            {f'''
            <div class="section">
                <h2 class="section-title">Education</h2>
                <div class="education-item">
                    <div class="item-description">
                        <ul>
                            {education_html}
                        </ul>
                    </div>
                </div>
            </div>
            ''' if data.get('education') else ''}
            
            <!-- Skills -->
            {f'''
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills-container">
                    {''.join([f'<span class="skill-tag">{skill}</span>' for skill in skills_list])}
                </div>
            </div>
            ''' if skills_list else ''}
            
            <!-- Footer Note -->
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #718096;">
                <p>Generated with Ethio GPT Tools - Free AI Resume Builder</p>
            </div>
        </div>
        
        <script>
            // Auto-print when opened (optional)
            // window.onload = function() {{
            //     window.print();
            // }};
        </script>
    </body>
    </html>
    """
    
    return html_template

@writer_bp.route('/health/writer', methods=['GET'])
def health_check():
    """Health check endpoint for writer service"""
    return jsonify({
        "status": "healthy",
        "service": "Resume Writer",
        "endpoints": {
            "POST /api/write": "Generate AI content",
            "POST /api/generate_resume": "Generate HTML resume",
            "GET /api/health/writer": "Health check"
        }
    })
