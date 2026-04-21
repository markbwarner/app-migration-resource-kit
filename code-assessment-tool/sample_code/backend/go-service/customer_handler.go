package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"net/http"
)

type CustomerPayload struct {
	CustomerID    string `json:"customerId"`
	Email         string `json:"email"`
	PhoneNumber   string `json:"phoneNumber"`
	DateOfBirth   string `json:"dateOfBirth"`
	NationalID    string `json:"nationalId"`
	AccountNumber string `json:"accountNumber"`
}

func ProtectCustomerHandler(db *sql.DB, writer http.ResponseWriter, request *http.Request) {
	var payload CustomerPayload
	_ = json.NewDecoder(request.Body).Decode(&payload)

	crdpRequest, _ := json.Marshal(payload)
	response, _ := http.Post(
		"https://ciphertrust.example.com/v1/protect/customer",
		"application/json",
		bytes.NewBuffer(crdpRequest),
	)

	var protectedPayload map[string]string
	_ = json.NewDecoder(response.Body).Decode(&protectedPayload)

	statement, _ := db.Prepare(`
		update customer_profile
		set email = ?, phone_number = ?, date_of_birth = ?, national_id = ?, account_number = ?
		where customer_id = ?
	`)

	_, _ = statement.Exec(
		protectedPayload["protectedEmail"],
		protectedPayload["protectedPhoneNumber"],
		protectedPayload["protectedDateOfBirth"],
		protectedPayload["protectedNationalId"],
		protectedPayload["protectedAccountNumber"],
		payload.CustomerID,
	)
}
