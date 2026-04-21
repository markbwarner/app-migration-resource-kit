import React, { useEffect, useState } from "react";
import axios from "axios";

type ClaimReview = {
  claimNumber: string;
  memberEmail: string;
  householdId: string;
  salaryAmount: string;
  homeAddress: string;
};

export function ClaimReviewScreen() {
  const [claimReview, setClaimReview] = useState<ClaimReview | null>(null);

  useEffect(() => {
    axios
      .get("/api/claims/CLM-101")
      .then((response) => setClaimReview(response.data))
      .catch((error) => console.error("Unable to load claim review", error));
  }, []);

  async function protectClaim() {
    if (!claimReview) {
      return;
    }

    await fetch("/api/claims/CLM-101/protect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        claimNumber: claimReview.claimNumber,
        memberEmail: claimReview.memberEmail,
        householdId: claimReview.householdId,
        salaryAmount: claimReview.salaryAmount,
        homeAddress: claimReview.homeAddress,
      }),
    });
  }

  if (!claimReview) {
    return <div>Loading claim review...</div>;
  }

  return (
    <section>
      <h2>Claim Review</h2>
      <div>Claim Number: {claimReview.claimNumber}</div>
      <div>Email: {claimReview.memberEmail}</div>
      <div>Household: {claimReview.householdId}</div>
      <div>Salary: {claimReview.salaryAmount}</div>
      <div>Address: {claimReview.homeAddress}</div>
      <button onClick={protectClaim}>Protect Claim Data</button>
    </section>
  );
}
