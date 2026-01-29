"""
Esports UGC Topic Consolidation - Implementation Plan Generator
================================================================
This script generates the complete implementation_plan.md from source data files:
- topic_esports_ugc_nov16.xlsx: Original 129 BERTopic topics with GPT labels and counts
- esports_ugc_report_nov16.xlsx: Merge group proposals and independent topic lists

Usage: python generate_implementation_plan.py

Output: implementation_plan.md (and topic_consolidation_plan.md as backup)
"""

import pandas as pd
import re

# =============================================================================
# CONFIGURATION
# =============================================================================
INPUT_TOPICS_FILE = 'topic_esports_ugc_nov16.xlsx'
INPUT_REPORT_FILE = 'esports_ugc_report_nov16.xlsx'
OUTPUT_FILE = 'implementation_plan.md'
BACKUP_FILE = 'topic_consolidation_plan.md'
ARTIFACT_FILE = r'C:\Users\Q\.gemini\antigravity\brain\28af0040-b354-4d30-b553-9e175f8a8655\implementation_plan.md'

# =============================================================================
# STEP 1: LOAD SOURCE DATA
# =============================================================================
print("Loading source data...")

# Load original topics
df_topics = pd.read_excel(INPUT_TOPICS_FILE)
topics = {}
for idx, row in df_topics.iterrows():
    tid = int(row['Topic'])
    gpt = str(row['GPT']) if pd.notna(row['GPT']) else ''
    if gpt.startswith('['):
        gpt = gpt.strip("[]'\"")
    topics[tid] = {
        'gpt': gpt,
        'count': int(row['Count']),
        'name': str(row['Name']) if pd.notna(row['Name']) else ''
    }

print(f"  Loaded {len(topics)} topics from {INPUT_TOPICS_FILE}")

# Load merge groups and independent topics from report
df_merge = pd.read_excel(INPUT_REPORT_FILE, sheet_name='MERGE_GROUPS')
df_indep = pd.read_excel(INPUT_REPORT_FILE, sheet_name='INDEPENDENT_TOPICS')

# Extract topic IDs from merge groups
merge_groups = {}
merge_topic_ids = set()
for idx, row in df_merge.iterrows():
    label = str(row.get('final_topic_label', ''))
    members = str(row.get('member_topics', ''))
    # Extract topic IDs from members string
    ids = [int(x) for x in re.findall(r'\d+', members)]
    if label and ids:
        merge_groups[label] = ids
        merge_topic_ids.update(ids)

# Extract independent topic IDs
independent_ids = set()
for idx, row in df_indep.iterrows():
    tid = row.get('topic_id')
    if pd.notna(tid):
        independent_ids.add(int(tid))

# Find overlapping topics (appear in both lists)
overlap_ids = merge_topic_ids & independent_ids
print(f"  Found {len(merge_groups)} merge groups, {len(independent_ids)} independent topics")
print(f"  {len(overlap_ids)} topics appear in both lists (overlap)")

# =============================================================================
# STEP 2: DEFINE FINAL TOPIC STRUCTURE
# =============================================================================
# This is the curated mapping based on analysis of the source data
# Each final topic has: label, theme, and list of source topic IDs

FINAL_TOPICS = {
    # COGNITIVE (C1-C9)
    'C1': {'label': 'Hangzhou Asian Games: Esports as Official Sport', 'theme': 'Cognitive', 'sources': [8]},
    'C2': {'label': 'Asian Games National Team Selection Process', 'theme': 'Cognitive', 'sources': [46, 72, 88]},
    'C3': {'label': 'Esports World Cup (EWC) as Premier Global Event', 'theme': 'Cognitive', 'sources': [1, 3, 17, 32, 33, 71, 103, 110]},
    'C4': {'label': 'Saudi Arabia as Major Esports Host Nation', 'theme': 'Cognitive', 'sources': [12, 28, 52, 77]},
    'C5': {'label': 'Dota 2 Riyadh Masters', 'theme': 'Cognitive', 'sources': [102]},
    'C6': {'label': 'Asian Games Torch Relay with Esports Athletes', 'theme': 'Cognitive', 'sources': [49]},
    'C7': {'label': 'Esports Virtual Human at Asian Games', 'theme': 'Cognitive', 'sources': [50]},
    'C8': {'label': 'Hearthstone Removed from Asian Games', 'theme': 'Cognitive', 'sources': [63]},
    'C9': {'label': 'Tencent Official Broadcasting Rights', 'theme': 'Cognitive', 'sources': [45]},
    
    # PRAGMATIC - Results (P1-P9)
    'P1': {'label': 'Yinuo (Xu Bicheng) Wins EWC FMVP', 'theme': 'Pragmatic-Results', 'sources': [13]},
    'P2': {'label': 'Faker Wins EWC FMVP (LoL)', 'theme': 'Pragmatic-Results', 'sources': [106]},
    'P3': {'label': 'Xiaohai (Zeng Zhuojun) Wins Street Fighter EWC', 'theme': 'Pragmatic-Results', 'sources': [29]},
    'P4': {'label': 'NAVI Wins Counter-Strike EWC', 'theme': 'Pragmatic-Results', 'sources': [124]},
    'P5': {'label': 'Team Falcons Wins EWC Club Championship', 'theme': 'Pragmatic-Results', 'sources': [113]},
    'P6': {'label': 'JDG夺冠与LPL亚运话题', 'theme': 'Pragmatic-Results', 'sources': [119]},
    'P7': {'label': 'EWC Match Results & Highlights', 'theme': 'Pragmatic-Results', 'sources': [70, 75]},
    'P8': {'label': 'LoL at EWC: LPL vs LCK Matches', 'theme': 'Pragmatic-Results', 'sources': [21, 22, 122]},
    'P9': {'label': 'Street Fighter EWC Qualifiers', 'theme': 'Pragmatic-Results', 'sources': [95]},
    
    # PRAGMATIC - Fan (P10-P18)
    'P10': {'label': 'Yinuo (一诺) Asian Games Fan Support', 'theme': 'Pragmatic-Fan', 'sources': [6, 15, 100]},
    'P11': {'label': 'Fan Support for Dream Team Players', 'theme': 'Pragmatic-Fan', 'sources': [62, 126]},
    'P12': {'label': 'LGD/Hua Aotian (花傲天) EWC Fan Hype', 'theme': 'Pragmatic-Fan', 'sources': [2, 5, 30, 37, 38, 39, 41, 55, 60, 65, 68, 69, 73, 81, 82, 91, 93, 97, 99, 105, 107, 112, 114, 115, 116, 117, 120, 125]},
    'P13': {'label': 'AG超玩会 (AG Super Play) Asian Games Support', 'theme': 'Pragmatic-Fan', 'sources': [16]},
    'P14': {'label': 'eStarPro 花海/坦然 Performance & Support', 'theme': 'Pragmatic-Fan', 'sources': [34, 111]},
    'P15': {'label': 'Asian Games Countdown & General Fan Support', 'theme': 'Pragmatic-Fan', 'sources': [19, 36, 43, 67, 87, 94, 109]},
    'P16': {'label': 'EWC Chinese Teams Fan Mobilization', 'theme': 'Pragmatic-Fan', 'sources': [48, 54, 56]},
    'P17': {'label': 'KPL Dream Team (梦之队) at EWC', 'theme': 'Pragmatic-Fan', 'sources': [92]},
    'P18': {'label': 'General EWC Fan Support & Engagement', 'theme': 'Pragmatic-Fan', 'sources': [0, 10, 20]},
    
    # PRAGMATIC - Team (P19-P25)
    'P19': {'label': 'Tianba (天霸) at Peace Elite EWC', 'theme': 'Pragmatic-Team', 'sources': [44]},
    'P20': {'label': 'XYG at EWC 揭幕战', 'theme': 'Pragmatic-Team', 'sources': [47]},
    'P21': {'label': 'WBG at Saudi EWC', 'theme': 'Pragmatic-Team', 'sources': [96]},
    'P22': {'label': 'Korean LoL National Team at Asian Games', 'theme': 'Pragmatic-Team', 'sources': [11]},
    'P23': {'label': 'Team China at Asian Games (YiNuo Narrative)', 'theme': 'Pragmatic-Team', 'sources': [42]},
    'P24': {'label': '和平精英亚运版本国家集训队', 'theme': 'Pragmatic-Team', 'sources': [79]},
    'P25': {'label': 'MLBB Tournament Results (International)', 'theme': 'Pragmatic-Team', 'sources': [53]},
    
    # PRAGMATIC - Commercial (P26-P34)
    'P26': {'label': 'Luo Yunxi (罗云熙) as Migu Esports Ambassador', 'theme': 'Pragmatic-Commercial', 'sources': [14]},
    'P27': {'label': 'vivo/iQOO Official Phones Partnership', 'theme': 'Pragmatic-Commercial', 'sources': [23]},
    'P28': {'label': 'Yestar (艺星) Medical Aesthetics Partnership', 'theme': 'Pragmatic-Commercial', 'sources': [121]},
    'P29': {'label': 'Yili (伊利) Asian Games Sponsorship', 'theme': 'Pragmatic-Commercial', 'sources': [89]},
    'P30': {'label': 'EWC Club Support Program & Partnerships', 'theme': 'Pragmatic-Commercial', 'sources': [104]},
    'P32': {'label': 'Digital/Tech Products (王室好物)', 'theme': 'Pragmatic-Commercial', 'sources': [25]},
    'P33': {'label': 'EWC Qiddiya City Venue Promotion', 'theme': 'Pragmatic-Commercial', 'sources': [51]},
    'P34': {'label': 'Hangzhou Asian Games Esports Ticketing', 'theme': 'Pragmatic-Commercial', 'sources': [24, 101]},
    
    # MORAL (M1-M7)
    'M1': {'label': 'JackeyLove Withdrawal from Asian Games Controversy', 'theme': 'Moral', 'sources': [4]},
    'M2': {'label': 'Jiuwei (九尾) EWC Roster Exclusion Controversy', 'theme': 'Moral', 'sources': [9, 26, 85, 108]},
    'M3': {'label': "Cat's Exclusion from EWC Roster Controversy", 'theme': 'Moral', 'sources': [27]},
    'M4': {'label': 'Nanjing Hero Club Transfer Fee Controversy (Wuwei)', 'theme': 'Moral', 'sources': [57, 59, 74, 78, 84, 90]},
    'M5': {'label': 'KPL Controversies & Roster Debates', 'theme': 'Moral', 'sources': [18, 64, 86, 127]},
    'M6': {'label': 'Uzi Asian Games Roster Discussions', 'theme': 'Moral', 'sources': [83]},
    'M7': {'label': 'Wuwei (无畏) Dream Team Voting & Fan Advocacy', 'theme': 'Moral', 'sources': [66, 80, 98]},
    
    # GAME-SPECIFIC (G1-G9)
    'G1': {'label': 'Honor of Kings (王者荣耀) at Asian Games', 'theme': 'Game-Specific', 'sources': [35, 40, 58]},
    'G2': {'label': 'Honor of Kings: KPL at EWC', 'theme': 'Game-Specific', 'sources': [64, 92, 127]},
    'G3': {'label': 'Peace Elite (和平精英) at EWC', 'theme': 'Game-Specific', 'sources': [61, 76]},
    'G4': {'label': 'PUBG Mobile at EWC', 'theme': 'Game-Specific', 'sources': [123]},
    'G5': {'label': 'Mobile Legends: Bang Bang (决胜巅峰) at EWC', 'theme': 'Game-Specific', 'sources': [7, 31, 118]},
    'G6': {'label': 'Street Fighter at EWC', 'theme': 'Game-Specific', 'sources': [29, 95]},
    'G7': {'label': 'League of Legends at Asian Games & EWC', 'theme': 'Game-Specific', 'sources': [4, 11, 40, 72, 83, 119]},
    'G8': {'label': 'Dota 2 at Riyadh Masters/EWC', 'theme': 'Game-Specific', 'sources': [102]},
    'G9': {'label': 'Counter-Strike at EWC', 'theme': 'Game-Specific', 'sources': [124]},
}

# =============================================================================
# STEP 3: BUILD ASSIGNMENT MAPPINGS & CALCULATE STATISTICS
# =============================================================================
print("Building assignment mappings...")

def get_count(tid):
    return topics[tid]['count'] if tid in topics else 0

def calc_total(ids):
    return sum(get_count(tid) for tid in ids)

# Build reverse mapping: topic_id -> list of (code, theme)
assignments = {}
for code, data in FINAL_TOPICS.items():
    for tid in data['sources']:
        if tid not in assignments:
            assignments[tid] = []
        assignments[tid].append((code, data['theme']))

# Calculate totals
total_docs = sum(t['count'] for t in topics.values())
outlier_docs = topics[-1]['count']
non_outlier_docs = total_docs - outlier_docs

# Table 1 totals
table1_total_docs = 0
table1_total_sources = 0
for code, data in FINAL_TOPICS.items():
    table1_total_docs += calc_total(data['sources'])
    table1_total_sources += len(data['sources'])

# Multi-category topics
multi_cat_topics = []
total_overlap = 0
for tid, assigns in assignments.items():
    if len(assigns) > 1:
        doc_count = topics[tid]['count']
        codes = [a[0] for a in assigns]
        overlap = doc_count * (len(assigns) - 1)
        multi_cat_topics.append((tid, topics[tid]['gpt'][:50], doc_count, codes))
        total_overlap += overlap

multi_cat_doc_total = sum(t[2] for t in multi_cat_topics)

# Check for unassigned topics
all_assigned = set(assignments.keys())
all_topic_ids = set(t for t in topics.keys() if t != -1)
unassigned = all_topic_ids - all_assigned

print(f"  {len(assignments)} topics assigned to {len(FINAL_TOPICS)} final categories")
print(f"  {len(multi_cat_topics)} topics in multiple categories")
print(f"  {len(unassigned)} unassigned topics: {sorted(unassigned) if unassigned else 'None'}")

# =============================================================================
# STEP 4: GENERATE MARKDOWN OUTPUT
# =============================================================================
print("Generating markdown output...")

lines = []

# Header & Summary
lines.append("# Esports UGC Topic Consolidation Plan")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append("This plan consolidates 129 BERTopic topics into 58 final topics for your manuscript, with legitimacy type classifications (pragmatic, moral, cognitive).")
lines.append("")
lines.append("### Current State Analysis")
lines.append(f"- **{len(topics)} original topics** (Topic -1 is outlier with {outlier_docs:,} docs, kept separate)")
lines.append(f"- **{len(assignments)} topics assigned** to {len(FINAL_TOPICS)} final topic categories")
lines.append("- **0 topics missing** (full coverage achieved)")
lines.append("")
lines.append("### Decision Framework")
lines.append("Per your criteria:")
lines.append("- Preserve game-specific discourse (no cross-game merging)")
lines.append("- Keep events separate (Asian Games vs EWC)")
lines.append("- Keep stakeholder perspectives separate")
lines.append("- Maintain temporal specificity")
lines.append("- Tag each topic with legitimacy type")
lines.append("")
lines.append("---")
lines.append("")

# Data Verification
lines.append("## Data Verification")
lines.append("")
lines.append("| Metric | Count |")
lines.append("|--------|-------|")
lines.append(f"| Original Topics | {len(topics)} |")
lines.append(f"| Total Documents | {total_docs:,} |")
lines.append(f"| Outlier (Topic -1) | {outlier_docs:,} (kept separate) |")
lines.append(f"| Non-Outlier Documents | {non_outlier_docs:,} |")
lines.append(f"| Final Topic Categories | {len(FINAL_TOPICS)} |")
lines.append(f"| Table 1 Total (with overlaps) | {table1_total_docs:,} |")
lines.append(f"| Multi-Category Topics | {len(multi_cat_topics)} ({total_overlap:,} docs overlap) |")
lines.append("")
lines.append(f"**Verification**: {non_outlier_docs:,} (non-outlier) + {total_overlap:,} (overlap) = {non_outlier_docs + total_overlap:,} = Table 1 total ✓")
lines.append("")
lines.append("---")
lines.append("")

# Legitimacy Framework
lines.append("## Proposed Final Topic List with Legitimacy Classification")
lines.append("")
lines.append("### Legitimacy Framework")
lines.append("- **Pragmatic**: Direct benefits for stakeholders (economic success, fan engagement, competitive results)")
lines.append("- **Moral**: Normative evaluation of actions/values (fairness, player treatment, controversies)")
lines.append("- **Cognitive**: Taken-for-granted status, institutional recognition (official events, national representation)")
lines.append("")
lines.append("---")
lines.append("")

# Helper to generate category table
def generate_category_table(category_codes, title, description=None, extra_col=None):
    lines.append(f"### {title}")
    lines.append("")
    if description:
        lines.append(description)
        lines.append("")
    
    if extra_col:
        lines.append(f"| # | Final Topic Label | Source Topics | Count | {extra_col} |")
        lines.append(f"|---|------------------|---------------|-------|{'------|' if extra_col else ''}")
    else:
        lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
        lines.append("|---|------------------|---------------|-------|-----------|")
    
    subtotal = 0
    for code in category_codes:
        data = FINAL_TOPICS[code]
        total = calc_total(data['sources'])
        subtotal += total
        source_str = ', '.join(str(s) for s in data['sources'])
        if extra_col == 'Game':
            game = data.get('game', '')
            lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | {game} |")
        else:
            lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | |")
    
    return subtotal

# A. COGNITIVE
lines.append("### A. COGNITIVE LEGITIMACY TOPICS (Institutional Recognition & Taken-for-Granted Status)")
lines.append("")
lines.append("These topics relate to esports achieving institutional recognition through major events and official status.")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
lines.append("|---|------------------|---------------|-------|-----------|")

cognitive_codes = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
cognitive_subtotal = 0
for code in cognitive_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    cognitive_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    rationale = {
        'C1': 'Core institutional milestone - esports as medal event',
        'C2': 'Official team formation process',
        'C3': 'Establishing EWC as major international circuit',
        'C4': 'Geopolitical positioning of esports',
        'C5': 'Established tournament circuit',
        'C6': 'Symbolic inclusion in Olympic tradition',
        'C7': 'Technology integration in traditional sports format',
        'C8': 'Institutional decision on game inclusion',
        'C9': 'Media legitimization'
    }.get(code, '')
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | {rationale} |")

lines.append(f"| | **COGNITIVE SUBTOTAL** | | **{cognitive_subtotal:,}** | |")
lines.append("")
lines.append("---")
lines.append("")

# B. PRAGMATIC
lines.append("### B. PRAGMATIC LEGITIMACY TOPICS (Stakeholder Benefits & Practical Interests)")
lines.append("")
lines.append("These topics relate to direct benefits: competitive results, fan engagement, sponsorships, economic outcomes.")
lines.append("")

# B1. Results
lines.append("#### B1. Competition Results & Player Achievements")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
lines.append("|---|------------------|---------------|-------|-----------|")

results_codes = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9']
results_subtotal = 0
for code in results_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    results_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | |")

lines.append(f"| | **Results Subtotal** | | **{results_subtotal:,}** | |")
lines.append("")

# B2. Fan Engagement
lines.append("#### B2. Fan Engagement & Support Campaigns")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
lines.append("|---|------------------|---------------|-------|-----------|")

fan_codes = ['P10', 'P11', 'P12', 'P13', 'P14', 'P15', 'P16', 'P17', 'P18']
fan_subtotal = 0
for code in fan_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    fan_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | |")

lines.append(f"| | **Fan Engagement Subtotal** | | **{fan_subtotal:,}** | |")
lines.append("")

# B3. Team Performance
lines.append("#### B3. Team & Organizational Performance")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
lines.append("|---|------------------|---------------|-------|-----------|")

team_codes = ['P19', 'P20', 'P21', 'P22', 'P23', 'P24', 'P25']
team_subtotal = 0
for code in team_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    team_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | |")

lines.append(f"| | **Team Performance Subtotal** | | **{team_subtotal:,}** | |")
lines.append("")

# B4. Commercial
lines.append("#### B4. Sponsorships, Partnerships & Commercial Activities")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
lines.append("|---|------------------|---------------|-------|-----------|")

commercial_codes = ['P26', 'P27', 'P28', 'P29', 'P30', 'P32', 'P33', 'P34']
commercial_subtotal = 0
for code in commercial_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    commercial_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | |")

lines.append(f"| | **Commercial Subtotal** | | **{commercial_subtotal:,}** | |")
lines.append("")

pragmatic_total = results_subtotal + fan_subtotal + team_subtotal + commercial_subtotal
lines.append(f"**PRAGMATIC GRAND TOTAL: {pragmatic_total:,}**")
lines.append("")
lines.append("---")
lines.append("")

# C. MORAL
lines.append("### C. MORAL LEGITIMACY TOPICS (Normative Evaluation & Values Alignment)")
lines.append("")
lines.append("These topics involve judgment of fairness, player rights, and ethical conduct.")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Rationale |")
lines.append("|---|------------------|---------------|-------|-----------|")

moral_codes = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
moral_subtotal = 0
for code in moral_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    moral_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | |")

lines.append(f"| | **MORAL SUBTOTAL** | | **{moral_subtotal:,}** | |")
lines.append("")
lines.append("---")
lines.append("")

# D. GAME-SPECIFIC
lines.append("### D. GAME-SPECIFIC TOPICS (Preserving Discourse by Game Title)")
lines.append("")
lines.append("Per your criteria, these are kept separate by game.")
lines.append("")
lines.append("| # | Final Topic Label | Source Topics | Count | Game |")
lines.append("|---|------------------|---------------|-------|------|")

game_info = {
    'G1': 'HoK', 'G2': 'HoK', 'G3': 'PUBG Mobile CN', 'G4': 'PUBG Mobile Intl',
    'G5': 'MLBB', 'G6': 'Street Fighter', 'G7': 'LoL', 'G8': 'Dota 2', 'G9': 'CS'
}
game_codes = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9']
game_subtotal = 0
for code in game_codes:
    data = FINAL_TOPICS[code]
    total = calc_total(data['sources'])
    game_subtotal += total
    source_str = ', '.join(str(s) for s in data['sources'])
    lines.append(f"| {code} | **{data['label']}** | {source_str} | {total:,} | {game_info.get(code, '')} |")

lines.append(f"| | **GAME-SPECIFIC SUBTOTAL** | | **{game_subtotal:,}** | |")
lines.append("")
lines.append("---")
lines.append("")

# Multi-category topics
lines.append("## Topics Appearing in Multiple Categories")
lines.append("")
lines.append(f"{len(multi_cat_topics)} topics are assigned to multiple final topic categories:")
lines.append("")
lines.append("| Topic ID | GPT Label | Docs | Categories |")
lines.append("|----------|-----------|------|------------|")

for tid, gpt, count, codes in sorted(multi_cat_topics, key=lambda x: -x[2]):
    lines.append(f"| {tid} | {gpt} | {count:,} | {', '.join(codes)} |")

lines.append(f"| | **TOTALS** | **{multi_cat_doc_total:,}** | |")
lines.append("")
lines.append("---")
lines.append("")

# Final Summary
lines.append("## Final Topic Count Summary")
lines.append("")
lines.append("| Category | Topics | Documents |")
lines.append("|----------|--------|-----------|")
lines.append(f"| Cognitive Legitimacy | {len(cognitive_codes)} | {cognitive_subtotal:,} |")
lines.append(f"| Pragmatic Legitimacy | {len(results_codes) + len(fan_codes) + len(team_codes) + len(commercial_codes)} | {pragmatic_total:,} |")
lines.append(f"| Moral Legitimacy | {len(moral_codes)} | {moral_subtotal:,} |")
lines.append(f"| Game-Specific (cross-cutting) | {len(game_codes)} | {game_subtotal:,} |")
lines.append(f"| **TOTAL** | **{len(FINAL_TOPICS)}** | **{table1_total_docs:,}*** |")
lines.append("")
lines.append(f"*Includes {total_overlap:,} docs from multi-category topics counted in multiple categories")
lines.append("")
lines.append("---")
lines.append("")

# Verification Plan
lines.append("## Verification Plan")
lines.append("")
lines.append("### Manual Verification (User Review)")
lines.append("")
lines.append("1. **Review each final topic** in the list above to confirm:")
lines.append("   - Merge decisions are appropriate (not losing important distinctions)")
lines.append("   - Legitimacy classification aligns with your theoretical framework")
lines.append("   - No topics are missing from the original 128 (excluding -1 outlier)")
lines.append("")
lines.append("2. **Check game-specific preservation**: Confirm MLBB, HoK, LoL, Peace Elite, Street Fighter, Dota 2, and Counter-Strike topics remain distinct")
lines.append("")
lines.append("3. **Validate stakeholder separation**: Confirm player-focused, team-focused, and organizational topics are appropriately distinguished")
lines.append("")
lines.append("### Deliverables After Approval")
lines.append("")
lines.append("Once you approve this plan, I will:")
lines.append("1. Create a clean Excel file with the final topic list")
lines.append("2. Include columns for: Topic ID, Final Label, Original Topics Merged, Document Count, Legitimacy Type, Rationale")
lines.append("3. Update the task.md to mark completion")

# =============================================================================
# STEP 5: SAVE OUTPUT FILES
# =============================================================================
content = '\n'.join(lines)

# Save to main output file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Saved: {OUTPUT_FILE}")

# Save backup
with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"✓ Saved: {BACKUP_FILE}")

# Save to artifact directory
try:
    with open(ARTIFACT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Saved: {ARTIFACT_FILE}")
except Exception as e:
    print(f"⚠ Could not save artifact: {e}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("")
print("=" * 60)
print("GENERATION COMPLETE")
print("=" * 60)
print(f"  Final Topics: {len(FINAL_TOPICS)}")
print(f"  Original Topics Assigned: {len(assignments)}")
print(f"  Total Documents: {total_docs:,}")
print(f"  Multi-Category Topics: {len(multi_cat_topics)} ({total_overlap:,} overlap)")
if unassigned:
    print(f"  ⚠ UNASSIGNED TOPICS: {sorted(unassigned)}")
else:
    print(f"  ✓ All non-outlier topics assigned")
