def test_healthcheck_reachable(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
