/**
 * frontend/src/utils/propagation.ts
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * Computes audience-specific vulnerability explanations and multi-stage
 * attack propagation models for both Executive leadership and Technical security responders.
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
  asset: Asset
): VulnerabilityPropagationProfile {
  const desc = (vuln.description || '').toLowerCase();
  const cve = vuln.cve_id.toUpperCase();
  const isKev = Boolean(vuln.in_kev);
  const isInternetFacing = asset.exposure === 'internet_facing';
  const isCriticalAsset = asset.criticality === 'critical';

  // Specific profile for Log4Shell (CVE-2021-44228)
  if (cve.includes('2021-44228') || desc.includes('log4j') || desc.includes('jndi')) {
    return {
      vulnType: 'Remote Code Execution via JNDI Injection',
      cweLabel: 'CWE-502 / CWE-917 (Deserialization of Untrusted Data & Expression Injection)',
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
          id: 'weaponization',
          title: 'External Weaponization',
          subtitle: 'Reconnaissance & Payload Formulation',
          actor: 'Remote Threat Actor',
          target: 'Internet Perimeter',
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
          id: 'perimeter_ingress',
          title: 'Perimeter Ingress',
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
          id: 'outbound_callback',
          title: 'Outbound Callback & Deserialization',
          subtitle: 'Egress Payload Fetch',
          actor: `Compromised ${asset.hostname}`,
          target: 'Attacker Directory Server (198.51.100.44)',
          protocol: 'LDAP / RMI (Port 1389/389)',
          techniqueId: 'T1071.001',
          techniqueName: 'Application Layer Protocol: Web Protocols',
          description:
            'Target server reaches out through perimeter firewall to attacker LDAP server and downloads compiled malicious Java bytecode.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'local_execution',
          title: 'Remote Code Execution',
          subtitle: 'Shell Access & Local Privilege',
          actor: 'Injected Payload',
          target: `${asset.hostname} OS Process`,
          protocol: 'System Subshell (/bin/sh)',
          techniqueId: 'T1059.004',
          techniqueName: 'Unix Shell Execution',
          description:
            'Bytecode executes within Java VM context, spawning interactive subshell and harvesting local environment variables and credentials.',
          status: 'critical',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'lateral_propagation',
          title: 'Lateral Movement & Enterprise Impact',
          subtitle: 'Internal Pivoting & Data Store Threat',
          actor: 'Attacker Foothold',
          target: 'Enterprise Core DB & Active Directory',
          protocol: 'Internal RPC / SQL (VLAN 20)',
          techniqueId: 'T1021.002',
          techniqueName: 'Remote Services: SMB/Windows Admin Shares',
          description:
            'Attacker leverages harvested credentials from reverse-proxy to probe internal cluster databases and initiate ransomware staging.',
          status: 'warning',
          iconName: 'database',
        },
      ],
    };
  }

  // Specific profile for Citrix ADC / Bleed (CVE-2023-3519 / CVE-2023-4966)
  if (cve.includes('2023-3519') || cve.includes('2023-4966') || desc.includes('netscaler') || desc.includes('citrix')) {
    return {
      vulnType: 'Memory Buffer Overflow & Gateway Authentication Bypass',
      cweLabel: 'CWE-119 / CWE-287 (Improper Restriction of Operations within Bounds & Improper Authentication)',
      executiveBrief: {
        headline: `Perimeter gateway authentication bypass exposing corporate VPN and remote access infrastructure`,
        businessImpact:
          'Direct breach of primary corporate gateway allowing adversaries to hijack active authenticated executive sessions without supplying multi-factor credentials.',
        blastRadius:
          'Critical Perimeter Compromise: Acts as the primary border gateway; compromise completely bypasses perimeter perimeter defenses.',
        urgencyRationale:
          'Documented by CISA and NSA as actively leveraged for nation-state corporate espionage and initial ransomware broker access.',
        executiveAction:
          'Authorize immediate reboot into patched firmware, terminate all active Citrix gateway sessions, and rotate enterprise Kerberos/SAML tokens.',
        financialRiskLevel: 'Critical',
        regulatoryImpact: 'Critical compliance exposure under SOC 2, ISO 27001, and HIPAA access control mandates.',
      },
      technicalDeepDive: {
        rootCause:
          'Unauthenticated stack buffer overflow in nsppe packet processing engine triggered via crafted HTTP GET/POST requests to /vpn/ endpoints.',
        protocolVector: 'Direct HTTPS requests to VPN / AAA authentication endpoints.',
        propagationMechanism:
          'Memory leak allows extraction of active session tokens (cookies); attacker replay session tokens to impersonate valid users and establish persistent reverse shells.',
        detectionSignatures: [
          'NetScaler ns.log: Segmentation faults or abnormal child process termination in nsppe process.',
          'Web access logs: Anomalous HTTP requests targeting /vpn/../vpns/cfg/smb.conf or oversized cookie headers.',
          'Filesystem anomalies: Suspicious .sh or .php webshell files located in /var/vpn/netscaler/ or /netscaler/ns_gui/.',
        ],
        containmentControls: [
          'Upgrade NetScaler ADC and Gateway to patched build recommended in Citrix security bulletin.',
          'Enforce strict IP access control lists (ACLs) on administrative management interfaces (NSIP).',
          'Invalidate all active session cookies and force complete enterprise session termination.',
        ],
        vlanExposure: 'External Gateway DMZ -> Direct access to Internal Corporate Subnets (VLAN 1 -> VLAN 100)',
      },
      stages: [
        {
          step: 1,
          id: 'weaponization',
          title: 'Perimeter Reconnaissance',
          subtitle: 'Gateway Version Fingerprinting',
          actor: 'Remote Threat Actor',
          target: `${asset.hostname} VPN Portal`,
          protocol: 'HTTPS (Port 443)',
          techniqueId: 'T1190',
          techniqueName: 'Exploit Public-Facing Application',
          description:
            'Attacker probes public SSL-VPN endpoint to fingerprint vulnerable NetScaler build.',
          status: 'warning',
          iconName: 'globe',
        },
        {
          step: 2,
          id: 'auth_bypass',
          title: 'Memory Leak & Token Theft',
          subtitle: 'Buffer Overread Exploitation',
          actor: 'Crafted Request',
          target: `${asset.hostname} NSPPE Engine`,
          protocol: 'HTTP OpenSSL Request',
          techniqueId: 'T1552.001',
          techniqueName: 'Unsecured Credentials: Credentials In Files',
          description:
            'Malformed request triggers memory buffer overread, dumping active session cookies and SAML tokens without authentication.',
          status: 'critical',
          iconName: 'server',
        },
        {
          step: 3,
          id: 'session_hijack',
          title: 'Session Hijack & Access',
          subtitle: 'MFA Bypass & Entry',
          actor: 'Attacker Replay',
          target: 'Corporate VPN Gateway',
          protocol: 'Authenticated Session Tunnel',
          techniqueId: 'T1556',
          techniqueName: 'Modify Authentication Process',
          description:
            'Attacker replays stolen session token to establish a fully authenticated tunnel into internal infrastructure, bypassing MFA.',
          status: 'critical',
          iconName: 'terminal',
        },
        {
          step: 4,
          id: 'webshell_drop',
          title: 'Persistence & Webshell Drop',
          subtitle: 'Command Injection',
          actor: 'Admin Session',
          target: `${asset.hostname} File System`,
          protocol: 'Local Script Engine',
          techniqueId: 'T1505.003',
          techniqueName: 'Server Software Component: Web Shell',
          description:
            'Payload writes a lightweight backdoor shell into web directory to survive appliance reboots and maintain long-term presence.',
          status: 'critical',
          iconName: 'alert',
        },
        {
          step: 5,
          id: 'internal_pivot',
          title: 'Internal Network Infiltration',
          subtitle: 'Corporate LAN Traversal',
          actor: 'Internal VPN Tunnel',
          target: 'Internal Domain Controllers & Financial Systems',
          protocol: 'RDP / SMB / Kerberos',
          techniqueId: 'T1021.001',
          techniqueName: 'Remote Desktop Protocol',
          description:
            'Using the gateway as a pivot point, the attacker initiates reconnaissance and brute force against internal domain controllers.',
          status: 'warning',
          iconName: 'database',
        },
      ],
    };
  }

  // Heuristic Synthesis for all other CVEs based on CVSS metrics, description, and asset coordinates
  let vulnType = 'System Vulnerability & Exploit Path';
  let cweLabel = 'CWE-Unknown (Software Flaw)';
  let primaryTechniqueId = 'T1190';
  let primaryTechniqueName = 'Exploit Public-Facing Application';

  if (desc.includes('remote code execution') || desc.includes('rce') || desc.includes('execute arbitrary code')) {
    vulnType = 'Remote Code Execution (RCE)';
    cweLabel = 'CWE-94 / CWE-78 (Improper Control of Generation of Code / OS Command Injection)';
    primaryTechniqueId = 'T1203';
    primaryTechniqueName = 'Exploitation for Client/Server Execution';
  } else if (desc.includes('buffer overflow') || desc.includes('memory corruption') || desc.includes('out-of-bounds')) {
    vulnType = 'Memory Corruption / Buffer Overflow';
    cweLabel = 'CWE-119 / CWE-120 (Buffer Errors & Memory Boundary Overwrite)';
    primaryTechniqueId = 'T1190';
    primaryTechniqueName = 'Exploit Public-Facing Application';
  } else if (desc.includes('sql injection') || desc.includes('sqli')) {
    vulnType = 'SQL Injection (Data Exfiltration & Tampering)';
    cweLabel = 'CWE-89 (Improper Neutralization of Special Elements used in an SQL Command)';
    primaryTechniqueId = 'T1190';
    primaryTechniqueName = 'Exploit Public-Facing Application';
  } else if (desc.includes('cross-site scripting') || desc.includes('xss')) {
    vulnType = 'Cross-Site Scripting (XSS)';
    cweLabel = 'CWE-79 (Improper Neutralization of Input During Web Page Generation)';
    primaryTechniqueId = 'T1189';
    primaryTechniqueName = 'Drive-by Compromise';
  } else if (desc.includes('privilege escalation') || desc.includes('elevation of privilege')) {
    vulnType = 'Local Privilege Escalation (LPE)';
    cweLabel = 'CWE-269 (Improper Privilege Management)';
    primaryTechniqueId = 'T1068';
    primaryTechniqueName = 'Exploitation for Privilege Escalation';
  } else if (desc.includes('denial of service') || desc.includes('dos') || desc.includes('crash')) {
    vulnType = 'Denial of Service (DoS)';
    cweLabel = 'CWE-400 (Uncontrolled Resource Consumption)';
    primaryTechniqueId = 'T1499';
    primaryTechniqueName = 'Endpoint Denial of Service';
  } else if (desc.includes('authentication bypass') || desc.includes('bypass security') || desc.includes('authorization')) {
    vulnType = 'Authentication Bypass / Security Misconfiguration';
    cweLabel = 'CWE-287 / CWE-306 (Improper Authentication)';
    primaryTechniqueId = 'T1556';
    primaryTechniqueName = 'Modify Authentication Process';
  }

  const financialRiskLevel =
    isCriticalAsset && isKev ? 'Critical' : isCriticalAsset || isKev ? 'High' : 'Moderate';

  return {
    vulnType,
    cweLabel,
    executiveBrief: {
      headline: `${vulnType} flaw affecting ${asset.hostname} (${asset.ip})`,
      businessImpact: isCriticalAsset
        ? `Threat actors compromising this host can directly disrupt mission-critical ${asset.notes || 'core business systems'}, leading to operational downtime and data integrity compromise.`
        : `Compromise introduces unauthorized system control, which attackers can leverage as a pivot point toward higher-tier assets.`,
      blastRadius: isInternetFacing
        ? `External Perimeter Risk: Internet accessibility allows opportunistic threat actors to discover and trigger the flaw without internal credentials.`
        : `Internal Network Risk: Requires internal network access or previous workstation compromise to exploit.`,
      urgencyRationale: isKev
        ? `Documented in CISA KEV as actively weaponized in real-world attacks. Poses immediate exploitation threat.`
        : `Standard CVSS ${vuln.cvss_score.toFixed(1)} rating. Prioritize based on operational criticality of ${asset.hostname}.`,
      executiveAction:
        isCriticalAsset || isKev
          ? `Deploy high-priority security mitigation within 24 hours. Validate firewall isolation and review recent host telemetry logs.`
          : `Schedule remediation in standard weekly patch cycle. Ensure monitoring rules flag abnormal outbound traffic.`,
      financialRiskLevel,
      regulatoryImpact: isCriticalAsset
        ? 'High audit visibility; potential SLA non-compliance if core services undergo disruption.'
        : 'Standard compliance reporting required under annual vulnerability management policy.',
    },
    technicalDeepDive: {
      rootCause:
        vuln.description || 'Specific protocol logic flaw identified in vendor software component.',
      protocolVector: isInternetFacing
        ? `Inbound external network packets directed to ${asset.ip} on listening application ports.`
        : `Internal TCP/UDP protocol connection within local subnet segment.`,
      propagationMechanism:
        'Following initial exploit trigger on the host, the threat actor attempts privilege elevation, dumps local process memory or credentials, and scans adjacent IP ranges for unpatched services.',
      detectionSignatures: [
        `SIEM Telemetry: Correlate unexpected connections targeting ${asset.ip} from external IP addresses.`,
        `Host Intrusion Detection: Watch for unexpected parent-child process trees or modified binary hashes.`,
        `Network Flow: Spike in outbound connection attempts on non-standard ports or lateral SMB/RPC sweeps.`,
      ],
      containmentControls: [
        `Host Isolation: Apply network segmentation rule to limit ${asset.hostname} communication to strictly necessary peers.`,
        `Vendor Patch: Upgrade affected package (${Array.isArray(asset.software) ? asset.software[0] : 'installed package'}) to patched release.`,
        `Credential Invalidation: If unauthenticated execution occurred, cycle local service accounts and API credentials.`,
      ],
      vlanExposure: isInternetFacing
        ? `Perimeter Ingress -> Lateral Pivot Risk across internal network (${asset.ip})`
        : `Internal Workstation / Server Subnet (${asset.ip})`,
    },
    stages: [
      {
        step: 1,
        id: 'stage_recon',
        title: 'Adversary Reconnaissance & Scanning',
        subtitle: 'Asset Discovery',
        actor: 'External Threat Actor',
        target: `${asset.hostname} (${asset.ip})`,
        protocol: isInternetFacing ? 'Internet Scanning (TCP)' : 'Internal Subnet Discovery',
        techniqueId: 'T1046',
        techniqueName: 'Network Service Discovery',
        description:
          'Attacker scans network boundaries to discover exposed software versions and open listening ports.',
        status: 'info',
        iconName: 'globe',
      },
      {
        step: 2,
        id: 'stage_ingress',
        title: 'Exploit Delivery & Trigger',
        subtitle: `Attack Vector on ${asset.hostname}`,
        actor: 'Malicious Payload',
        target: `${asset.hostname} Port`,
        protocol: 'Application Protocol',
        techniqueId: primaryTechniqueId,
        techniqueName: primaryTechniqueName,
        description:
          `Attacker sends crafted exploit payload triggering the ${vulnType} vulnerability.`,
        status: 'critical',
        iconName: 'server',
      },
      {
        step: 3,
        id: 'stage_execution',
        title: 'Local Execution & Compromise',
        subtitle: 'System Control',
        actor: 'Injected Code / Subprocess',
        target: `${asset.hostname} Memory/OS`,
        protocol: 'Process Execution',
        techniqueId: 'T1059',
        techniqueName: 'Command & Scripting Interpreter',
        description:
          'Exploit achieves unauthorized code execution or alters access controls, granting initial local system foothold.',
        status: 'critical',
        iconName: 'terminal',
      },
      {
        step: 4,
        id: 'stage_propagation',
        title: 'Lateral Movement & Reconnaissance',
        subtitle: 'Subnet Traversal',
        actor: `Compromised ${asset.hostname}`,
        target: 'Adjacent Subnet Hosts',
        protocol: 'Internal LAN / RPC / SMB',
        techniqueId: 'T1021',
        techniqueName: 'Remote Services',
        description:
          'Adversary leverages the compromised host to scan adjacent internal systems, seeking to pivot toward high-value corporate targets.',
        status: 'warning',
        iconName: 'alert',
      },
      {
        step: 5,
        id: 'stage_impact',
        title: 'Impact & Business Objective',
        subtitle: 'Data & Service Threat',
        actor: 'Threat Actor',
        target: 'Enterprise Core Data Stores',
        protocol: 'Database / File Exfiltration',
        techniqueId: 'T1486',
        techniqueName: 'Data Encrypted for Impact / Exfiltration',
        description:
          'Adversary executes primary objective: exfiltrating sensitive business data or staging destructive ransomware payloads.',
        status: isCriticalAsset ? 'critical' : 'warning',
        iconName: 'database',
      },
    ],
  };
}
