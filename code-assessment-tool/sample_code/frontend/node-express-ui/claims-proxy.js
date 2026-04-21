const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.json());

app.get("/claims-review/:claimId", async (req, res) => {
  const response = await axios.get(`http://backend.internal/api/claims/${req.params.claimId}`);
  res.json(response.data);
});

app.post("/claims-review/:claimId/protect", async (req, res) => {
  const payload = {
    claimNumber: req.body.claimNumber,
    memberEmail: req.body.memberEmail,
    householdId: req.body.householdId,
    salaryAmount: req.body.salaryAmount,
    homeAddress: req.body.homeAddress,
  };

  const response = await axios.post(
    `http://backend.internal/api/claims/${req.params.claimId}/protect`,
    payload
  );

  res.json(response.data);
});

app.listen(4201);
