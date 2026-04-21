namespace SampleCompany.Models;

public class CustomPatternLiterals
{
    public string HouseholdIdLiteral => "HH-123456";
    public string HouseholdNbrAlias => "householdNbr";
    public string HhIdAlias => "hhId";
    public string AccountNumberLiteral => "123456789012";
    public string AcctNbrAlias => "acctNbr";
    public string AccntNbrAlias => "accntNbr";
    public string SalaryLiteral => "$125,000";
    public string Comment = "Household HH-998877 should map to account 9876543210 and salary $150,000";
}
