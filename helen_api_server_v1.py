"""
HELEN OS Web API Server v1.0

RESTful API interface for HELEN multi-model system.
Run with: python helen_api_server_v1.py
Access at: http://localhost:8000

Endpoints:
  GET  /                    - API info
  GET  /health              - Health check
  GET  /models              - List available models
  POST /query               - Query with auto-routing
  POST /query/<model>       - Query specific model
  GET  /status              - System status
  GET  /stats               - Usage statistics
  POST /avatar/<name>       - Switch avatar
"""

from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict
import json
import logging
from functools import wraps
from pathlib import Path

from helen_unified_interface_v1 import HELENMultiModel
from helen_multimodel_dispatcher_v1 import TaskType, TaskContext
from helen_test_avatar_v1 import AvatarRegistry
from helen_os.api.do_next_v1 import DoNextService
from helen_os.executor.bounded_executor_v1 import BoundedExecutor

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global HELEN instance
helen: Optional[HELENMultiModel] = None
current_avatar = "helen"
do_next_service = DoNextService(storage_dir=Path(__file__).resolve().parent / "storage" / "do_next_sessions")
_SANDBOX_DIR = Path(__file__).resolve().parent / "storage" / "action_sandbox"
action_executor = BoundedExecutor(
    base_dir=_SANDBOX_DIR,
    policy_version="STAGE_B1_V1",
    registry_path=_SANDBOX_DIR / "_execution_registry.ndjson",
)
action_executor.base_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize():
    """Initialize HELEN OS on startup"""
    global helen
    try:
        helen = HELENMultiModel()
        logger.info("✅ HELEN OS initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize HELEN OS: {e}")
        return False

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "message": str(error)}), 500

# ============================================================================
# DECORATORS
# ============================================================================

def require_helen(f):
    """Decorator to check if HELEN is initialized"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if helen is None:
            return jsonify({"error": "HELEN OS not initialized"}), 503
        return f(*args, **kwargs)
    return decorated

# ============================================================================
# ROUTES: Information
# ============================================================================

@app.route('/', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        "name": "HELEN OS Multi-Model API",
        "version": "1.0",
        "status": "operational",
        "description": "Intelligent AI assistant with multi-model routing",
        "endpoints": {
            "GET /health": "Health check",
            "GET /models": "List available models",
            "POST /query": "Query with auto-routing",
            "POST /query/<model>": "Query specific model",
            "GET /status": "System status",
            "GET /stats": "Usage statistics",
            "POST /avatar/<name>": "Switch avatar",
            "POST /do_next": "Constitutional /do_next boundary",
            "POST /actions/execute": "Execute bounded action (WRITE|EDIT|ANALYZE|ROUTE)",
            "GET /avatars": "List avatars",
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "helen_initialized": helen is not None,
    })

# ============================================================================
# ROUTES: Models & Configuration
# ============================================================================

@app.route('/models', methods=['GET'])
@require_helen
def get_models():
    """List all available models"""
    models = helen.list_available_models()
    return jsonify({
        "models": models,
        "count": len(models),
    })

@app.route('/avatars', methods=['GET'])
def get_avatars():
    """List available avatars"""
    avatars = AvatarRegistry.list_avatars()
    return jsonify({
        "avatars": avatars,
        "current": current_avatar,
        "count": len(avatars),
    })

@app.route('/avatar/<name>', methods=['POST'])
def switch_avatar(name: str):
    """Switch to a different avatar"""
    global current_avatar

    if name.lower() not in AvatarRegistry.AVATARS:
        return jsonify({
            "error": f"Unknown avatar: {name}",
            "available": list(AvatarRegistry.AVATARS.keys()),
        }), 404

    avatar = AvatarRegistry.get_avatar(name)
    current_avatar = name

    return jsonify({
        "avatar": current_avatar,
        "name": avatar.name,
        "emoji": avatar.emoji,
        "greeting": avatar.greeting,
    })

# ============================================================================
# ROUTES: Querying
# ============================================================================

@app.route('/query', methods=['POST'])
@require_helen
def query_auto():
    """Query with automatic model selection"""
    data = request.get_json()

    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    prompt = data['prompt']
    task_type_str = data.get('task_type', 'CONVERSATION').upper()
    stream = data.get('stream', False)

    try:
        task_type = TaskType[task_type_str]
    except KeyError:
        return jsonify({
            "error": f"Invalid task type: {task_type_str}",
            "valid_types": [t.name for t in TaskType]
        }), 400

    try:
        # Get routing decision
        decision = helen.get_routing_decision(task_type)

        # Generate response (in test mode, this uses mock)
        response = helen.query(
            prompt,
            task_type=task_type,
            stream=stream,
        )

        lineage = {
            "name": decision.model_config.name,
            "provider": decision.model_config.provider.value,
            "capability": decision.model_config.capability_tier.value,
        }
        routing = {
            "reason": decision.reason,
            "confidence": decision.confidence,
        }

        if not response or not response.strip():
            return jsonify({
                "success": False,
                "failure_code": "empty_inference_response",
                "task_type": task_type.value,
                "model": lineage,
                "routing": routing,
                "avatar": current_avatar,
                "timestamp": datetime.now().isoformat(),
            }), 503

        return jsonify({
            "success": True,
            "prompt": prompt,
            "task_type": task_type.value,
            "model": lineage,
            "routing": routing,
            "response": response,
            "avatar": current_avatar,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/do_next', methods=['POST'])
def do_next():
    """Constitutional /do_next boundary"""
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400
    status, out = do_next_service.handle_http(data)
    return jsonify(out), status

@app.route('/actions/execute', methods=['POST'])
def execute_action():
    """Execute bounded actions (WRITE|EDIT|ANALYZE|ROUTE) in sandbox"""
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    decision, result, artifact = action_executor.execute(data)

    status_code = 200
    if result.status == "FAILURE":
        status_code = 409 if result.failure_code == "duplicate_execution" else 400

    return jsonify({
        "success": result.status == "SUCCESS",
        "avatar": current_avatar,
        "sandbox_dir": str(action_executor.base_dir),
        "decision": asdict(decision),
        "result": asdict(result),
        "artifact": asdict(artifact) if artifact else None,
    }), status_code

@app.route('/query/<model>', methods=['POST'])
@require_helen
def query_specific(model: str):
    """Query specific model"""
    data = request.get_json()

    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    prompt = data['prompt']

    try:
        # For testing, we'll use the auto-routing but note the requested model
        response = helen.query(prompt)

        return jsonify({
            "success": True,
            "prompt": prompt,
            "requested_model": model,
            "response": response,
            "avatar": current_avatar,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ROUTES: Status & Analytics
# ============================================================================

@app.route('/status', methods=['GET'])
@require_helen
def get_status():
    """System status"""
    status = helen.get_status()

    return jsonify({
        "system": "operational",
        "helen_os": status,
        "avatar": current_avatar,
        "timestamp": datetime.now().isoformat(),
    })

@app.route('/stats', methods=['GET'])
@require_helen
def get_stats():
    """Usage statistics"""
    stats = helen.get_stats()

    return jsonify({
        "statistics": stats,
        "timestamp": datetime.now().isoformat(),
    })

# ============================================================================
# ROUTES: Task Types Reference
# ============================================================================

@app.route('/task-types', methods=['GET'])
def get_task_types():
    """List available task types"""
    task_types = {
        t.name.lower(): t.value for t in TaskType
    }

    routing_map = {
        "reasoning": "Claude, GPT, Grok",
        "coding": "Claude, GPT, Grok",
        "math": "GPT, Claude, Grok",
        "analysis": "Claude, GPT, Grok",
        "creative": "Claude, Grok, Qwen",
        "vision": "Gemini, GPT, Claude",
        "conversation": "Ollama, Claude, GPT",
        "research": "Claude, GPT, Grok",
        "factual": "Claude, GPT, Gemini",
    }

    return jsonify({
        "task_types": task_types,
        "routing_map": routing_map,
    })

# ============================================================================
# ROUTES: Health & Version
# ============================================================================

@app.route('/version', methods=['GET'])
def get_version():
    """API version information"""
    return jsonify({
        "api_version": "1.0",
        "helen_version": "1.0",
        "python_version": "3.10+",
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize HELEN
    if not initialize():
        logger.error("Failed to initialize HELEN OS")
        exit(1)

    # Start Flask server
    print("\n" + "="*70)
    print("🧠 HELEN OS Web API Server")
    print("="*70)
    print("\n📍 API Endpoint: http://localhost:8000")
    print("\n📚 Documentation: http://localhost:8000")
    print("\n🔌 Available endpoints:")
    print("   • GET  /health           - Health check")
    print("   • GET  /models           - List models")
    print("   • GET  /avatars          - List avatars")
    print("   • POST /query            - Query (auto-routing)")
    print("   • POST /query/<model>    - Query (specific model)")
    print("   • GET  /status           - System status")
    print("   • GET  /stats            - Usage statistics")
    print("   • POST /avatar/<name>    - Switch avatar")
    print("   • POST /actions/execute  - Execute bounded action")
    print("\n💡 Example request:")
    print('   curl -X POST http://localhost:8000/query \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"prompt": "What is Python?", "task_type": "EXPLANATION"}\'')
    print("\n" + "="*70 + "\n")

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True,
    )
