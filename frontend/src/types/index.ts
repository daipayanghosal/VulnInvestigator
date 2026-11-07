export type RiskBand = 'Critical' | 'High' | 'Medium' | 'Low';
export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN';

export interface Vulnerability {
  cve_id: string;
  cvss_score: number;
  cvss_severity: Severity;
  cvss_vector?: string;
  in_kev: boolean;
  risk_score: number;
  risk_band: RiskBand;
  matched_asset_id: string;
  rank_cvss: number;
  rank_contextual: number;
  rank_displacement: number;
  description: string;
  affected_products?: string;
  published_date?: string;
}

export interface Asset {
  asset_id: string;
  hostname: string;
  ip: string;
  type: string;
  os: string;
  software: string | string[];
  criticality: 'critical' | 'high' | 'medium' | 'low';
  exposure: 'internet_facing' | 'dmz' | 'internal' | 'restricted' | 'air_gapped';
  owner?: string;
  tags?: string | string[];
  notes?: string;
}

export interface Technique {
  id: string;
  name: string;
  tactics: string;
  description: string;
}

export interface SecurityLog {
  event_id: string;
  timestamp: string;
  asset_id: string;
  source_ip: string;
  event_type: string;
  technique_id: string;
  description: string;
  raw_log: string;
  is_noise: boolean | number;
  cve_id?: string;
}

export interface FactorBreakdown {
  cvss_val: number;
  cvss_norm: number;
  cvss_contrib: number;
  in_kev: boolean;
  kev_contrib: number;
  crit_tier: string;
  crit_score: number;
  asset_contrib: number;
  expo_tier: string;
  expo_score: number;
  expo_contrib: number;
  total_score: number;
}

export interface InvestigationSection {
  title: string;
  content: string;
}

export interface InvestigationReport {
  cve_id: string;
  title: string;
  grounding_score: number;
  citations_found: number;
  unsupported_claims_count: number;
  citations: string[];
  sections: InvestigationSection[];
  unsupported_claims: string[];
  generated_at?: string;
  is_live?: boolean;
}

export interface EvaluationData {
  summary: {
    total_cves: number;
    in_kev: number;
    critical_risk: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
    has_cvss: number;
  };
  ranking_metrics: {
    kendall_tau: number;
    spearman_rho: number;
    ndcg_at_10: number;
    ndcg_at_20: number;
    min_displacement: number;
    max_displacement: number;
    mean_abs_displacement: number;
  };
  histogram_bins: Array<{
    bin_start: number;
    bin_end: number;
    bin_label: string;
    count: number;
    is_positive: boolean;
  }>;
  grounding_metrics: {
    evidence_citation_rate: number;
    claim_support_rate: number;
    hallucination_rate: number;
    mean_confidence_score: number;
    benchmark_scenarios_tested: number;
  };
  failure_modes: Array<{
    mode: string;
    status: string;
    test_input: string;
    expected: string;
    actual: string;
    coverage: string;
  }>;
  top_displacements: Array<{
    cve_id: string;
    cvss_score: number;
    cvss_rank: number;
    contextual_score: number;
    contextual_rank: number;
    displacement: number;
    justification: string;
  }>;
}
