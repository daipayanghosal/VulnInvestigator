import { Asset, FactorBreakdown, RiskBand, Vulnerability } from '../types';

export const WEIGHTS = {
  cvss: 0.35,
  kev: 0.30,
  asset_criticality: 0.20,
  exposure: 0.15,
};

export const CRITICALITY_MAP: Record<string, number> = {
  critical: 1.0,
  high: 0.75,
  medium: 0.50,
  low: 0.25,
  unknown: 0.10,
};

export const EXPOSURE_MAP: Record<string, number> = {
  internet_facing: 1.0,
  dmz: 0.75,
  internal: 0.50,
  restricted: 0.25,
  air_gapped: 0.0,
};

export function getRiskBand(score: number): RiskBand {
  if (score >= 0.80) return 'Critical';
  if (score >= 0.60) return 'High';
  if (score >= 0.40) return 'Medium';
  return 'Low';
}

export function calculateFactorBreakdown(
  cvssScore: number,
  inKev: boolean,
  asset: Asset
): FactorBreakdown {
  const cvss_val = Math.max(0, Math.min(10, cvssScore || 0));
  const cvss_norm = cvss_val / 10.0;
  const cvss_contrib = WEIGHTS.cvss * cvss_norm;

  const kev_contrib = inKev ? WEIGHTS.kev : 0.0;

  const crit_tier = (asset.criticality || 'medium').toLowerCase();
  const crit_score = CRITICALITY_MAP[crit_tier] ?? 0.50;
  const asset_contrib = WEIGHTS.asset_criticality * crit_score;

  const expo_tier = (asset.exposure || 'internal').toLowerCase();
  const expo_score = EXPOSURE_MAP[expo_tier] ?? 0.50;
  const expo_contrib = WEIGHTS.exposure * expo_score;

  const raw_total = cvss_contrib + kev_contrib + asset_contrib + expo_contrib;
  const total_score = Math.max(0, Math.min(1, Math.round(raw_total * 1000) / 1000));

  return {
    cvss_val,
    cvss_norm,
    cvss_contrib,
    in_kev: inKev,
    kev_contrib,
    crit_tier,
    crit_score,
    asset_contrib,
    expo_tier,
    expo_score,
    expo_contrib,
    total_score,
  };
}

export function generateExecutiveVerdict(
  cveId: string,
  breakdown: FactorBreakdown,
  asset: Asset,
  band: RiskBand,
  displacement: number
): { title: string; text: string; status: 'escalated' | 'de-escalated' | 'balanced' } {
  const { in_kev, cvss_val, total_score, crit_tier, expo_tier } = breakdown;
  const hostname = asset.hostname || 'target host';
  const absShift = Math.abs(displacement);

  if (in_kev && expo_tier.includes('internet')) {
    return {
      status: 'escalated',
      title: 'Active Exploitation Escalation Notice',
      text: `While generic vendor scoring rates this vulnerability at ${cvss_val.toFixed(1)}, static metrics dangerously overlook adversary behavior. CISA confirms this flaw is actively weaponized in the wild, and it directly affects an Internet-facing ${crit_tier} system (${hostname}). Our engine escalates this threat to ${total_score.toFixed(3)} (${band}), surging its remediation priority by ${absShift} positions to prevent an imminent enterprise breach.`,
    };
  } else if (!in_kev) {
    return {
      status: 'de-escalated',
      title: 'False Alarm Mitigation & Workload Preservation',
      text: `Standard scoring rates this flaw at a severe ${cvss_val.toFixed(1)}, treating it as a priority emergency in isolation. However, CISA confirms zero wild exploits observed across threat intelligence feeds. Because ${hostname} resides in an ${expo_tier} perimeter, true enterprise urgency decreases to ${total_score.toFixed(3)} (${band}), shifting it ${absShift} spots down the queue to avoid panic patching and preserve engineering bandwidth.`,
    };
  } else {
    return {
      status: 'balanced',
      title: 'Calibrated Multi-Factor Prioritization',
      text: `Standard technical severity (${cvss_val.toFixed(1)}) is balanced against observed exploit activity and the ${crit_tier} business function of ${hostname}. With an ${expo_tier} network posture, the calculated contextual score of ${total_score.toFixed(3)} (${band}) ensures proportionate defensive focus.`,
    };
  }
}
