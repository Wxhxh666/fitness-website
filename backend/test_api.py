import sys
sys.path.insert(0, "E:/Codex_Project/test3/fitness-website/backend")
from app import app

client = app.test_client()

results = []

def test(method, path, body=None, expected=200):
    if method == "GET":
        resp = client.get(path)
    elif method == "POST":
        resp = client.post(path, json=body or {})
    elif method == "PUT":
        resp = client.put(path, json=body or {})
    data = resp.get_json()
    ok = resp.status_code == expected
    results.append((ok, method, path, resp.status_code, data))
    return data

print("=== FITLUXE API Test ===\n")

test("GET", "/api/health")
test("GET", "/api/exercises/categories")
test("GET", "/api/exercises")
test("GET", "/api/exercises?category=chest")
test("GET", "/api/exercises/1")
test("GET", "/api/plans/goals")
test("GET", "/api/plans")
test("GET", "/api/plans?goal=muscle")
test("GET", "/api/plans/1")
test("GET", "/api/body-metrics")
test("POST", "/api/body-metrics/bmi", {"height_cm": 175, "weight_kg": 72.5})
test("GET", "/api/body-metrics/measurements")
test("PUT", "/api/body-metrics/measurements/5", {"value": 80.0})
test("GET", "/api/site/contact-info")
test("POST", "/api/contact", {"name": "测试", "email": "test@test.com", "subject": "course", "message": "测试留言"})

print(f"Total: {len(results)}, Passed: {sum(1 for r in results if r[0])}, Failed: {sum(1 for r in results if not r[0])}\n")

for ok, method, path, status, data in results:
    code = data.get("code", -1) if data else -1
    label = "PASS" if ok else "FAIL"
    detail = ""
    if ok and data and "data" in data:
        d = data["data"]
        if isinstance(d, list):
            detail = f" ({len(d)} items)"
        elif isinstance(d, dict):
            if "items" in d:
                detail = f" ({len(d['items'])} items, total={d['total']})"
            elif "name" in d:
                detail = f" - {d.get('name', '')}"
            elif "bmi" in d:
                detail = f" - bmi={d['bmi']}"
    print(f"  [{label}] {method} {path} -> {status} (code={code}){detail}")

print("\n=== All tests done ===")
