/**
 * frontend/src/utils/propagation.ts
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * Deep contextual threat propagation model. Extracts real technical mechanics,
 * protocol vectors, lateral paths, and executive business impacts for any CVE.
 */

import { Asset, Vulnerability } from '../types';

export interface PropagationStage {
  step: number;
  id: string;
  title: string;
  subtitle: string;
  actor: string;
  target: string;
  protocol: string;
  techniqueId: string;
  techniqueName: string;
  description: string;
  status: 'critical' | 'warning' | 'info' | 'contained';
  iconName: 'globe' | 'shield' | 'terminal' | 'server' | 'database' | 'alert';
}

export interface VulnerabilityPropagationProfile {
  vulnType: string;
  cweLabel: string;
  affectedSoftwareName: string;
  threatActorIp: string;
  ingressPort: string;
  localExecutionPort: string;
  trajectoryBadges: {
    ingress: string;
    trigger: string;
    lateral: string;
    impact: string;
  };
  nodeLabels: {
    node2Title: string;
    node2Sub: string;
    node2Ip: string;
  };
  executiveBrief: {
    headline: string;
    businessImpact: string;
    blastRadius: string;
    urgencyRationale: string;
    executiveAction: string;
    financialRiskLevel: 'Critical' | 'High' | 'Moderate' | 'Low';
    regulatoryImpact: string;
  };
  technicalDeepDive: {
    rootCause: string;
    protocolVector: string;
    propagationMechanism: string;
    detectionSignatures: string[];
    containmentControls: string[];
    vlanExposure: string;
  };
  stages: PropagationStage[];
}

export function getVulnerabilityPropagationProfile(
  vuln: Vulnerability,
  asset: Asset,
  sourceIp: string = '198.51.100.44'
): VulnerabilityPropagationProfile {
  const cve = (vuln.cve_id || '').toUpperCase();
  const desc = (vuln.description || '').toLowerCase();
  const rawDesc = vuln.description || '';
  const isKev = Boolean(vuln.in_kev);
  const isInternetFacing = asset.exposure === 'internet_facing';
  const isCriticalAsset = asset.criticality === 'critical';

  // ─────────────────────────────────────────────────────────────────────────
  // 1. SPECIFIC PROFILE: Palo Alto Networks PAN-OS GlobalProtect (CVE-2024-3400)
  // ─────────────────────────────────────────────────────────────────────────
  if (cve.includes('2024-3400') || (desc.includes('pan-os') && desc.includes('command injection'))) {
    return {
      vulnType: 'OS Command Injection via GlobalProtect Telemetry',
      cweLabel: 'CWE-78: Improper Neutralization of Special Elements used in an OS Command',
      affectedSoftwareName: 'Palo Alto Networks PAN-OS GlobalProtect',
      threatActorIp: sourceIp || '198.51.100.44',
      ingressPort: 'HTTPS:443',
      localExecutionPort: 'ROOT SHELL:443',
      trajectoryBadges: {
        ingress: 'INBOUND T1190:443',
        trigger: 'ROOT CMD INJECTION',
        lateral: 'INTERNAL ROUTE PIVOT',
        impact: 'SECURITY BYPASS T1562',
      },
      nodeLabels: {
        node2Title: 'Root Bash Subshell',
        node2Sub: 'PAN-OS Linux Kernel (root)',
        node2Ip: `${asset.ip}:443 (root)`,
      },
      executiveBrief: {
        headline: `Zero-day perimeter firewall compromise: Threat actors executing arbitrary root commands on primary gateway ${asset.hostname}`,
        businessImpact:
          `Compromise of ${asset.hostname} collapses perimeter network segregation. Because this appliance manages firewall access policies, attackers can disable traffic inspection, tap encrypted VPN traffic, and traverse into internal production enclaves with unrestricted network routing authority.`,
        blastRadius:
          'Border-Wide Infrastructure Breach: The firewall sits at the apex of all enterprise trust zones; root compromise grants full visibility over perimeter, partner interconnects, and corporate VLANs.',
        urgencyRationale:
          'Listed in CISA KEV; actively exploited by nation-state cyber espionage groups as an initial access broker before distributing ransomware.',
        executiveAction:
          'Authorize immediate deployment of vendor hotfix (PAN-OS 10.2 / 11.0 / 11.1); immediately disable Device Telemetry feature if patching window requires postponement.',
        financialRiskLevel: 'Critical',
        regulatoryImpact:
          'Catastrophic audit failure under PCI-DSS Requirement 1 (Network Security Controls) and SOC 2 Trust Principles due to total firewall control loss.',
      },
      technicalDeepDive: {
        rootCause:
          'Failure to sanitize HTTP session cookies before passing parameter values to internal telemetry bash scripts, allowing arbitrary shell command execution with root privileges.',
        protocolVector:
          `Inbound HTTPS POST requests directed to GlobalProtect gateway on ${asset.ip}:443 containing shell metacharacters in SESSID cookie values.`,
        propagationMechanism:
          'Attacker spawns persistent reverse root shell, modifies system crontab, harvests firewall configuration credentials, and creates GRE/SSH tunnels into internal application and database subnets.',
        detectionSignatures: [
          'PAN-OS system logs: Abnormal file generation under /opt/panlogs/tmp/device_telemetry/hour/',
          'Snort / Suricata: ET EXPLOIT Palo Alto PAN-OS GlobalProtect Command Injection (CVE-2024-3400)',
          'Endpoint / Telemetry: Unexpected outbound SSH/curl connections initiated from firewall management control plane.',
        ],
        containmentControls: [
          'Immediate Workaround: Disable "Device Telemetry" under Device -> Setup -> Telemetry.',
          'Hotfix: Upgrade PAN-OS to 10.2.9-h1, 11.0.4-h1, or 11.1.2-h3.',
          'Perimeter ACL: Restrict GlobalProtect portal access exclusively to sanctioned geolocations or enterprise source IPs.',
        ],
        vlanExposure: 'External Edge Gateway -> Full Unrestricted Routing into All Internal Corporate VLANs',
      },
      stages: [
        {
          step: 1,
          id: 'stage_recon',
          title: 'Perimeter Reconnaissance & Ingress',
          subtitle: 'GlobalProtect Portal Probing',
          actor: 'Remote Threat Actor',
          target: `${asset.hostname} (Port 443)`,
          protocol: 'HTTPS / TLS (Port 443)',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            `Attacker identifies exposed GlobalProtect VPN portal on ${asset.hostname} (${asset.ip}) running vulnerable PAN-OS software version.`,
          status: 'critical',
          iconName: 'globe',
        },
        {
          step: 2,
          id: 'stage_ingress',
          title: 'Cookie Parameter Manipulation',
          subtitle: 'Arbitrary File Creation in Telemetry',
          actor: 'Crafted Inbound POST',
          target: `${asset.hostname} Web Server`,
          protocol: 'HTTP Cookie SESSID',
          techniqueId: 'T1059.004',
          techniqueName: 'Unix Shell Execution',
          description:
            'Malformed SESSID cookie containing directory traversal and shell command injection payload bypasses authentication and creates payload file in telemetry directory.',
          status: 'critical',
          iconName: 'server',
        },
        {
          step: 3,
          id: 'stage_execution',
          title: 'Root Command Execution',
          subtitle: 'Cron Job Execution with Root Privileges',
          actor: 'System Cron Service',
          target: 'PAN-OS Linux OS (Root)',
          protocol: 'OS Subshell (/bin/sh)',
          techniqueId: 'T1068',
          techniqueName: 'Exploitation for Privilege Escalation',
          description:
            'Internal cron job evaluates the injected file path without input sanitization, executing commands as root and establishing persistent reverse connection.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'stage_propagation',
          title: 'Firewall Policy & Network Traversal',
          subtitle: 'Internal Routing & Trust Zone Bypass',
          actor: 'Compromised Firewall OS',
          target: 'Internal Core Networks',
          protocol: 'Internal Routing / SSH Tunnel',
          techniqueId: 'T1021.004',
          techniqueName: 'SSH Hijacking & Tunneling',
          description:
            'Operating from the firewall root plane, attacker modifies routing rules and establishes encrypted tunnels to probe internal cluster databases without generating security alerts.',
          status: 'warning',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'stage_impact',
          title: 'Network Control & Strategic Exfiltration',
          subtitle: 'Total Security Architecture Compromise',
          actor: 'Threat Actor',
          target: 'Enterprise Core Data Stores & Active Directory',
          protocol: 'Internal VPN Routing',
          techniqueId: 'T1562.001',
          techniqueName: 'Impair Defenses: Disable Tools',
          description:
            'Adversary exfiltrates active administrative session tokens, disables security logging, and prepares domain-wide lateral expansion.',
          status: 'critical',
          iconName: 'database',
        },
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // 2. SPECIFIC PROFILE: Log4Shell (CVE-2021-44228)
  // ─────────────────────────────────────────────────────────────────────────
  if (cve.includes('2021-44228') || desc.includes('log4j') || desc.includes('jndi')) {
    return {
      vulnType: 'JNDI Format String Remote Code Execution (Log4Shell)',
      cweLabel: 'CWE-502 / CWE-917: Deserialization of Untrusted Data & Expression Injection',
      affectedSoftwareName: 'Apache Log4j2 (versions 2.0-beta9 to 2.15.0)',
      threatActorIp: sourceIp || '198.51.100.44',
      ingressPort: 'HTTP/S:443',
      localExecutionPort: 'LDAP CALLBACK:1389',
      trajectoryBadges: {
        ingress: 'INBOUND T1190:443',
        trigger: 'JNDI LDAP CALLBACK',
        lateral: 'LATERAL PIVOT:SMB',
        impact: 'CORE EXFILTRATION',
      },
      nodeLabels: {
        node2Title: 'Java VM Subshell',
        node2Sub: 'Injected Bytecode Execution',
        node2Ip: `${asset.ip}:1389`,
      },
      executiveBrief: {
        headline: `Weaponized zero-click remote code execution actively compromising public gateway ${asset.hostname}`,
        businessImpact:
          'Attackers can commandeer complete control of customer-facing infrastructure, intercept confidential transactional sessions, and use the compromised server as a foothold into internal back-office databases.',
        blastRadius:
          isInternetFacing
            ? 'Enterprise-wide Perimeter Breach: Direct internet ingress exposes entire production DMZ and internal core networks.'
            : 'Internal Segment Breach: Restricted to local network segment unless lateral pivoting occurs.',
        urgencyRationale:
          'Listed in CISA Known Exploited Vulnerabilities (KEV). Active wild weaponization observed with automated worming payloads.',
        executiveAction:
          'Mandate emergency change freeze: Apply immediate Log4j patch, terminate active reverse-proxy sessions, and block egress LDAP/RMI ports.',
        financialRiskLevel: 'Critical',
        regulatoryImpact: 'High risk of GDPR/PCI-DSS regulatory violation due to plaintext API token exposure.',
      },
      technicalDeepDive: {
        rootCause:
          'Log4j2 JNDI parser evaluates user-controllable lookup strings (${jndi:ldap://...}) in log message format strings without input sanitization.',
        protocolVector:
          'Inbound HTTP/HTTPS requests (User-Agent, Authorization headers, or form fields) triggering outbound TCP LDAP (389), RMI (1099), or DNS resolution.',
        propagationMechanism:
          'Upon payload evaluation, the host initiates an outbound callback to an attacker-controlled directory server, downloads arbitrary Java bytecode, and executes local commands with application service privileges.',
        detectionSignatures: [
          'SIEM / Web Server logs containing obfuscated strings: ${jndi:ldap://, ${jndi:rmi://, or ${lower:j}ndi:',
          'Suricata / Snort alert: ET EXPLOIT Apache Log4j JNDI Exploit Attempt Outbound Callback',
          'EDR Process telemetry: java / apache process spawning /bin/sh, /bin/bash, cmd.exe, or powershell.exe',
        ],
        containmentControls: [
          'Perimeter Firewall: Immediately drop outbound TCP traffic on ports 389, 636, 1099, 1389.',
          'Environment Variable: Set LOG4J_FORMAT_MSG_NO_LOOKUPS=true to disable recursive JNDI expansion.',
          'Patch Management: Upgrade log4j-core library to version 2.17.1 or higher.',
        ],
        vlanExposure: 'Perimeter DMZ -> Lateral pivot to Internal Application Cluster (VLAN 10 -> VLAN 20)',
      },
      stages: [
        {
          step: 1,
          id: 'stage_recon',
          title: 'External Weaponization',
          subtitle: 'Reconnaissance & JNDI Formulation',
          actor: 'Remote Threat Actor',
          target: 'Internet Perimeter Gateway',
          protocol: 'HTTP / HTTPS (Port 443)',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            'Attacker transmits crafted HTTP requests with obfuscated JNDI lookup strings in HTTP headers (User-Agent, X-Forwarded-For).',
          status: 'critical',
          iconName: 'globe',
        },
        {
          step: 2,
          id: 'stage_ingress',
          title: 'Perimeter Ingress & Logging',
          subtitle: `Ingress on ${asset.hostname}`,
          actor: 'Inbound Web Request',
          target: `${asset.hostname} (${asset.ip})`,
          protocol: 'TCP / HTTP Gateway',
          techniqueId: 'T1059',
          techniqueName: 'Command & Scripting Interpreter',
          description:
            `Target application logs the HTTP request. Log4j parser interprets the nested variable and initiates remote object resolution.`,
          status: 'critical',
          iconName: 'server',
        },
        {
          step: 3,
          id: 'stage_execution',
          title: 'Outbound Callback & Deserialization',
          subtitle: 'Egress Payload Fetch (Port 1389)',
          actor: `Compromised ${asset.hostname}`,
          target: `Attacker Directory (${sourceIp}:1389)`,
          protocol: 'LDAP / RMI (Port 1389/389)',
          techniqueId: 'T1071.001',
          techniqueName: 'Application Layer Protocol: Web Protocols',
          description:
            'Target server reaches out through perimeter firewall to attacker LDAP server, downloads compiled malicious Java bytecode, and spawns interactive shell.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'stage_propagation',
          title: 'Internal Cluster Pivoting',
          subtitle: 'Credential Harvesting & Lateral Sweep',
          actor: 'Injected Subshell',
          target: 'Internal Application Cluster',
          protocol: 'Internal LAN / RPC / SMB',
          techniqueId: 'T1021.002',
          techniqueName: 'Remote Services: SMB/Admin Shares',
          description:
            'Bytecode extracts local process environment variables (AWS_ACCESS_KEY, DB_PASSWORDS) and scans internal subnets for secondary targets.',
          status: 'warning',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'stage_impact',
          title: 'Database Vault Exfiltration',
          subtitle: 'Core Enterprise Data Threat',
          actor: 'Threat Actor',
          target: 'Enterprise Core DB & Active Directory',
          protocol: 'SQL Query / Database Exfil',
          techniqueId: 'T1486',
          techniqueName: 'Data Encrypted for Impact / Exfiltration',
          description:
            'Attacker connects directly to internal database stores using captured credentials, staging exfiltration or destructive data extortion.',
          status: 'critical',
          iconName: 'database',
        },
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // 3. SPECIFIC PROFILE: Citrix ADC / Bleed (CVE-2023-4966 / CVE-2023-3519)
  // ─────────────────────────────────────────────────────────────────────────
  if (cve.includes('2023-4966') || cve.includes('2023-3519') || desc.includes('netscaler') || desc.includes('citrix bleed')) {
    const isBleed = cve.includes('2023-4966') || desc.includes('bleed');
    return {
      vulnType: isBleed ? 'Session Token Memory Leak (Citrix Bleed)' : 'Memory Buffer Overflow & Gateway RCE',
      cweLabel: isBleed
        ? 'CWE-119: Improper Restriction of Operations within the Bounds of a Memory Buffer'
        : 'CWE-120: Buffer Copy without Checking Size of Input',
      affectedSoftwareName: 'Citrix NetScaler ADC / Gateway',
      threatActorIp: sourceIp || '198.51.100.44',
      ingressPort: 'HTTPS:443',
      localExecutionPort: 'NSPPE MEMORY:443',
      trajectoryBadges: {
        ingress: 'INBOUND T1190:443',
        trigger: isBleed ? 'SESSION TOKEN LEAK' : 'BUFFER OVERFLOW',
        lateral: 'VPN TUNNEL PIVOT',
        impact: 'MFA BYPASS ACCESS',
      },
      nodeLabels: {
        node2Title: isBleed ? 'Session Token Memory' : 'NSPPE Process Shell',
        node2Sub: 'Packet Engine Memory Leak',
        node2Ip: `${asset.ip}:443`,
      },
      executiveBrief: {
        headline: `Perimeter gateway authentication bypass: Stolen session tokens allowing full corporate VPN ingress without MFA`,
        businessImpact:
          `Attackers can impersonate authenticated executive and engineering staff on ${asset.hostname}. By replaying leaked session tokens, attackers bypass multi-factor authentication entirely and access internal corporate networks as authorized staff.`,
        blastRadius:
          'Critical Remote Access Breach: Acts as the front door for corporate access. Compromise bypasses firewalls and MFA controls.',
        urgencyRationale:
          'Documented in CISA KEV; widely weaponized by ransomware syndicates to establish persistent network access.',
        executiveAction:
          'Apply official Citrix firmware patch immediately, terminate all active Citrix gateway sessions, and force multi-factor re-authentication company-wide.',
        financialRiskLevel: 'Critical',
        regulatoryImpact: 'Severe compliance failure under SOC 2 and ISO 27001 Access Control domains.',
      },
      technicalDeepDive: {
        rootCause:
          'Unauthenticated buffer overread in NetScaler OpenID / OAuth endpoint allows attackers to dump process memory containing valid session tokens.',
        protocolVector:
          `Inbound HTTPS GET requests to /oauth/idp/.well-known/openid-configuration with oversized Host headers.`,
        propagationMechanism:
          'Attacker extracts valid session cookies from the response, replays them against /vpn/index.html, and uses the resulting authenticated VPN tunnel to access internal corporate workstations.',
        detectionSignatures: [
          'NetScaler HTTP logs: Requests with unusually long Host headers (> 2048 bytes)',
          'Session anomaly: Single session cookie active from disparate geographical IP addresses simultaneously.',
          'Firewall: Sudden spike in inbound traffic directed to /vpn/ authentication URIs.',
        ],
        containmentControls: [
          'Patch: Upgrade NetScaler ADC to release 13.1-49.15 or 14.1-8.50.',
          'Kill Sessions: Execute CLI command "kill aaa session -all" to invalidate all leaked cookies.',
          'ACL: Restrict management GUI (NSIP) to private administrative subnets.',
        ],
        vlanExposure: 'External Edge Gateway -> Direct VPN Tunnel into Corporate Workstation LAN',
      },
      stages: [
        {
          step: 1,
          id: 'stage_recon',
          title: 'Gateway Fingerprinting',
          subtitle: 'Citrix Gateway Version Discovery',
          actor: 'Remote Threat Actor',
          target: `${asset.hostname} (Port 443)`,
          protocol: 'HTTPS (Port 443)',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            `Attacker probes public SSL-VPN endpoint on ${asset.hostname} (${asset.ip}) to confirm presence of unpatched NetScaler firmware.`,
          status: 'warning',
          iconName: 'globe',
        },
        {
          step: 2,
          id: 'stage_ingress',
          title: 'Memory Overread Exploitation',
          subtitle: 'Malformed OpenID HTTP Request',
          actor: 'Inbound Request',
          target: `${asset.hostname} NSPPE Engine`,
          protocol: 'HTTP Host Header',
          techniqueId: 'T1552.001',
          techniqueName: 'Unsecured Credentials: Process Memory',
          description:
            'Attacker transmits crafted payload triggering buffer overread, causing the NetScaler process to dump active memory pages in HTTP responses.',
          status: 'critical',
          iconName: 'server',
        },
        {
          step: 3,
          id: 'stage_execution',
          title: 'Session Token Extraction',
          subtitle: 'Zero-Authentication MFA Bypass',
          actor: 'Attacker Parser',
          target: `${asset.hostname} Token Store`,
          protocol: 'Extracted Session Cookie',
          techniqueId: 'T1556',
          techniqueName: 'Modify Authentication Process',
          description:
            'Adversary extracts valid NSC_AAAC session tokens from memory dump, enabling full impersonation of logged-in corporate users without credentials.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'stage_propagation',
          title: 'Authenticated VPN Tunnel Pivoting',
          subtitle: 'Internal Corporate LAN Infiltration',
          actor: 'Hijacked VPN Session',
          target: 'Internal Corporate Subnets',
          protocol: 'IPSec / SSL-VPN Tunnel',
          techniqueId: 'T1021.001',
          techniqueName: 'Remote Desktop Protocol / SMB',
          description:
            'Using the legitimate VPN tunnel, the attacker scans internal Active Directory domain controllers, fileservers, and developer workstations.',
          status: 'warning',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'stage_impact',
          title: 'Domain Compromise & Data Staging',
          subtitle: 'Enterprise-Wide Foothold',
          actor: 'Threat Actor',
          target: 'Active Directory & Critical Core Stores',
          protocol: 'Kerberos / LDAP',
          techniqueId: 'T1486',
          techniqueName: 'Enterprise Access Control Hijack',
          description:
            'Adversary escalates privileges to Domain Admin and stages ransomware payloads across core server infrastructure.',
          status: 'critical',
          iconName: 'database',
        },
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // 4. SPECIFIC PROFILE: Apache Tomcat Ghostcat (CVE-2020-1938)
  // ─────────────────────────────────────────────────────────────────────────
  if (cve.includes('2020-1938') || desc.includes('ghostcat') || desc.includes('ajp')) {
    return {
      vulnType: 'AJP Connector Arbitrary File Read / Remote Code Execution (Ghostcat)',
      cweLabel: 'CWE-20: Improper Input Validation in Apache JServ Protocol (AJP)',
      affectedSoftwareName: 'Apache Tomcat (versions 6.x, 7.x, 8.x, 9.x)',
      threatActorIp: sourceIp || '198.51.100.44',
      ingressPort: 'AJP:8009',
      localExecutionPort: 'JVM PROCESS:8009',
      trajectoryBadges: {
        ingress: 'INBOUND AJP:8009',
        trigger: 'FILE READ / INCLUDE',
        lateral: 'APP CLUSTER PIVOT',
        impact: 'SOURCE CODE EXFIL',
      },
      nodeLabels: {
        node2Title: 'Tomcat AJP Worker',
        node2Sub: 'Arbitrary File Inclusion',
        node2Ip: `${asset.ip}:8009`,
      },
      executiveBrief: {
        headline: `High-risk application server file disclosure on ${asset.hostname}: Attackers reading server configurations and database credentials`,
        businessImpact:
          `Attackers exploiting the misconfigured AJP connector on ${asset.hostname} can download internal application source code, configuration files (web.xml), and database credentials stored on the server without authentication.`,
        blastRadius:
          'Application Subnet Threat: Exposes backend configuration secrets, enabling rapid secondary compromise of connected databases.',
        urgencyRationale:
          'CISA KEV listed; common scanning target across corporate cloud deployments where port 8009 is inadvertently exposed.',
        executiveAction:
          'Disable the AJP connector in Tomcat server.xml or upgrade to patched Tomcat release (9.0.31+, 8.5.51+).',
        financialRiskLevel: 'High',
        regulatoryImpact: 'High risk of credential compromise leading to customer database breach.',
      },
      technicalDeepDive: {
        rootCause:
          'Tomcat AJP connector implicitly trusts incoming connections on port 8009 without authentication, allowing attackers to manipulate request attributes and read arbitrary files from web application roots.',
        protocolVector: 'Direct TCP connection to port 8009 using Apache JServ Protocol v1.3 framing.',
        propagationMechanism:
          'Attacker downloads application configuration files, extracts database passwords, and combines file inclusion with web upload to execute arbitrary JSP web shells.',
        detectionSignatures: [
          'Network telemetry: Unexpected inbound connections on TCP port 8009 originating from external or non-proxy IPs.',
          'Snort alert: ET EXPLOIT Apache Tomcat AJP File Read/Inclusion (CVE-2020-1938)',
          'Host logs: Spikes in access to WEB-INF/web.xml or uploaded temporary files.',
        ],
        containmentControls: [
          'Immediate Config: Comment out <Connector port="8009" protocol="AJP/1.3" /> in conf/server.xml.',
          'Firewall: Block inbound TCP port 8009 at external and internal subnet firewalls.',
          'If AJP required: Add requiredSecret attribute to enforce authentication.',
        ],
        vlanExposure: 'App Subnet -> Direct Extraction of Database Credentials -> Database Vault',
      },
      stages: [
        {
          step: 1,
          id: 'stage_recon',
          title: 'AJP Port Discovery',
          subtitle: 'TCP Port 8009 Scanning',
          actor: 'Remote Threat Actor',
          target: `${asset.hostname} (Port 8009)`,
          protocol: 'TCP Port 8009',
          techniqueId: 'T1046',
          techniqueName: 'Network Service Discovery',
          description:
            `Attacker discovers open AJP 1.3 connector port on ${asset.hostname} (${asset.ip}) during automated port scanning.`,
          status: 'info',
          iconName: 'globe',
        },
        {
          step: 2,
          id: 'stage_ingress',
          title: 'AJP Request Framing',
          subtitle: 'Request Attribute Injection',
          actor: 'Custom AJP Client',
          target: `${asset.hostname} AJP Connector`,
          protocol: 'AJP 1.3 Protocol',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            'Attacker transmits crafted AJP request specifying javax.servlet.include.request_uri parameters to override file access boundaries.',
          status: 'critical',
          iconName: 'server',
        },
        {
          step: 3,
          id: 'stage_execution',
          title: 'Arbitrary File Read & Secret Leak',
          subtitle: 'Extraction of web.xml & Credentials',
          actor: 'Tomcat JVM Worker',
          target: `${asset.hostname} Filesystem`,
          protocol: 'File System Stream',
          techniqueId: 'T1552.001',
          techniqueName: 'Credentials In Files',
          description:
            'Tomcat returns raw file contents of server configuration files, exposing database credentials, API tokens, and application source code.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'stage_propagation',
          title: 'Database Access Pivoting',
          subtitle: 'Direct Internal SQL Connection',
          actor: 'Attacker Client',
          target: 'Internal Database Cluster',
          protocol: 'JDBC / SQL Protocol',
          techniqueId: 'T1078',
          techniqueName: 'Valid Accounts',
          description:
            'Using database credentials stolen from web.xml, the attacker authenticates directly to internal database servers on the local subnet.',
          status: 'warning',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'stage_impact',
          title: 'Customer Data Store Dumping',
          subtitle: 'Exfiltration of Proprietary Data',
          actor: 'Threat Actor',
          target: 'Enterprise Core Data Stores',
          protocol: 'Database Connection',
          techniqueId: 'T1567',
          techniqueName: 'Exfiltration Over Web Service',
          description:
            'Attacker dumps tables containing sensitive customer records, completing the data theft objective.',
          status: 'critical',
          iconName: 'database',
        },
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // 5. SPECIFIC PROFILE: Fortinet FortiOS SSL-VPN (CVE-2024-21762)
  // ─────────────────────────────────────────────────────────────────────────
  if (cve.includes('2024-21762') || (desc.includes('fortinet') && desc.includes('out-of-bounds'))) {
    return {
      vulnType: 'Out-of-Bounds Write Remote Code Execution via SSL-VPN',
      cweLabel: 'CWE-787: Out-of-bounds Write',
      affectedSoftwareName: 'Fortinet FortiOS SSL-VPN',
      threatActorIp: sourceIp || '198.51.100.44',
      ingressPort: 'HTTPS:8443',
      localExecutionPort: 'KERNEL BUFFER:8443',
      trajectoryBadges: {
        ingress: 'INBOUND T1190:8443',
        trigger: 'OUT-OF-BOUNDS RCE',
        lateral: 'ROUTING TABLE PIVOT',
        impact: 'CREDENTIAL EXFIL',
      },
      nodeLabels: {
        node2Title: 'SSL-VPN Worker Subshell',
        node2Sub: 'FortiOS Kernel Memory Hijack',
        node2Ip: `${asset.ip}:8443`,
      },
      executiveBrief: {
        headline: `Critical perimeter SSL-VPN boundary collapse on ${asset.hostname}: Remote unauthenticated code execution`,
        businessImpact:
          `Attackers can execute arbitrary instructions with root privileges on primary remote access gateway ${asset.hostname} without credentials, disabling perimeter inspection and intercepting enterprise VPN sessions.`,
        blastRadius:
          'Total Gateway Compromise: As the front door for corporate remote access, root control over the appliance exposes all encrypted transit tunnels and connected internal enterprise subnets.',
        urgencyRationale:
          'CISA KEV listed; actively exploited by advanced persistent threat (APT) groups against enterprise and government entities.',
        executiveAction:
          'Immediately apply Fortinet security update (FortiOS 7.4.3+, 7.2.7+, 7.0.14+) or disable SSL-VPN functionality entirely until patched.',
        financialRiskLevel: 'Critical',
        regulatoryImpact:
          'Severe compliance violation under SOC 2 and ISO 27001 due to unauthenticated edge perimeter bypass.',
      },
      technicalDeepDive: {
        rootCause:
          'Out-of-bounds write in FortiOS SSL-VPN daemon caused by improper handling of chunked HTTP request transfer encodings, allowing unauthenticated remote code execution via specially crafted web requests.',
        protocolVector:
          `Inbound HTTPS requests directed to ${asset.ip}:8443 or :443 containing malformed chunked transfer encoding headers.`,
        propagationMechanism:
          'Adversary overwrites adjacent heap control blocks, hijacks control flow into memory shellcode, spawns interactive root session, and dumps local administrative credential caches.',
        detectionSignatures: [
          'FortiOS system event log: Spikes in crash log entries referencing sslvpnd process segfaults.',
          'Snort/Suricata alert: ET EXPLOIT Fortinet FortiOS SSL-VPN Out-of-Bounds Write (CVE-2024-21762)',
          'Network telemetry: Unexpected external connections on SSL-VPN port with malformed HTTP Transfer-Encoding headers.',
        ],
        containmentControls: [
          'Upgrade FortiOS firmware to 7.4.3, 7.2.7, 7.0.14, or 6.4.15 immediately.',
          'Workaround: Disable SSL-VPN service (config vpn ssl settings -> set status disable).',
          'Perimeter ACL: Restrict inbound SSL-VPN access strictly to pre-approved corporate IP ranges.',
        ],
        vlanExposure: 'External Perimeter Edge -> Direct Routing Pivoting into Core Internal Subnets',
      },
      stages: [
        {
          step: 1,
          id: 'stage_recon',
          title: 'SSL-VPN Portal Probing',
          subtitle: 'FortiOS Endpoint Fingerprinting',
          actor: 'Remote Threat Actor',
          target: `${asset.hostname} (Port 8443)`,
          protocol: 'HTTPS (Port 8443)',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            `Attacker discovers open FortiOS SSL-VPN portal on ${asset.hostname} (${asset.ip}) during perimeter service scanning.`,
          status: 'warning',
          iconName: 'globe',
        },
        {
          step: 2,
          id: 'stage_ingress',
          title: 'Chunked Transfer Manipulation',
          subtitle: 'Malformed HTTP Transfer-Encoding',
          actor: 'Inbound Web Request',
          target: `${asset.hostname} SSL-VPN Engine`,
          protocol: 'HTTP/HTTPS Header',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            'Crafted HTTP request containing malformed chunked transfer encoding triggers memory buffer corruption in sslvpnd daemon.',
          status: 'critical',
          iconName: 'server',
        },
        {
          step: 3,
          id: 'stage_execution',
          title: 'Heap Corruption & Code Injection',
          subtitle: 'Unauthenticated Control Flow Hijack',
          actor: 'Kernel Injected Shellcode',
          target: 'FortiOS Memory & Root Plane',
          protocol: 'Memory Execution',
          techniqueId: 'T1059',
          techniqueName: 'Command and Scripting Interpreter',
          description:
            'Adversary overwrites return address in heap memory, executing arbitrary shellcode with elevated operating system privileges.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'stage_propagation',
          title: 'Corporate VPN Routing Bypass',
          subtitle: 'Enterprise Tunnel Pivoting',
          actor: 'Compromised VPN Gateway',
          target: 'Internal Enclave Networks',
          protocol: 'IPSec / SSL-VPN Internal Routes',
          techniqueId: 'T1021',
          techniqueName: 'Remote Services',
          description:
            'Leveraging the compromised gateway, the threat actor accesses internal corporate VLANs without traversing secondary perimeter firewalls.',
          status: 'warning',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'stage_impact',
          title: 'Administrative Credential Exfiltration',
          subtitle: 'Core Enterprise Authentication Compromise',
          actor: 'Threat Actor',
          target: 'Active Directory & Corporate Identity Stores',
          protocol: 'Credential Dumping',
          techniqueId: 'T1003',
          techniqueName: 'OS Credential Dumping',
          description:
            'Adversary harvests session secrets and enterprise credentials, gaining long-term persistent access across enterprise infrastructure.',
          status: 'critical',
          iconName: 'database',
        },
      ],
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // 6. DYNAMIC HEURISTIC SYNTHESIS: For ALL other 8,328 CVEs and Custom Inputs
  // ─────────────────────────────────────────────────────────────────────────
  // Determine flaw classification dynamically
  let vulnType = 'Remote Software Vulnerability';
  let cweLabel = 'CWE-Unknown (Software Flaw)';
  let primaryTechId = 'T1190';
  let primaryTechName = 'Exploit Public-Facing Application';
  let executionDetail = 'Spawns unauthorized OS subshell or memory corruption payload';
  let triggerBadge = 'EXPLOIT TRIGGER:443';
  let portUsed = isInternetFacing ? 'HTTPS:443' : 'TCP:8080';

  if (desc.includes('command injection') || desc.includes('shell injection') || desc.includes('execute commands')) {
    vulnType = 'OS Command Injection Vulnerability';
    cweLabel = 'CWE-78: OS Command Injection';
    primaryTechId = 'T1059.004';
    primaryTechName = 'Command and Scripting Interpreter: Unix Shell';
    executionDetail = 'Executes arbitrary shell commands under application account privileges';
    triggerBadge = 'CMD INJECTION:443';
  } else if (desc.includes('remote code execution') || desc.includes('rce') || desc.includes('execute arbitrary code')) {
    vulnType = 'Remote Code Execution (RCE)';
    cweLabel = 'CWE-94: Improper Control of Generation of Code';
    primaryTechId = 'T1203';
    primaryTechName = 'Exploitation for Client/Server Execution';
    executionDetail = 'Injects arbitrary executable instructions into application process memory';
    triggerBadge = 'RCE PAYLOAD:443';
  } else if (desc.includes('buffer overflow') || desc.includes('out-of-bounds write') || desc.includes('memory corruption')) {
    vulnType = 'Memory Corruption / Buffer Overflow';
    cweLabel = 'CWE-787 / CWE-120: Out-of-bounds Write / Buffer Overflow';
    primaryTechId = 'T1190';
    primaryTechName = 'Exploit Public-Facing Application';
    executionDetail = 'Overwrites adjacent memory boundaries to hijack execution flow and register pointers';
    triggerBadge = 'BUFFER OVERFLOW';
  } else if (desc.includes('sql injection') || desc.includes('sqli')) {
    vulnType = 'SQL Injection (Data Extraction & Manipulation)';
    cweLabel = 'CWE-89: SQL Injection';
    primaryTechId = 'T1190';
    primaryTechName = 'Exploit Public-Facing Application';
    executionDetail = 'Alters backend SQL statement logic to dump, modify, or delete database tables';
    portUsed = 'SQL:3306';
    triggerBadge = 'SQL INJECTION';
  } else if (desc.includes('authentication bypass') || desc.includes('bypass security') || desc.includes('authorization')) {
    vulnType = 'Authentication Bypass / Security Misconfiguration';
    cweLabel = 'CWE-287: Improper Authentication';
    primaryTechId = 'T1556';
    primaryTechName = 'Modify Authentication Process';
    executionDetail = 'Circumvents authentication checks, granting administrative access without credentials';
    triggerBadge = 'AUTH BYPASS:443';
  } else if (desc.includes('path traversal') || desc.includes('directory traversal') || desc.includes('arbitrary file')) {
    vulnType = 'Directory Traversal & Arbitrary File Access';
    cweLabel = 'CWE-22: Path Traversal';
    primaryTechId = 'T1006';
    primaryTechName = 'Direct Volume Access / Arbitrary File Read';
    executionDetail = 'Traverses restricted parent directories to read sensitive host configuration files';
    triggerBadge = 'PATH TRAVERSAL';
  } else if (desc.includes('denial of service') || desc.includes('dos') || desc.includes('crash')) {
    vulnType = 'Denial of Service (DoS)';
    cweLabel = 'CWE-400: Uncontrolled Resource Consumption';
    primaryTechId = 'T1499';
    primaryTechName = 'Endpoint Denial of Service';
    executionDetail = 'Consumes CPU or memory pools, causing service crash and loss of availability';
    triggerBadge = 'SERVICE CRASH';
  }

  // Derive software component name
  let softwareName = 'Installed Application Service';
  if (Array.isArray(asset.software) && asset.software.length > 0) {
    softwareName = asset.software[0];
  } else if (typeof asset.software === 'string' && asset.software) {
    softwareName = asset.software;
  }
  if (vuln.affected_products && vuln.affected_products.length > 3) {
    const parts = vuln.affected_products.split(':');
    if (parts.length > 4 && parts[4]) {
      softwareName = `${parts[3]} ${parts[4]}`.replace(/_/g, ' ');
    }
  }

  const financialRiskLevel =
    isCriticalAsset && isKev ? 'Critical' : isCriticalAsset || isKev ? 'High' : 'Moderate';

  return {
    vulnType,
    cweLabel,
    affectedSoftwareName: softwareName,
    threatActorIp: sourceIp || '198.51.100.44',
    ingressPort: portUsed,
    localExecutionPort: `${portUsed} (Compromised)`,
    trajectoryBadges: {
      ingress: `INBOUND ${primaryTechId}:${portUsed.split(':')[1] || '443'}`,
      trigger: triggerBadge,
      lateral: 'LATERAL PIVOT',
      impact: 'DATA / VAULT RISK',
    },
    nodeLabels: {
      node2Title: `${vulnType} Trigger`,
      node2Sub: `${softwareName} Process`,
      node2Ip: `${asset.ip} (${softwareName})`,
    },
    executiveBrief: {
      headline: `${vulnType} flaw directly impacting ${softwareName} on ${asset.hostname}`,
      businessImpact: isCriticalAsset
        ? `Adversaries exploiting ${cve} can compromise mission-critical ${softwareName} running on ${asset.hostname}. Because this system fulfills a ${asset.criticality} operational tier (${asset.notes || 'core infrastructure'}), successful exploitation directly threatens business uptime and operational resilience.`
        : `Exploitation grants attackers an unauthorized foothold on ${asset.hostname}. While currently isolated, threat actors can leverage this system as a low-profile staging ground to traverse toward critical databases.`,
      blastRadius: isInternetFacing
        ? `External Perimeter Threat: Since ${asset.hostname} is internet-facing (${asset.ip}), opportunistic threat actors can discover and trigger ${cve} remotely without possessing internal credentials.`
        : `Internal Subnet Risk: Requires internal access or an existing compromised workstation to trigger.`,
      urgencyRationale: isKev
        ? `Formally flagged in CISA KEV Catalogue as actively exploited in wild attacks. Immediate patch priority required.`
        : `Evaluated with CVSS score ${vuln.cvss_score.toFixed(1)}. Remediation should be prioritized based on asset criticality (${asset.criticality.toUpperCase()}).`,
      executiveAction:
        isCriticalAsset || isKev
          ? `Issue 24-hour emergency containment directive: Apply vendor security update for ${softwareName}, inspect recent firewall logs for ${asset.ip}, and restrict ingress traffic.`
          : `Schedule remediation within the standard 7-day vulnerability management window for ${asset.hostname}.`,
      financialRiskLevel,
      regulatoryImpact: isCriticalAsset
        ? 'High regulatory exposure: Unmitigated compromise of critical tiers triggers mandatory reporting under GDPR / NIS 2 and SOC 2 compliance frameworks.'
        : 'Standard compliance reporting required under annual cybersecurity audit.',
    },
    technicalDeepDive: {
      rootCause:
        rawDesc || `Vulnerability in ${softwareName} allowing unauthorized manipulation of host resources.`,
      protocolVector: isInternetFacing
        ? `Inbound external network packets directed to ${asset.ip}:${portUsed.split(':')[1] || '443'} targeting ${softwareName}.`
        : `Internal protocol connections within local subnet (${asset.ip}).`,
      propagationMechanism:
        `${executionDetail}. Attacker then attempts privilege escalation, extracts active memory tokens, and scans adjacent internal IP ranges for unpatched services.`,
      detectionSignatures: [
        `SIEM Telemetry: Inbound connections directed to ${asset.ip} from non-sanctioned external IPs with unexpected payload signatures.`,
        `Host Process Monitoring: Abnormal child process creation spawned by ${softwareName} service binaries.`,
        `Network Flow: Unexpected outbound TCP connection spikes or internal subnet port sweeps initiated from ${asset.ip}.`,
      ],
      containmentControls: [
        `Network Isolation: Implement microsegmentation ACL limiting ${asset.hostname} communication strictly to verified upstream proxies.`,
        `Software Patching: Upgrade ${softwareName} to latest vendor-recommended patched release immediately.`,
        `Process Monitoring: Terminate any rogue subprocesses spawned from the ${softwareName} daemon and rotate local service secrets.`,
      ],
      vlanExposure: isInternetFacing
        ? `Perimeter Ingress -> Lateral Pivot across internal network (${asset.ip})`
        : `Internal Workstation / Server Subnet (${asset.ip})`,
    },
    stages: [
      {
        step: 1,
        id: 'stage_recon',
        title: 'Adversary Reconnaissance',
        subtitle: `Discovery of ${softwareName}`,
        actor: 'External Threat Actor',
        target: `${asset.hostname} (${asset.ip})`,
        protocol: isInternetFacing ? `Public ${portUsed}` : 'Internal Subnet Sweep',
        techniqueId: 'T1046',
        techniqueName: 'Network Service Discovery',
        description:
          `Attacker scans enterprise perimeter and identifies exposed ${softwareName} listening on ${asset.hostname} (${asset.ip}).`,
        status: 'info',
        iconName: 'globe',
      },
      {
        step: 2,
        id: 'stage_ingress',
        title: 'Exploit Delivery & Ingress',
        subtitle: `${cve} Payload Delivery`,
        actor: 'Crafted Inbound Traffic',
        target: `${asset.hostname} (${portUsed})`,
        protocol: portUsed,
        techniqueId: primaryTechId,
        techniqueName: primaryTechName,
        description:
          `Threat actor transmits crafted packets weaponizing ${cve} against ${softwareName}.`,
        status: 'critical',
        iconName: 'server',
      },
      {
        step: 3,
        id: 'stage_execution',
        title: 'Flaw Activation & Local Compromise',
        subtitle: `${vulnType}`,
        actor: 'Injected Code / Malicious Parser',
        target: `${asset.hostname} OS Context`,
        protocol: 'Process Execution',
        techniqueId: 'T1059',
        techniqueName: 'Command & Scripting Interpreter',
        description:
          `${executionDetail}. Adversary establishes local foothold on ${asset.hostname}.`,
        status: 'critical',
        iconName: 'terminal',
      },
      {
        step: 4,
        id: 'stage_propagation',
        title: 'Lateral Movement & Reconnaissance',
        subtitle: 'Internal Subnet Traversal',
        actor: `Compromised ${asset.hostname}`,
        target: 'Adjacent Subnet Hosts',
        protocol: 'Internal LAN / RPC / SMB',
        techniqueId: 'T1021',
        techniqueName: 'Remote Services',
        description:
          `Using ${asset.hostname} as a pivot point, the adversary probes adjacent internal servers for weak credentials and unpatched services.`,
        status: 'warning',
        iconName: 'alert',
      },
      {
        step: 5,
        id: 'stage_impact',
        title: 'Enterprise Impact & Objective',
        subtitle: 'Core Enterprise Data Threat',
        actor: 'Threat Actor',
        target: 'Enterprise Core Data Stores',
        protocol: 'Internal Data Extraction',
        techniqueId: 'T1486',
        techniqueName: 'Data Encrypted for Impact / Exfiltration',
        description:
          `Adversary executes primary breach objective, attempting to compromise sensitive customer records and core enterprise data stores.`,
        status: isCriticalAsset ? 'critical' : 'warning',
        iconName: 'database',
      },
    ],
  };
}
