import React, { useEffect, useState } from "react";
import axios from "axios";

type CustomerProfile = {
  customerId: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  ssnLast4: string;
  dateOfBirth: string;
  homeAddress: string;
};

export function CustomerProfileScreen() {
  const [profile, setProfile] = useState<CustomerProfile | null>(null);

  useEffect(() => {
    axios
      .get("/api/customers/12345/profile")
      .then((response) => setProfile(response.data))
      .catch((error) => console.error("Unable to load customer profile", error));
  }, []);

  async function updateProfile() {
    if (!profile) {
      return;
    }

    await fetch("/api/customers/12345/profile", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        firstName: profile.firstName,
        lastName: profile.lastName,
        email: profile.email,
        phoneNumber: profile.phoneNumber,
        homeAddress: profile.homeAddress,
        dateOfBirth: profile.dateOfBirth,
      }),
    });
  }

  if (!profile) {
    return <div>Loading customer details...</div>;
  }

  return (
    <section>
      <h1>Customer Profile</h1>
      <div>First Name: {profile.firstName}</div>
      <div>Last Name: {profile.lastName}</div>
      <div>Email: {profile.email}</div>
      <div>Phone: {profile.phoneNumber}</div>
      <div>Date Of Birth: {profile.dateOfBirth}</div>
      <div>Address: {profile.homeAddress}</div>
      <div>SSN Last 4: {profile.ssnLast4}</div>
      <button onClick={updateProfile}>Save</button>
    </section>
  );
}
