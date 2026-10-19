"""Local HTTP relay with an on-disk chunk cache: serves /<driveId> with Range support, fetching
aligned 8 MB chunks from Drive via curl (which knows the session proxy) only when ffmpeg reads them.
Each chunk is fetched once, to stay inside Drive's anonymous download quota."""
import http.server, socketserver, subprocess, sys, re, time, os, threading
U = 'https://drive.usercontent.google.com/download?export=download&confirm=t&id='
CACHE = sys.argv[2]; os.makedirs(CACHE, exist_ok=True)
CH = 8 * 1024 * 1024
SIZES = {  # bytes, from Drive metadata
'16cUKxEfhmHfjwMnMkoGk0Vua9yARSxZ1': 3266769084, '1KM5iucB5wbTGWCC3DDYGlwUaXsi4SjS7': 3126960316,
         '1yZgHVlulT88qSVTklsz-E6dQYJJQnAH8': 3943237940, '1aNlVECq42vY_F9XUuMJeThcaDqXc5eER': 311198600,
         '1Dz-Wf1PATRof-zafw7JmSJKgJcLJm3oV': 622397096}
LOCK = threading.Lock(); LOG = open(os.path.join(CACHE, 'fetch.log'), 'a')
def chunk(fid, i):
    p = os.path.join(CACHE, f'{fid}.{i}')
    if os.path.exists(p): return open(p, 'rb').read()
    a = i * CH; b = min(SIZES[fid], a + CH) - 1
    for attempt in range(6):
        data = subprocess.run(['curl', '-sS', '-L', '--max-time', '180', '-r', f'{a}-{b}', U + fid], capture_output=True).stdout
        if len(data) == b - a + 1:
            open(p + '.tmp', 'wb').write(data); os.replace(p + '.tmp', p)
            LOG.write(f'{time.time():.0f} ok {fid} {i}\n'); LOG.flush(); return data
        LOG.write(f'{time.time():.0f} bad {fid} {i} got {len(data)}\n'); LOG.flush()
        time.sleep(2 + 2 * attempt)
    raise ConnectionResetError('drive refused ' + fid)
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *a): pass
    def do_HEAD(self): self.go(False)
    def do_GET(self): self.go(True)
    def go(self, body):
        fid = self.path.strip('/').split('.')[0]; n = SIZES[fid]
        rng = self.headers.get('Range'); a, b = 0, n - 1
        if rng:
            m = re.match(r'bytes=(\d*)-(\d*)', rng); a = int(m.group(1) or 0); b = int(m.group(2)) if m.group(2) else n - 1
        b = min(b, n - 1)
        self.send_response(206 if rng else 200)
        self.send_header('Content-Type', 'application/octet-stream'); self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(b - a + 1))
        if rng: self.send_header('Content-Range', f'bytes {a}-{b}/{n}')
        self.end_headers()
        if not body: return
        pos = a
        try:
            while pos <= b:
                i = pos // CH; data = chunk(fid, i)
                off = pos - i * CH; part = data[off: off + (b - pos + 1)]
                self.wfile.write(part); self.wfile.flush(); pos += len(part)
        except (BrokenPipeError, ConnectionResetError):
            pass
class S(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads = True
S(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
