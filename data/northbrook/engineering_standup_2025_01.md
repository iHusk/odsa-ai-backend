# Northbrook Partners — Engineering Team Meeting Notes

**Date:** January 14, 2025
**Location:** Virtual (Zoom)
**Time:** 10:00 AM - 11:15 AM CT

---

## Attendees

- **Maria Rodriguez**, CTO
- **Kevin Okafor**, VP of Engineering
- **Priya Sharma**, Lead Engineer — Platform Team
- **Marcus Johnson**, Lead Engineer — Client Solutions Team
- **Elena Vasquez**, Lead Engineer — Data Engineering Team
- **Chris Hayward**, Senior Engineer — DevOps

**Absent:** None

---

## 1. Cloud Infrastructure Migration Update (Project Atlas)

Priya Sharma provided an update on Project Atlas — the ongoing migration from on-premises infrastructure to AWS. The migration is currently **55% complete**, tracking slightly behind the original Q2 2025 target. The remaining work involves migrating PRISM Reports (the legacy reporting services) and the client data warehouse, which Priya described as the most complex components due to data residency requirements.

Key milestones completed:
- All development and staging environments are now fully cloud-hosted.
- CI/CD pipelines have been migrated to GitHub Actions.
- Northbrook Core (the internal platform) authentication service was moved to AWS Cognito in December.

Remaining work:
- Client data warehouse migration (estimated 6 weeks).
- PRISM Reports refactoring and migration (estimated 8 weeks).
- Final security audit and penetration testing (estimated 3 weeks after migration).

Maria asked about risk to the timeline. Priya noted that the PRISM Reports refactoring could extend if unexpected dependencies are found, but the team has allocated a 2-week buffer. Revised completion target: **end of Q2 2025**.

## 2. Partner Gateway v2 Launch Timeline

Marcus Johnson presented the status of Partner Gateway v2 (API v2), which introduces a modernized RESTful API for client integrations. The new API replaces the legacy SOAP-based interface and includes improved authentication (OAuth 2.0), pagination, rate limiting, and webhook support.

Current status:
- Core endpoints are feature-complete and undergoing internal testing.
- Documentation is 80% complete, with the interactive API explorer on track for delivery by end of January.
- Beta testing with 3 pilot clients is scheduled to begin **February 10, 2025**.
- General availability target: **March 31, 2025**.

Marcus raised a concern about backward compatibility. Several existing clients rely on specific behaviors of the v1 API that do not have direct equivalents in v2. The team has built a compatibility shim, but Marcus recommended maintaining the v1 API in read-only mode for 6 months post-launch to give clients time to migrate.

Maria approved the backward-compatibility plan and asked Marcus to prepare a client communication plan by January 24.

## 3. Hiring Update

Kevin Okafor provided an update on engineering hiring. Of the 15 positions approved by the board in Q3 2024, **9 have been filled**. The remaining 6 positions are:

- 2 senior backend engineers (3 candidates in final round)
- 1 senior frontend engineer (2 candidates in final round)
- 1 mid-level data engineer (offer extended, awaiting response)
- 1 mid-level platform engineer (sourcing)
- 1 junior engineer (sourcing)

Kevin expects to close 4 of the 6 remaining positions by the end of Q1 2025. He noted that the senior frontend role has been particularly competitive, and the team may need to adjust the compensation band to attract qualified candidates. Maria agreed to discuss with James Wright.

Additionally, Kevin mentioned that the newly approved AI initiative will require **hiring 3 more senior engineers** with experience in machine learning infrastructure, LLM integration, and evaluation frameworks. These positions are separate from the original 15 and will be posted in February.

## 4. Technical Debt and Maintenance

Elena Vasquez raised the topic of technical debt in the data pipeline layer. The current ETL jobs were written 3 years ago and use libraries that are approaching end-of-life. She proposed allocating 20% of the data engineering team's time in Q1 to refactoring the most critical pipelines.

After discussion, Maria approved the allocation with the condition that Elena prioritize the pipelines affecting client-facing reporting first. Elena will present a prioritized list at the next meeting.

## 5. Action Items

| Owner | Action | Due Date |
|-------|--------|----------|
| Marcus Johnson | Prepare Partner Gateway v2 client communication plan | Jan 24, 2025 |
| Kevin Okafor | Discuss frontend engineer comp band with James Wright | Jan 17, 2025 |
| Kevin Okafor | Post 3 AI engineering positions | Feb 1, 2025 |
| Elena Vasquez | Present data pipeline refactoring priorities | Jan 28, 2025 |
| Priya Sharma | Updated Project Atlas migration timeline with risk register | Jan 21, 2025 |

---

*Notes compiled by Kevin Okafor. Next meeting: January 28, 2025.*
