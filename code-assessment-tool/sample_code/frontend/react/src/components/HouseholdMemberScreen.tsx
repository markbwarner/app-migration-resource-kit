import React, { useEffect, useState } from "react";
import axios from "axios";

type HouseholdMember = {
  householdId: string;
  primaryEmail: string;
  salaryAmount: string;
  accntNbr: string;
  homeAddress: string;
};

export function HouseholdMemberScreen() {
  const [members, setMembers] = useState<HouseholdMember[]>([]);

  useEffect(() => {
    axios
      .get("/api/households/7788/members")
      .then((response) => setMembers(response.data))
      .catch((error) => console.error("Unable to load household members", error));
  }, []);

  async function protectMembers() {
    const firstMember = members[0];
    if (!firstMember) {
      return;
    }

    await fetch("/api/households/7788/protect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        householdId: firstMember.householdId,
        primaryEmail: firstMember.primaryEmail,
        salaryAmount: firstMember.salaryAmount,
        accntNbr: firstMember.accntNbr,
        homeAddress: firstMember.homeAddress,
      }),
    });
  }

  return (
    <section>
      <h2>Household Members</h2>
      {members.map((member) => (
        <div key={member.householdId}>
          <div>Email: {member.primaryEmail}</div>
          <div>Salary: {member.salaryAmount}</div>
          <div>Account: {member.accntNbr}</div>
          <div>Address: {member.homeAddress}</div>
        </div>
      ))}
      <button onClick={protectMembers}>Protect Household Data</button>
    </section>
  );
}
