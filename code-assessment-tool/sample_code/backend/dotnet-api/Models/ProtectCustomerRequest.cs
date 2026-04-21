namespace SampleCompany.Models;

public class ProtectCustomerRequest
{
    public string? Email { get; set; }
    public string? PhoneNumber { get; set; }
    public string? DateOfBirth { get; set; }
    public string? Ssn { get; set; }
    public string? AccountNumber { get; set; }
    public string? RoutingNumber { get; set; }
}
