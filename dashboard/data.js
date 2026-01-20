/* ========================================
   UIDAI Analytics Dashboard - Data
   Real data from analysis outputs
   ======================================== */

// KPI Data
const kpiData = {
    totalEnrolments: 5435702,
    totalDemoUpdates: 49295187,
    totalBioUpdates: 69763095,
    totalUpdates: 119058282,
    updateToEnrolRatio: 21.90,
    avgDemoIntensity: 6.10,
    avgBioIntensity: 10.31,
    avgChildAttentionGap: -0.228,
    statesAnalyzed: 54,
    districtsAnalyzed: 1041,
    matureRegionsPct: 1.56,
    underservedRegionsPct: 22.84
};

// State Summary Data (Top 20 states)
const stateData = [
    { state: "Uttar Pradesh", enrol: 1018629, demo: 8542328, bio: 9577735, total: 18120063, childGap: -0.259, intensity: 17.79 },
    { state: "Bihar", enrol: 609585, demo: 4814350, bio: 4897587, total: 9711937, childGap: -0.390, intensity: 15.93 },
    { state: "Madhya Pradesh", enrol: 493970, demo: 2912938, bio: 5923771, total: 8836709, childGap: -0.233, intensity: 17.89 },
    { state: "West Bengal", enrol: 375308, demo: 3872318, bio: 2524506, total: 6396824, childGap: -0.325, intensity: 17.04 },
    { state: "Maharashtra", enrol: 369139, demo: 5054602, bio: 9226139, total: 14280741, childGap: -0.385, intensity: 38.69 },
    { state: "Rajasthan", enrol: 348458, demo: 2817615, bio: 3994955, total: 6812570, childGap: -0.269, intensity: 19.55 },
    { state: "Gujarat", enrol: 280549, demo: 1824327, bio: 3196514, total: 5020841, childGap: -0.385, intensity: 17.90 },
    { state: "Assam", enrol: 230197, demo: 1012578, bio: 982722, total: 1995300, childGap: -0.346, intensity: 8.67 },
    { state: "Karnataka", enrol: 223235, demo: 1695285, bio: 2635954, total: 4331239, childGap: -0.146, intensity: 19.40 },
    { state: "Tamil Nadu", enrol: 220789, demo: 2212228, bio: 4698117, total: 6910345, childGap: -0.114, intensity: 31.30 },
    { state: "Jharkhand", enrol: 157539, demo: 1401189, bio: 2026297, total: 3427486, childGap: -0.244, intensity: 21.76 },
    { state: "Telangana", enrol: 131574, demo: 1629908, bio: 1737654, total: 3367562, childGap: -0.149, intensity: 25.59 },
    { state: "Andhra Pradesh", enrol: 127686, demo: 2295582, bio: 3714633, total: 6010215, childGap: -0.121, intensity: 47.07 },
    { state: "Odisha", enrol: 122987, demo: 1112065, bio: 2464960, total: 3577025, childGap: -0.083, intensity: 29.08 },
    { state: "Meghalaya", enrol: 109771, demo: 87378, bio: 87626, total: 175004, childGap: -0.266, intensity: 1.59 },
    { state: "Chhattisgarh", enrol: 103219, demo: 2005434, bio: 2648729, total: 4654163, childGap: -0.307, intensity: 45.09 },
    { state: "Haryana", enrol: 98252, demo: 1166140, bio: 1635454, total: 2801594, childGap: -0.241, intensity: 28.51 },
    { state: "Delhi", enrol: 94529, demo: 1438934, bio: 1304362, total: 2743296, childGap: -0.479, intensity: 29.02 },
    { state: "Punjab", enrol: 76746, demo: 881895, bio: 1739671, total: 2621566, childGap: -0.260, intensity: 34.16 },
    { state: "Kerala", enrol: 75002, demo: 744952, bio: 1609730, total: 2354682, childGap: -0.182, intensity: 31.39 }
];

// Monthly Trend Data (Simulated based on patterns observed)
const monthlyData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    demographic: [4.2, 4.8, 1.2, 3.9, 4.1, 4.3, 4.0, 4.5, 4.8, 4.2, 5.2, 4.1],
    biometric: [5.8, 6.2, 2.1, 5.5, 5.9, 6.1, 5.7, 6.3, 7.2, 6.0, 6.8, 5.7]
};

// Critical Districts Data (Top 20)
const criticalDistricts = [
    { rank: 1, state: "Delhi", district: "North East", gap: -0.9999, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 2, state: "Haryana", district: "Jhajjar", gap: -0.9999, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 3, state: "Odisha", district: "Kendrapara", gap: -0.9999, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 4, state: "Tamil Nadu", district: "Namakkal", gap: -0.9999, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 5, state: "Uttar Pradesh", district: "Kushi Nagar", gap: -0.9911, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 6, state: "Maharashtra", district: "Nandurbar", gap: -0.9876, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 7, state: "Bihar", district: "Sheikpura", gap: -0.9836, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 8, state: "Bihar", district: "Monghyr", gap: -0.9821, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 9, state: "Maharashtra", district: "Raigarh(Mh)", gap: -0.9735, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 10, state: "Odisha", district: "Nabarangpur", gap: -0.9729, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 11, state: "Haryana", district: "Nuh", gap: -0.9721, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 12, state: "Uttar Pradesh", district: "Jyotiba Phule Nagar", gap: -0.9710, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 13, state: "Madhya Pradesh", district: "Ashoknagar", gap: -0.9702, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 14, state: "Uttar Pradesh", district: "Siddharth Nagar", gap: -0.9670, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 15, state: "West Bengal", district: "Dinajpur Dakshin", gap: -0.9659, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 16, state: "Telangana", district: "Ranga Reddy", gap: -0.9648, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 17, state: "Bihar", district: "Samstipur", gap: -0.9645, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 18, state: "Jharkhand", district: "East Singhbum", gap: -0.9634, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 19, state: "Maharashtra", district: "Gondia", gap: -0.9622, severity: "Critical", recommendation: "Increase child update campaigns" },
    { rank: 20, state: "Chhattisgarh", district: "Janjgir - Champa", gap: -0.9619, severity: "Critical", recommendation: "Increase child update campaigns" }
];

// Cluster Data
const clusterData = {
    labels: ['Cluster 0\nEnrolment Frontiers', 'Cluster 1-2\nMature Systems', 'Cluster 3\nHigh Verification', 'Cluster 4\nDormant'],
    values: [80, 560, 200, 60],
    colors: ['#1e88e5', '#43a047', '#fb8c00', '#e53935']
};

// Metric Details
const metricDetails = {
    enrolments: {
        title: "Total Enrolments",
        value: "5,435,702",
        description: "New Aadhaar enrolments during the 12-month observation period.",
        breakdown: [
            { label: "Uttar Pradesh", value: "1,018,629 (18.7%)" },
            { label: "Bihar", value: "609,585 (11.2%)" },
            { label: "Madhya Pradesh", value: "493,970 (9.1%)" },
            { label: "West Bengal", value: "375,308 (6.9%)" },
            { label: "Others", value: "2,938,210 (54.1%)" }
        ]
    },
    updates: {
        title: "Total Updates",
        value: "119,058,282",
        description: "Combined demographic and biometric updates during the observation period.",
        breakdown: [
            { label: "Demographic Updates", value: "49,295,187 (41.4%)" },
            { label: "Biometric Updates", value: "69,763,095 (58.6%)" }
        ]
    },
    demographic: {
        title: "Demographic Updates",
        value: "49,295,187",
        description: "Name, address, and contact information corrections.",
        breakdown: [
            { label: "Uttar Pradesh", value: "8,542,328 (17.3%)" },
            { label: "Maharashtra", value: "5,054,602 (10.3%)" },
            { label: "Bihar", value: "4,814,350 (9.8%)" },
            { label: "West Bengal", value: "3,872,318 (7.9%)" },
            { label: "Others", value: "27,011,589 (54.7%)" }
        ]
    },
    biometric: {
        title: "Biometric Updates",
        value: "69,763,095",
        description: "Fingerprint, iris, and photograph refresh transactions.",
        breakdown: [
            { label: "Uttar Pradesh", value: "9,577,735 (13.7%)" },
            { label: "Maharashtra", value: "9,226,139 (13.2%)" },
            { label: "Madhya Pradesh", value: "5,923,771 (8.5%)" },
            { label: "Bihar", value: "4,897,587 (7.0%)" },
            { label: "Others", value: "40,137,863 (57.6%)" }
        ]
    },
    states: {
        title: "States Analyzed",
        value: "54",
        description: "Total number of states and union territories in the analysis.",
        breakdown: [
            { label: "Major States", value: "28" },
            { label: "Union Territories", value: "8" },
            { label: "Special Regions", value: "18" }
        ]
    },
    districts: {
        title: "Districts Analyzed",
        value: "1,041",
        description: "Total number of districts covered in the analysis.",
        breakdown: [
            { label: "High Activity", value: "~450 districts" },
            { label: "Moderate Activity", value: "~400 districts" },
            { label: "Low Activity", value: "~190 districts" }
        ]
    },
    childgap: {
        title: "Average Child Attention Gap",
        value: "-22.8%",
        description: "Average difference between child share in enrolments vs updates. Negative values indicate under-representation.",
        breakdown: [
            { label: "Best (Odisha)", value: "-8.3%" },
            { label: "Worst (Delhi)", value: "-47.9%" },
            { label: "Critical Districts", value: "20+" }
        ]
    },
    underserved: {
        title: "Underserved Regions",
        value: "22.8%",
        description: "Percentage of districts classified as underserved based on update intensity and coverage.",
        breakdown: [
            { label: "Underserved Districts", value: "~238 districts" },
            { label: "States Affected", value: "42 states" },
            { label: "Priority for Intervention", value: "High" }
        ]
    }
};

// Export data for use in other scripts
window.dashboardData = {
    kpi: kpiData,
    states: stateData,
    monthly: monthlyData,
    critical: criticalDistricts,
    clusters: clusterData,
    metricDetails: metricDetails
};
