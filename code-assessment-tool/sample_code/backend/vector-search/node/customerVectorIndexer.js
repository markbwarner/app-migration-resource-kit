async function indexCustomerDocument(vectorIndex, customerProfile) {
  const protectResponse = await fetch("https://ciphertrust.example.com/v1/protect/customer-vector", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customerId: customerProfile.customerId,
      email: customerProfile.email,
      phoneNumber: customerProfile.phoneNumber,
      homeAddress: customerProfile.homeAddress,
      dateOfBirth: customerProfile.dateOfBirth,
    }),
  });

  const protectedProfile = await protectResponse.json();

  await vectorIndex.upsert([
    {
      id: customerProfile.customerId,
      text: `Customer ${protectedProfile.protectedEmail} ${protectedProfile.protectedPhoneNumber}`,
      metadata: {
        email: protectedProfile.protectedEmail,
        phoneNumber: protectedProfile.protectedPhoneNumber,
        homeAddress: protectedProfile.protectedHomeAddress,
        dateOfBirth: protectedProfile.protectedDateOfBirth,
      },
    },
  ]);
}

module.exports = { indexCustomerDocument };
