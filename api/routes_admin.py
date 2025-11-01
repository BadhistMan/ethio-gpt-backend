from flask import Blueprint, request, jsonify
import os

admin_bp = Blueprint('admin', __name__)

# Simple admin authentication
ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'admin-secret-change-me')

def require_admin_secret(func):
    def wrapper(*args, **kwargs):
        secret = request.headers.get('X-Admin-Secret') or request.args.get('admin_secret')
        if secret != ADMIN_SECRET:
            return jsonify({"error": "Admin access denied"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/admin/stats')
@require_admin_secret
def get_stats():
    try:
        # Basic stats
        stats = {
            "total_users": len(users_db),
            "total_requests": sum(user.get('usage_count', 0) for user in users_db.values()),
            "active_tools": ["chat", "image", "translator", "tts", "writer"],
            "system_status": "healthy"
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/admin/tools/<tool_name>', methods=['POST'])
@require_admin_secret
def toggle_tool(tool_name):
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        return jsonify({
            "tool": tool_name,
            "enabled": enabled,
            "message": f"Tool {tool_name} {'enabled' if enabled else 'disabled'}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
