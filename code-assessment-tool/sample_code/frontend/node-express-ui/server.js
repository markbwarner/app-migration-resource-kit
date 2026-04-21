const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.json());

app.get("/customer-search", async (req, res) => {
  const query = {
    email: req.query.email,
    phoneNumber: req.query.phoneNumber,
    taxId: req.query.taxId,
  };

  const response = await axios.get("http://backend.internal/api/customer-search", {
    params: query,
  });

  res.json({
    requestedEmail: query.email,
    requestedPhoneNumber: query.phoneNumber,
    requestedTaxId: query.taxId,
    backendPayload: response.data,
  });
});

app.post("/beneficiary", async (req, res) => {
  const payload = {
    firstName: req.body.firstName,
    lastName: req.body.lastName,
    bankAccount: req.body.bankAccount,
    routingNumber: req.body.routingNumber,
    homeAddress: req.body.homeAddress,
  };

  const response = await fetch("http://backend.internal/api/beneficiary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  res.json(await response.json());
});

app.listen(3000);
