from app.integrations.mojang_client import MinecraftProfile
from app.main import create_app


class FakeMojangClient:
    def __init__(self):
        self.profiles = {
            "someseller": MinecraftProfile(
                uuid="11111111111111111111111111111111",
                username="SomeSeller",
            ),
            "newseller": MinecraftProfile(
                uuid="22222222222222222222222222222222",
                username="NewSeller",
            ),
            "oldname": MinecraftProfile(
                uuid="33333333333333333333333333333333",
                username="OldName",
            ),
            "newname": MinecraftProfile(
                uuid="33333333333333333333333333333333",
                username="NewName",
            ),
            "notch": MinecraftProfile(
                uuid="069a79f444e94726a5befca90e38aaf5",
                username="Notch",
            ),
        }

    def lookup_profile(self, username: str) -> MinecraftProfile | None:
        return self.profiles.get(username.lower())


def make_app(tmp_path):
    return create_app(tmp_path / "test.db", mojang_client=FakeMojangClient())


def test_rating_flow(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        create_response = client.post(
            "/rating/SomeSeller",
            json={
                "outcome": "LEGIT",
                "tradeCategory": "SPAWNER",
                "tradeDescription": "Blaze spawner",
                "quantity": 2,
                "price": 5000000,
                "currency": "DOLLARS",
                "reviewText": "Seller delivered after payment.",
                "evidenceUrl": "https://example.com/screenshot.png",
                "reporterUsername": "Mark",
            },
        )

        assert create_response.status_code == 201
        created = create_response.json()
        assert created["sellerUsername"] == "SomeSeller"
        assert created["outcome"] == "LEGIT"
        assert created["tradeCategory"] == "SPAWNER"
        assert created["tradeDescription"] == "Blaze spawner"
        assert created["reviewText"] == "Seller delivered after payment."

        list_response = client.get("/rating/someseller")
        assert list_response.status_code == 200
        ratings = list_response.json()
        assert ratings["sellerUsername"] == "SomeSeller"
        assert len(ratings["ratings"]) == 1

        summary_response = client.get("/rating/SomeSeller/summary")
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert summary["totalRatings"] == 1
        assert summary["legitCount"] == 1
        assert summary["scammerCount"] == 0
        assert summary["mixedCount"] == 0
        assert summary["legitPercentage"] == 100
        assert summary["reputation"] == "LEGIT"

        recent_response = client.get("/rating/recent")
        assert recent_response.status_code == 200
        recent = recent_response.json()
        assert len(recent) == 1
        assert recent[0]["sellerUsername"] == "SomeSeller"

        stats_response = client.get("/rating/stats")
        assert stats_response.status_code == 200
        assert stats_response.json() == {"totalRatings": 1}


def test_empty_seller_returns_empty_rating_list_and_no_data_summary(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        list_response = client.get("/rating/NewSeller")
        assert list_response.status_code == 200
        assert list_response.json() == {"sellerUsername": "NewSeller", "ratings": []}

        summary_response = client.get("/rating/NewSeller/summary")
        assert summary_response.status_code == 200
        assert summary_response.json() == {
            "sellerUsername": "NewSeller",
            "totalRatings": 0,
            "legitCount": 0,
            "scammerCount": 0,
            "mixedCount": 0,
            "legitPercentage": 0,
            "reputation": "NO_DATA",
        }

        stats_response = client.get("/rating/stats")
        assert stats_response.status_code == 200
        assert stats_response.json() == {"totalRatings": 0}


def test_invalid_username_returns_400(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        response = client.get("/rating/x")

    assert response.status_code == 400
    assert response.json() == {
        "error": "Seller username must be 3-16 letters, numbers, or underscores."
    }


def test_ratings_follow_mojang_uuid_when_username_changes(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        create_response = client.post(
            "/rating/OldName",
            json={
                "outcome": "SCAMMER",
                "tradeCategory": "OTHER",
                "tradeDescription": "Item trade",
                "reviewText": "Seller kept the item and did not pay.",
            },
        )
        assert create_response.status_code == 201
        assert create_response.json()["sellerUsername"] == "OldName"

        list_response = client.get("/rating/NewName")
        assert list_response.status_code == 200
        body = list_response.json()
        assert body["sellerUsername"] == "NewName"
        assert len(body["ratings"]) == 1
        assert body["ratings"][0]["outcome"] == "SCAMMER"


def test_avatar_route_redirects_to_mineatar(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        response = client.get("/avatar/Notch", follow_redirects=False)

    assert response.status_code == 307
    assert (
        response.headers["location"]
        == "https://api.mineatar.io/face/069a79f444e94726a5befca90e38aaf5?scale=32"
    )


def test_rating_rate_limit_is_enforced(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        payload = {
            "outcome": "LEGIT",
            "tradeCategory": "GEAR",
            "tradeDescription": "Diamond set",
            "reviewText": "Seller delivered the items after payment.",
        }
        first_response = client.post("/rating/SomeSeller", json=payload)
        second_response = client.post("/rating/SomeSeller", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 429


def test_visit_counter_increments_and_reads_back(tmp_path):
    app = make_app(tmp_path)
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        first_response = client.post("/logging/visit")
        second_response = client.post("/logging/visit")
        read_response = client.get("/logging/visits")

    assert first_response.status_code == 200
    assert first_response.json() == {"visits": 1}
    assert second_response.status_code == 200
    assert second_response.json() == {"visits": 2}
    assert read_response.status_code == 200
    assert read_response.json() == {"visits": 2}
