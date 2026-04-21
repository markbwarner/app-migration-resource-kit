using System.Data;
using Microsoft.Data.SqlClient;
using SampleCompany.Models;

namespace SampleCompany.Services;

public class CustomerService
{
    private readonly HttpClient _httpClient;
    private readonly string _connectionString;

    public CustomerService(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _connectionString = configuration.GetConnectionString("CustomerDb");
    }

    public async Task<CustomerProfile> LoadCustomerAsync(string customerId)
    {
        await using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();

        await using var command = new SqlCommand(
            """
            select customer_id, first_name, last_name, email, phone_number, date_of_birth,
                   ssn, account_number, routing_number
            from customer_profile
            where customer_id = @customerId
            """,
            connection);

        command.Parameters.Add(new SqlParameter("@customerId", SqlDbType.VarChar) { Value = customerId });
        await using var reader = await command.ExecuteReaderAsync();
        await reader.ReadAsync();

        return new CustomerProfile
        {
            CustomerId = reader["customer_id"].ToString(),
            FirstName = reader["first_name"].ToString(),
            LastName = reader["last_name"].ToString(),
            Email = reader["email"].ToString(),
            PhoneNumber = reader["phone_number"].ToString(),
            DateOfBirth = reader["date_of_birth"].ToString(),
            Ssn = reader["ssn"].ToString(),
            AccountNumber = reader["account_number"].ToString(),
            RoutingNumber = reader["routing_number"].ToString()
        };
    }

    public async Task<object> ProtectCustomerAsync(string customerId, ProtectCustomerRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync(
            "https://ciphertrust.example.com/v1/protect/customer",
            new
            {
                request.Email,
                request.PhoneNumber,
                request.DateOfBirth,
                request.Ssn,
                request.AccountNumber,
                request.RoutingNumber
            });

        var protectedPayload = await response.Content.ReadFromJsonAsync<ProtectedCustomerPayload>();

        await using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();
        await using var command = new SqlCommand(
            """
            update customer_profile
            set email = @email,
                phone_number = @phoneNumber,
                date_of_birth = @dateOfBirth,
                ssn = @ssn,
                account_number = @accountNumber,
                routing_number = @routingNumber
            where customer_id = @customerId
            """,
            connection);

        command.Parameters.AddWithValue("@email", protectedPayload!.ProtectedEmail);
        command.Parameters.AddWithValue("@phoneNumber", protectedPayload.ProtectedPhoneNumber);
        command.Parameters.AddWithValue("@dateOfBirth", protectedPayload.ProtectedDateOfBirth);
        command.Parameters.AddWithValue("@ssn", protectedPayload.ProtectedSsn);
        command.Parameters.AddWithValue("@accountNumber", protectedPayload.ProtectedAccountNumber);
        command.Parameters.AddWithValue("@routingNumber", protectedPayload.ProtectedRoutingNumber);
        command.Parameters.AddWithValue("@customerId", customerId);
        await command.ExecuteNonQueryAsync();

        return new { customerId, protectedFields = new[] { "Email", "PhoneNumber", "DateOfBirth", "Ssn", "AccountNumber", "RoutingNumber" } };
    }
}
