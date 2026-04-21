from fastapi import FastAPI
import requests
import psycopg2

app = FastAPI()


@app.post("/api/member/protect")
def protect_member(payload: dict):
    member_id = payload.get("memberId")
    email = payload.get("email")
    phone_number = payload.get("phoneNumber")
    date_of_birth = payload.get("dateOfBirth")
    passport = payload.get("passport")
    diagnosis = payload.get("diagnosis")

    protected_payload = requests.post(
        "https://ciphertrust.example.com/v1/protect/member",
        json={
            "email": email,
            "phoneNumber": phone_number,
            "dateOfBirth": date_of_birth,
            "passport": passport,
            "diagnosis": diagnosis,
        },
        timeout=10,
    ).json()

    connection = psycopg2.connect("dbname=memberdb user=memberapp password=memberpass")
    cursor = connection.cursor()
    cursor.execute(
        """
        update member_profile
        set email = %s,
            phone_number = %s,
            date_of_birth = %s,
            passport = %s,
            diagnosis = %s
        where member_id = %s
        """,
        (
            protected_payload["protectedEmail"],
            protected_payload["protectedPhoneNumber"],
            protected_payload["protectedDateOfBirth"],
            protected_payload["protectedPassport"],
            protected_payload["protectedDiagnosis"],
            member_id,
        ),
    )
    connection.commit()

    return protected_payload
