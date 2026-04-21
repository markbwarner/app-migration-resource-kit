using Microsoft.AspNetCore.Mvc;
using SampleCompany.Services;

namespace SampleCompany.Controllers;

[ApiController]
[Route("api/customer")]
public class CustomerController : ControllerBase
{
    private readonly CustomerService _customerService;

    public CustomerController(CustomerService customerService)
    {
        _customerService = customerService;
    }

    [HttpGet("{customerId}")]
    public async Task<IActionResult> GetCustomer(string customerId)
    {
        var profile = await _customerService.LoadCustomerAsync(customerId);
        return Ok(profile);
    }

    [HttpPost("{customerId}/protect")]
    public async Task<IActionResult> ProtectCustomer(string customerId, [FromBody] ProtectCustomerRequest request)
    {
        var result = await _customerService.ProtectCustomerAsync(customerId, request);
        return Ok(result);
    }
}
