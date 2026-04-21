using System.Data.SqlClient;
using System.Net.Http.Json;
using Sample.DotNetApi.Models;

namespace Sample.DotNetApi.Services;

public class ClaimReviewService
{
    private readonly HttpClient _httpClient;
    private readonly string _connectionString = "Server=tcp:claims;Database=claims;";

    public ClaimReviewService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public ClaimReviewRecord LoadClaimReview(string claimId)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();

        using var command = new SqlCommand(
            @"select claim_number, member_email, household_id, salary_amount, home_address
                from claim_review
               where claim_id = @claimId",
            connection);
        command.Parameters.AddWithValue("@claimId", claimId);

        using var reader = command.ExecuteReader();
        reader.Read();

        return new ClaimReviewRecord
        {
            ClaimNumber = reader["claim_number"].ToString(),
            MemberEmail = reader["member_email"].ToString(),
            HouseholdId = reader["household_id"].ToString(),
            SalaryAmount = reader["salary_amount"].ToString(),
            HomeAddress = reader["home_address"].ToString()
        };
    }

    public object ProtectClaimReview(string claimId, ClaimProtectionRequest request)
    {
        var response = _httpClient.PostAsJsonAsync(
            "https://ciphertrust.example.com/v1/protect/claims",
            new
            {
                request.ClaimNumber,
                request.MemberEmail,
                request.HouseholdId,
                request.SalaryAmount,
                request.HomeAddress
            }).Result;

        var protectedPayload = response.Content.ReadFromJsonAsync<ClaimProtectionPayload>().Result;

        using var connection = new SqlConnection(_connectionString);
        connection.Open();

        using var command = new SqlCommand(
            @"update claim_review
                 set member_email = @memberEmail,
                     household_id = @householdId,
                     salary_amount = @salaryAmount,
                     home_address = @homeAddress
               where claim_id = @claimId",
            connection);
        command.Parameters.AddWithValue("@memberEmail", protectedPayload!.MemberEmail);
        command.Parameters.AddWithValue("@householdId", protectedPayload.HouseholdId);
        command.Parameters.AddWithValue("@salaryAmount", protectedPayload.SalaryAmount);
        command.Parameters.AddWithValue("@homeAddress", protectedPayload.HomeAddress);
        command.Parameters.AddWithValue("@claimId", claimId);
        command.ExecuteNonQuery();

        return new
        {
            claimId,
            protectedFields = new[] { "memberEmail", "householdId", "salaryAmount", "homeAddress" }
        };
    }
}
