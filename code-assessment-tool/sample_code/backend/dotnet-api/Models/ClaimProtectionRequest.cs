namespace Sample.DotNetApi.Models;

public class ClaimProtectionRequest
{
    public string ClaimNumber { get; set; } = string.Empty;
    public string MemberEmail { get; set; } = string.Empty;
    public string HouseholdId { get; set; } = string.Empty;
    public string SalaryAmount { get; set; } = string.Empty;
    public string HomeAddress { get; set; } = string.Empty;
}
