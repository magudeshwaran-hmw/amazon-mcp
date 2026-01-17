import sys
import json

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        except Exception:
            break

        method = req.get("method")
        req_id = req.get("id")

        # 1️⃣ REQUIRED MCP HANDSHAKE
        if method == "initialize":
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "amazon-search",
                        "version": "1.0.0"
                    }
                }
            })

        # 2️⃣ REQUIRED
        elif method == "notifications/initialized":
            # Just acknowledge, no response needed usually, but good to handle
            pass

        # 3️⃣ REQUIRED
        elif method == "tools/list":
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "amazon_search",
                            "description": "Search Amazon products",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    ]
                }
            })

        # 4️⃣ REQUIRED
        elif method == "tools/call":
            tool = req.get("params", {}).get("name")
            args = req.get("params", {}).get("arguments", {})

            if tool == "amazon_search":
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Amazon search result for: {args.get('query')}"
                            }
                        ]
                    }
                })
            else:
                send({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                })

        # MCP expects a response to Pings
        elif method == "ping":
             send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            })
            
        # Fallback for unknown methods to keep connection alive if they expect response
        elif req_id is not None:
            # If it's a request (has id), we must respond
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            })

if __name__ == "__main__":
    main()
