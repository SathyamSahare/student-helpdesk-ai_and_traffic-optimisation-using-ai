from fastapi.testclient import TestClient
from api import app
c = TestClient(app)

def test_health():
    assert c.get("/health").json()["status"] == "ok"

def test_known_intent():
    assert c.post("/chat", json={"message": "how can I pay my fees online"}).json()["intent"] == "fee_payment"

def test_out_of_scope_falls_back():
    r = c.post("/chat", json={"message": "tell me a joke"}).json()
    assert r["intent"] is None and "Sorry" in r["answer"]

def test_empty_message():
    assert c.post("/chat", json={"message": "  "}).json()["intent"] is None
