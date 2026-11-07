"""Versioned engine evidence for the three fixed history entries."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent / 'data' / 'history'
VERSION = 1

def fingerprint(pgn):
    return hashlib.sha256(pgn.encode('utf-8')).hexdigest()

def load(name, pgn, depth, seconds):
    try:
        payload = json.loads((ROOT / f'{name}.json').read_text(encoding='utf-8'))
        if (payload['version'] != VERSION or payload['pgn_sha256'] != fingerprint(pgn)
                or payload['depth'] != depth or payload['seconds'] != seconds):
            return None
        report = payload['report']
        if not report.get('engine') or not report.get('generated_at') or not report.get('rows'):
            return None
        report['preloaded'] = True
        return report
    except (OSError, ValueError, KeyError, TypeError):
        return None

def save(name, pgn, depth, seconds, report):
    ROOT.mkdir(parents=True, exist_ok=True)
    target = ROOT / f'{name}.json'
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(dict(version=VERSION, pgn_sha256=fingerprint(pgn),
        depth=depth, seconds=seconds, report=report), ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(target)
