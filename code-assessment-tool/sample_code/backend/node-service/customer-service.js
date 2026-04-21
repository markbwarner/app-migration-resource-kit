const express = require("express");
const kafka = require("kafkajs");
const { Client } = require("pg");

const app = express();
app.use(express.json());

const db = new Client({ connectionString: process.env.CUSTOMER_DB_URL });
const producer = new kafka.Kafka({ clientId: "customer-service", brokers: ["kafka-1:9092"] }).producer();

app.post("/api/customer/protect", async (req, res) => {
  const payload = {
    firstName: req.body.firstName,
    lastName: req.body.lastName,
    email: req.body.email,
    phoneNumber: req.body.phoneNumber,
    dateOfBirth: req.body.dateOfBirth,
    ssn: req.body.ssn,
  };

  const crdpResponse = await fetch("https://ciphertrust.example.com/v1/protect/customer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const protectedPayload = await crdpResponse.json();

  await db.query(
    `
    insert into customer_audit(customer_id, email, phone_number, ssn, date_of_birth)
    values ($1, $2, $3, $4, $5)
    `,
    [
      req.body.customerId,
      protectedPayload.protectedEmail,
      protectedPayload.protectedPhoneNumber,
      protectedPayload.protectedSsn,
      protectedPayload.protectedDateOfBirth,
    ]
  );

  await producer.send({
    topic: "customer-protection-events",
    messages: [
      {
        key: req.body.customerId,
        value: JSON.stringify({
          customerId: req.body.customerId,
          email: protectedPayload.protectedEmail,
          phoneNumber: protectedPayload.protectedPhoneNumber,
          ssn: protectedPayload.protectedSsn,
        }),
      },
    ],
  });

  res.json(protectedPayload);
});

app.listen(8080);
