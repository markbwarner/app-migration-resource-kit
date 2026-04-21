const express = require("express");
const axios = require("axios");
const { Pool } = require("pg");

const app = express();
const pool = new Pool({ connectionString: process.env.CLAIMS_DB_URL });

app.use(express.json());

app.get("/api/claims/:claimId", async (req, res) => {
  const result = await pool.query(
    `select claim_number, member_email, household_id, salary_amount, home_address
       from claim_review
      where claim_id = $1`,
    [req.params.claimId]
  );

  res.json(result.rows[0]);
});

app.post("/api/claims/:claimId/protect", async (req, res) => {
  const crdpResponse = await axios.post(
    "https://ciphertrust.example.com/v1/protect/claim-review",
    {
      claimNumber: req.body.claimNumber,
      memberEmail: req.body.memberEmail,
      householdId: req.body.householdId,
      salaryAmount: req.body.salaryAmount,
      homeAddress: req.body.homeAddress,
    }
  );

  await pool.query(
    `update claim_review
        set member_email = $1,
            household_id = $2,
            salary_amount = $3,
            home_address = $4
      where claim_id = $5`,
    [
      crdpResponse.data.memberEmail,
      crdpResponse.data.householdId,
      crdpResponse.data.salaryAmount,
      crdpResponse.data.homeAddress,
      req.params.claimId,
    ]
  );

  res.json({
    claimNumber: req.body.claimNumber,
    protectedFields: ["memberEmail", "householdId", "salaryAmount", "homeAddress"],
  });
});

app.listen(3100);
