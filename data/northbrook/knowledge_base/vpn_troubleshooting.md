# VPN & Cloudflare Zero Trust — Troubleshooting Guide

## Common Issues After Security Updates

After scheduled security updates, the Cloudflare Zero Trust client may require re-authentication or cache clearing. Follow these steps in order:

### Step 1: Force Re-Authentication
1. Click the Cloudflare WARP icon in your system tray
2. Select "Preferences" → "Account"
3. Click "Re-authenticate" and log in with your Northbrook SSO credentials
4. Wait 30 seconds for the tunnel to re-establish

### Step 2: Clear Client Cache
If re-authentication doesn't resolve the issue:
1. Quit the Cloudflare WARP client completely
2. Delete the folder: `~/.cloudflare-warp/` (Mac) or `%APPDATA%\Cloudflare\` (Windows)
3. Restart the WARP client
4. Re-authenticate per Step 1

### Step 3: Check Split Tunnel Configuration
Some applications may be excluded from the VPN tunnel. Verify that your required services (GitHub, internal APIs, Jira) are routed through the tunnel in Preferences → Split Tunnels.

### When to Escalate
If the above steps don't resolve your issue within 15 minutes, contact the Network Infrastructure team. Include:
- Your device type and OS version
- Screenshot of the WARP client status
- Output of `warp-cli status` (terminal command)

**SLA:** VPN issues affecting remote workers are treated as high priority. Target response: 2 hours during business hours.
