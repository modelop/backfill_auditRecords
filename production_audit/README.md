# ModelOp Production Use Case AuditRecords

### ***Secure, validated approach to retrieve audit records associated with production Use Cases.***

---

## Overview

This is a production-ready Python solution for identifying audit records for use cases in production in ModelOp Center 3.4.

### The Solution

This toolkit provides:

- **`production_audit.py`** — Captures all audit records associated with use cases in production.
- **Comprehensive CSV exports** — Enable audit trail

---

## <img src="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/folder/default/48px.svg" width="24" height="24" alt="files" /> Repository Structure

```
backfill_auditRecords/
├── requirements.txt                          # Python dependencies
│
├── production_audit.py                       # Script
│
└── Generated Outputs (after running scripts)
    ├── storedmodels.csv            # Production StoredModels snapshot
    ├── auditrecords.csv            # AuditRecords 
```

---

## <img src="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/settings/default/48px.svg" width="24" height="24" alt="config" /> Configuration & Setup

### Prerequisites

- Python 3.7+
- Access to ModelOp Center 3.4 API
- Bearer/Access token

### Environment Variables

```plaintext
MOC_BASE_URL=https://your-instance.modelop.center
MOC_ACCESS_TOKEN=<cached-oauth2-token>
PRODUCTION_MODEL_STAGE_VALUE=prod
```

```

---

## <img src="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/terminal/default/48px.svg" width="24" height="24" alt="install" /> Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **requests** ≥ 2.28.0 — HTTP client for API calls
- **pandas** ≥ 1.5.0 — DataFrame and CSV handling

### First Run Setup

```bash
python production_audit.py
```

---

## <img src="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/warning/default/48px.svg" width="24" height="24" alt="troubleshoot" /> Troubleshooting Guide

### Authentication Issues


**Error**: `401 Unauthorized` or `Failed to authenticate`
```bash
# Check your bearer token/access token and environment URL
python production_audit.py

```

### API Connection Issues

**Error**: `Connection timeout` or `HTTPConnectionPool`
- Verify network connectivity to ModelOp Center instance
- Check base URL is correct
- Verify firewall/proxy settings aren't blocking API calls
- Test connectivity: `ping your-instance.modelop.center`

**Error**: `404 Not Found` on endpoints
- Verify endpoint paths are correct for your environment
- Confirm `/api/storedModels/search/findProductionUseCases` exists in your version
- Check API documentation for available endpoints

---

### Data & Script Issues

**Error**: `No production StoredModels discovered`
- Verify StoredModels exist and are in production stage
- Check `PRODUCTION_MODEL_STAGE_VALUE` (default: `prod`)
- Run preflight with debug logging for details


**Error**: CSV files are empty or minimal
- Check script logs for error messages

---

### Windows-Specific Issues

**Error**: `'python' is not recognized as an internal or external command`
```bash
# Use python3 or full path to Python executable
python3 production_audit.py
# Or:
C:\Python310\python.exe production_audit.py
```
---

## Quick Reference

### Common Commands

```bash
# First time setup
pip install -r requirements.txt
python production_audit.py

# Capture current state
python production_audit.py

### CSV Column Guide

**auditrecords.csv**:
- `storedModelId` — StoredModel UUID
- `auditRecordId` — Existing AuditRecord UUID (NULL if none)
- `auditRecordCreatedDate` — When the AuditRecord was created
- `recordExists` — TRUE/FALSE whether AuditRecord currently exists

---

## Security Best Practices

✅ **Implemented in this toolkit**:
- OAuth2 token cached locally for reuse
- HTTPS for all API calls

⚠️ **Additional recommendations**:
- Use service accounts for automated deployments
- Rotate credentials periodically
- Consider AWS Secrets Manager or HashiCorp Vault for production environments

---

## Support & Debugging

**For detailed debugging**, enable Python logging:

1. Edit the script to set logging level to DEBUG:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Run the script and capture full logs:
   ```bash
   python production_audit.py > production_audit.log 2>&1
   ```

3. Review the detailed logs for specific error information

**For script issues**:
1. Review generated CSV files to understand current state
2. Check the detailed logs (enable DEBUG logging above)
3. Verify API endpoints are accessible and correct
4. Ensure your credentials are valid

## Implementation Details

---

## Files & Configuration

### Included Files

| File | Purpose |
|------|---------|
| `production_audit.py` | Non-destructive GET-only validation script |
| `requirements.txt` | Python package dependencies |
| `.vscode/settings.json` | VS Code integrated terminal configuration |

### Auto-Generated Files

After running scripts, you'll have:

```
storedmodels.csv              # StoredModels snapshot
auditrecords.csv              # AuditRecords 
```
---

**Last Updated**: March 12, 2026  
**Version**: 1.0 — Production Ready  