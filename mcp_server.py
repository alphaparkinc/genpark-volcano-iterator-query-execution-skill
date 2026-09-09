import sys
import json
from client import SeqScanOperator, HashJoinOperator, SortAggregateOperator

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    if method == "execute_pipeline":
        left = SeqScanOperator(params.get("left", []))
        right = SeqScanOperator(params.get("right", []))
        join = HashJoinOperator(left, right, params.get("lk", "id"), params.get("rk", "id"))
        join.open()
        res = []
        while True:
            r = join.next()
            if r is None:
                break
            res.append(r)
        join.close()
        return {"results": res}
    return {"error": "Unknown method"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        res = handle_request(req)
        print(json.dumps(res))
        sys.stdout.flush()

if __name__ == '__main__':
    main()
