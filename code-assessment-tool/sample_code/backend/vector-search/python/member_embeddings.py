import requests


def upsert_member_embedding(vector_client, member_profile: dict):
    protected_payload = requests.post(
        "https://ciphertrust.example.com/v1/protect/vector-member",
        json={
            "memberId": member_profile["memberId"],
            "email": member_profile["email"],
            "phoneNumber": member_profile["phoneNumber"],
            "dateOfBirth": member_profile["dateOfBirth"],
            "diagnosis": member_profile["diagnosis"],
        },
        timeout=10,
    ).json()

    document = {
        "id": member_profile["memberId"],
        "text": f"Member email {protected_payload['protectedEmail']} diagnosis {protected_payload['protectedDiagnosis']}",
        "metadata": {
            "email": protected_payload["protectedEmail"],
            "phoneNumber": protected_payload["protectedPhoneNumber"],
            "dateOfBirth": protected_payload["protectedDateOfBirth"],
            "diagnosis": protected_payload["protectedDiagnosis"],
        },
    }

    vector_client.upsert("member-embeddings", [document])
