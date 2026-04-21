using Microsoft.AspNetCore.Mvc;
using Sample.DotNetApi.Models;
using Sample.DotNetApi.Services;

namespace Sample.DotNetApi.Controllers;

[ApiController]
[Route("api/claims")]
public class ClaimReviewController : ControllerBase
{
    private readonly ClaimReviewService _claimReviewService;

    public ClaimReviewController(ClaimReviewService claimReviewService)
    {
        _claimReviewService = claimReviewService;
    }

    [HttpGet("{claimId}")]
    public ActionResult<ClaimReviewRecord> GetClaimReview(string claimId)
    {
        return Ok(_claimReviewService.LoadClaimReview(claimId));
    }

    [HttpPost("{claimId}/protect")]
    public ActionResult<object> ProtectClaimReview(string claimId, [FromBody] ClaimProtectionRequest request)
    {
        return Ok(_claimReviewService.ProtectClaimReview(claimId, request));
    }
}
