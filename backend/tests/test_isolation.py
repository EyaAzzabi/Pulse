from tests.conftest import register_and_login


def test_cannot_access_other_organization_summary(client):
    headers_a, org_a = register_and_login(client, "org-a-owner@example.com", org_name="Org A")
    headers_b, org_b = register_and_login(client, "org-b-owner@example.com", org_name="Org B")

    resp = client.get(f"/financial/summary?organization_id={org_b}", headers=headers_a)
    assert resp.status_code == 403

    resp_ok = client.get(f"/financial/summary?organization_id={org_a}", headers=headers_a)
    assert resp_ok.status_code == 200


def test_cannot_list_members_of_other_organization(client):
    headers_a, org_a = register_and_login(client, "iso-a@example.com", org_name="Iso A")
    _, org_b = register_and_login(client, "iso-b@example.com", org_name="Iso B")

    resp = client.get(f"/organizations/{org_b}/members", headers=headers_a)
    assert resp.status_code == 403
