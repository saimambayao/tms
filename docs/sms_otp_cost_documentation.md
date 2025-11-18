# SMS OTP Cost Documentation - #FahanieCares Portal

## Overview

The #FahanieCares portal implements SMS OTP (One-Time Password) as an accessible two-factor authentication option for constituents who may not have smartphones or email access. This document outlines the cost structure and payment arrangements for this government-funded service.

## Cost Responsibility

**The Philippine government, through the Office of MP Atty. Sittie Fahanie S. Uy-Oyod, covers all SMS OTP costs.**

This ensures equal access to security features for all constituents regardless of their economic status, in line with the #FahanieCares mission of "Bringing Public Service Closer to You."

## SMS Gateway Options and Pricing

### Primary Provider: Semaphore (Recommended for Philippine Market)

**Government Contract Rates:**
- Standard Rate: ₱0.15 - ₱0.30 per SMS
- Bulk Discounts Available:
  - 10,000+ messages/month: ₱0.12 per SMS
  - 50,000+ messages/month: ₱0.10 per SMS
  - 100,000+ messages/month: ₱0.08 per SMS

**Features:**
- Local Philippine provider
- Direct carrier connections
- 99.9% delivery rate
- Real-time delivery reports
- Government-compliant infrastructure

### Backup Provider: Twilio (International Option)

**Rates to Philippine Numbers:**
- Standard Rate: ₱1.50 - ₱2.00 per SMS
- Volume discounts available for enterprise accounts

**When to Use:**
- International constituents
- Backup during Semaphore outages
- Special routing requirements

## Cost Projections

### Monthly Estimates (Based on User Base)

| User Base | OTPs/Month* | Semaphore Cost | Twilio Cost |
|-----------|-------------|----------------|-------------|
| 1,000 users | 3,000 | ₱300 - ₱900 | ₱4,500 - ₱6,000 |
| 5,000 users | 15,000 | ₱1,500 - ₱4,500 | ₱22,500 - ₱30,000 |
| 10,000 users | 30,000 | ₱2,400 - ₱9,000 | ₱45,000 - ₱60,000 |
| 50,000 users | 150,000 | ₱12,000 - ₱45,000 | ₱225,000 - ₱300,000 |

*Assumes average of 3 OTP requests per user per month

### Annual Budget Planning

For a projected 10,000 active users:
- **Using Semaphore**: ₱28,800 - ₱108,000 per year
- **Using Twilio**: ₱540,000 - ₱720,000 per year

**Recommended Budget**: ₱150,000 annually (includes buffer for growth)

## Cost Control Measures

### 1. Rate Limiting
- Maximum 3 OTP requests per hour per user
- Prevents abuse and controls costs
- Implemented in `SMSOTPService` class

### 2. Smart Routing
- Use Semaphore for Philippine numbers (+63)
- Use Twilio only for international numbers
- Automatic failover between providers

### 3. Monitoring and Alerts
- Daily SMS usage reports
- Budget threshold alerts (75%, 90%, 100%)
- Unusual activity detection

### 4. Optimization Strategies
- Extend OTP validity to 5 minutes (reduces resends)
- Clear user instructions to minimize errors
- Backup codes to reduce SMS dependency

## Implementation Details

### Configuration (config/settings/base.py)
```python
# Government-funded SMS service
SMS_PROVIDER = 'semaphore'  # Primary provider
SEMAPHORE_API_KEY = os.environ.get('SEMAPHORE_API_KEY')
SEMAPHORE_SENDER_NAME = 'FAHANIECARES'

# Backup provider
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Cost control
SMS_OTP_MAX_REQUESTS_PER_HOUR = 3
SMS_OTP_VALIDITY_MINUTES = 5
```

### Usage Tracking
The system tracks:
- Total SMS sent per day/month
- SMS per user
- Failed delivery attempts
- Cost per department/chapter

## Budget Allocation Process

### 1. Initial Setup
- Government allocates initial SMS budget
- Set up prepaid accounts with providers
- Configure automatic top-ups

### 2. Monthly Process
- Finance department reviews usage reports
- Adjusts budget based on actual usage
- Approves next month's allocation

### 3. Procurement
- Follow government procurement guidelines
- Negotiate bulk rates with providers
- Annual contract reviews

## Reporting and Accountability

### Monthly Reports Include:
1. Total SMS sent and costs
2. Usage by user type (constituent, staff, etc.)
3. Geographic distribution
4. Success/failure rates
5. Cost per successful authentication

### Quarterly Reviews:
- Cost optimization opportunities
- Provider performance evaluation
- User feedback on SMS delivery
- Budget adjustment recommendations

## Alternative Funding Models (Future Consideration)

### 1. Shared Cost Model
- Government covers first 3 OTPs/month
- Users pay for additional OTPs
- Not recommended due to accessibility concerns

### 2. Department Allocation
- Each department/ministry allocated SMS budget
- Based on constituent base size
- Requires complex tracking

### 3. Grant Funding
- Seek technology grants for SMS costs
- Partner with telcos for CSR programs
- Explore international aid for digital inclusion

## Compliance and Regulations

### NPC (National Privacy Commission) Requirements:
- User consent for SMS communications
- Secure storage of phone numbers
- Data retention policies
- Breach notification procedures

### Government Accounting:
- Proper documentation of all SMS expenses
- Audit trail for each message sent
- Regular reconciliation with providers
- COA (Commission on Audit) compliance

## Contact for Budget Matters

**Finance Department**
- Email: finance@fahaniecares.ph
- Phone: +63 XX XXX XXXX

**Technical Implementation**
- Email: tech@fahaniecares.ph
- Phone: +63 XX XXX XXXX

**SMS Provider Accounts**
- Semaphore Account Manager: [Contact Details]
- Twilio Enterprise Support: [Contact Details]

---

*Last Updated: January 2025*
*Document Version: 1.0*
*Next Review: July 2025*