from flask import Flask, request, render_template, jsonify, Response
import pickle, json, queue
import socket

app = Flask(__name__)
# in‑memory overrides: { url: 0|1 }
overrides = {}
# a list of queues—one per connected client
clients = []
# Load model pipeline
with open('./model/model_pipeline.pkl', 'rb') as f:
    pipeline = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data      = request.get_json(force=True)
        browser   = data.get('browser', 'unknown')
        url_input = data.get('url', '')
        client_ip = request.remote_addr
        # 1) check manual override first
        prefix = next((u for u in overrides if url_input.startswith(u)), None)
        if prefix is not None:
            prediction = overrides[url_input]
            source = 'override'
        else:
            model_pred = pipeline.predict([url_input])[0]
            prediction = 1 if model_pred else 0
            source = 'model'
        hostname = socket.gethostname()
        server_ip = socket.gethostbyname(hostname)
        print(server_ip)
        result = {
            'browser':    browser,
            'input_url':  url_input,
            'prediction': prediction,
            'source':     source,
            'client_ip' : client_ip
        }
        # push to SSE clients
        for q in clients:
            q.put_nowait(result)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        #write to .txt logic
        return jsonify({'error': str(e)}), 500

@app.route('/override', methods=['POST'])
def override():
    """
    Receive {"url": "...", "status": 0|1} from the UI
    and update overrides dict.
    """
    data   = request.get_json(force=True)
    url    = data.get('url', '').strip()
    status = data.get('status')

    if not url or status not in (0,1):
        return jsonify({'error':'Invalid payload'}), 400

    overrides[url] = status
    # notify all clients that an override was added/changed
    payload = {'override_url': url, 'override_status': status}
    for q in clients:
        q.put_nowait(payload)

    return jsonify({'ok': True, 'overrides': overrides})

@app.route('/stream')
def stream():
    def event_stream(q):
        while True:
            data = q.get()
            yield f"data: {json.dumps(data)}\n\n"
    q = queue.Queue()
    clients.append(q)
    return Response(event_stream(q), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
