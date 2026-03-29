"""
Update topic model output with Final Topic Labels and Themes
===========================================================
Reads input_data.xlsx and adds:
- Final_Topic_Code: The consolidated topic code (C1, P12, M1, G7, etc.)
- Final_Topic_Label: Human-readable label
- Legitimacy_Theme: Cognitive, Pragmatic-*, Moral, or Game-Specific

Output: output_with_labels.xlsx
"""

import pandas as pd

print("Loading data...")
df = pd.read_excel('input_data.xlsx')
print(f"  Loaded {len(df)} rows")

# Topic to Final Topic mapping from Table 2
# Format: {original_topic_id: [(code, theme), ...]}
TOPIC_MAPPING = {
    -1: [('Outlier', 'Outlier')],
    0: [('P18', 'Pragmatic-Fan')],
    1: [('C3', 'Cognitive')],
    2: [('P12', 'Pragmatic-Fan')],
    3: [('C3', 'Cognitive')],
    4: [('M1', 'Moral'), ('G7', 'Game-Specific')],
    5: [('P12', 'Pragmatic-Fan')],
    6: [('P10', 'Pragmatic-Fan')],
    7: [('G5', 'Game-Specific')],
    8: [('C1', 'Cognitive')],
    9: [('M2', 'Moral')],
    10: [('P18', 'Pragmatic-Fan')],
    11: [('P22', 'Pragmatic-Team'), ('G7', 'Game-Specific')],
    12: [('C4', 'Cognitive')],
    13: [('P1', 'Pragmatic-Results')],
    14: [('P26', 'Pragmatic-Commercial')],
    15: [('P10', 'Pragmatic-Fan')],
    16: [('P13', 'Pragmatic-Fan')],
    17: [('C3', 'Cognitive')],
    18: [('M5', 'Moral')],
    19: [('P15', 'Pragmatic-Fan')],
    20: [('P18', 'Pragmatic-Fan')],
    21: [('P8', 'Pragmatic-Results')],
    22: [('P8', 'Pragmatic-Results')],
    23: [('P27', 'Pragmatic-Commercial')],
    24: [('P34', 'Pragmatic-Commercial')],
    25: [('P32', 'Pragmatic-Commercial')],
    26: [('M2', 'Moral')],
    27: [('M3', 'Moral')],
    28: [('C4', 'Cognitive')],
    29: [('P3', 'Pragmatic-Results'), ('G6', 'Game-Specific')],
    30: [('P12', 'Pragmatic-Fan')],
    31: [('G5', 'Game-Specific')],
    32: [('C3', 'Cognitive')],
    33: [('C3', 'Cognitive')],
    34: [('P14', 'Pragmatic-Fan')],
    35: [('G1', 'Game-Specific')],
    36: [('P15', 'Pragmatic-Fan')],
    37: [('P12', 'Pragmatic-Fan')],
    38: [('P12', 'Pragmatic-Fan')],
    39: [('P12', 'Pragmatic-Fan')],
    40: [('G1', 'Game-Specific'), ('G7', 'Game-Specific')],
    41: [('P12', 'Pragmatic-Fan')],
    42: [('P23', 'Pragmatic-Team')],
    43: [('P15', 'Pragmatic-Fan')],
    44: [('P19', 'Pragmatic-Team')],
    45: [('C9', 'Cognitive')],
    46: [('C2', 'Cognitive')],
    47: [('P20', 'Pragmatic-Team')],
    48: [('P16', 'Pragmatic-Fan')],
    49: [('C6', 'Cognitive')],
    50: [('C7', 'Cognitive')],
    51: [('P33', 'Pragmatic-Commercial')],
    52: [('C4', 'Cognitive')],
    53: [('P25', 'Pragmatic-Team')],
    54: [('P16', 'Pragmatic-Fan')],
    55: [('P12', 'Pragmatic-Fan')],
    56: [('P16', 'Pragmatic-Fan')],
    57: [('M4', 'Moral')],
    58: [('G1', 'Game-Specific')],
    59: [('M4', 'Moral')],
    60: [('P12', 'Pragmatic-Fan')],
    61: [('G3', 'Game-Specific')],
    62: [('P11', 'Pragmatic-Fan')],
    63: [('C8', 'Cognitive')],
    64: [('M5', 'Moral'), ('G2', 'Game-Specific')],
    65: [('P12', 'Pragmatic-Fan')],
    66: [('M7', 'Moral')],
    67: [('P15', 'Pragmatic-Fan')],
    68: [('P12', 'Pragmatic-Fan')],
    69: [('P12', 'Pragmatic-Fan')],
    70: [('P7', 'Pragmatic-Results')],
    71: [('C3', 'Cognitive')],
    72: [('C2', 'Cognitive'), ('G7', 'Game-Specific')],
    73: [('P12', 'Pragmatic-Fan')],
    74: [('M4', 'Moral')],
    75: [('P7', 'Pragmatic-Results')],
    76: [('G3', 'Game-Specific')],
    77: [('C4', 'Cognitive')],
    78: [('M4', 'Moral')],
    79: [('P24', 'Pragmatic-Team')],
    80: [('M7', 'Moral')],
    81: [('P12', 'Pragmatic-Fan')],
    82: [('P12', 'Pragmatic-Fan')],
    83: [('M6', 'Moral'), ('G7', 'Game-Specific')],
    84: [('M4', 'Moral')],
    85: [('M2', 'Moral')],
    86: [('M5', 'Moral')],
    87: [('P15', 'Pragmatic-Fan')],
    88: [('C2', 'Cognitive')],
    89: [('P29', 'Pragmatic-Commercial')],
    90: [('M4', 'Moral')],
    91: [('P12', 'Pragmatic-Fan')],
    92: [('P17', 'Pragmatic-Fan'), ('G2', 'Game-Specific')],
    93: [('P12', 'Pragmatic-Fan')],
    94: [('P15', 'Pragmatic-Fan')],
    95: [('P9', 'Pragmatic-Results'), ('G6', 'Game-Specific')],
    96: [('P21', 'Pragmatic-Team')],
    97: [('P12', 'Pragmatic-Fan')],
    98: [('M7', 'Moral')],
    99: [('P12', 'Pragmatic-Fan')],
    100: [('P10', 'Pragmatic-Fan')],
    101: [('P34', 'Pragmatic-Commercial')],
    102: [('C5', 'Cognitive'), ('G8', 'Game-Specific')],
    103: [('C3', 'Cognitive')],
    104: [('P30', 'Pragmatic-Commercial')],
    105: [('P12', 'Pragmatic-Fan')],
    106: [('P2', 'Pragmatic-Results')],
    107: [('P12', 'Pragmatic-Fan')],
    108: [('M2', 'Moral')],
    109: [('P15', 'Pragmatic-Fan')],
    110: [('C3', 'Cognitive')],
    111: [('P14', 'Pragmatic-Fan')],
    112: [('P12', 'Pragmatic-Fan')],
    113: [('P5', 'Pragmatic-Results')],
    114: [('P12', 'Pragmatic-Fan')],
    115: [('P12', 'Pragmatic-Fan')],
    116: [('P12', 'Pragmatic-Fan')],
    117: [('P12', 'Pragmatic-Fan')],
    118: [('G5', 'Game-Specific')],
    119: [('P6', 'Pragmatic-Results'), ('G7', 'Game-Specific')],
    120: [('P12', 'Pragmatic-Fan')],
    121: [('P28', 'Pragmatic-Commercial')],
    122: [('P8', 'Pragmatic-Results')],
    123: [('G4', 'Game-Specific')],
    124: [('P4', 'Pragmatic-Results'), ('G9', 'Game-Specific')],
    125: [('P12', 'Pragmatic-Fan')],
    126: [('P11', 'Pragmatic-Fan')],
    127: [('M5', 'Moral'), ('G2', 'Game-Specific')],
}

# Final topic labels from Table 1
FINAL_LABELS = {
    'C1': 'Hangzhou Asian Games: Esports as Official Sport',
    'C2': 'Asian Games National Team Selection Process',
    'C3': 'Esports World Cup (EWC) as Premier Global Event',
    'C4': 'Saudi Arabia as Major Esports Host Nation',
    'C5': 'Dota 2 Riyadh Masters',
    'C6': 'Asian Games Torch Relay with Esports Athletes',
    'C7': 'Esports Virtual Human at Asian Games',
    'C8': 'Hearthstone Removed from Asian Games',
    'C9': 'Tencent Official Broadcasting Rights',
    'P1': 'Yinuo (Xu Bicheng) Wins EWC FMVP',
    'P2': 'Faker Wins EWC FMVP (LoL)',
    'P3': 'Xiaohai (Zeng Zhuojun) Wins Street Fighter EWC',
    'P4': 'NAVI Wins Counter-Strike EWC',
    'P5': 'Team Falcons Wins EWC Club Championship',
    'P6': 'JDG夺冠与LPL亚运话题',
    'P7': 'EWC Match Results & Highlights',
    'P8': 'LoL at EWC: LPL vs LCK Matches',
    'P9': 'Street Fighter EWC Qualifiers',
    'P10': 'Yinuo (一诺) Asian Games Fan Support',
    'P11': 'Fan Support for Dream Team Players',
    'P12': 'LGD/Hua Aotian (花傲天) EWC Fan Hype',
    'P13': 'AG超玩会 (AG Super Play) Asian Games Support',
    'P14': 'eStarPro 花海/坦然 Performance & Support',
    'P15': 'Asian Games Countdown & General Fan Support',
    'P16': 'EWC Chinese Teams Fan Mobilization',
    'P17': 'KPL Dream Team (梦之队) at EWC',
    'P18': 'General EWC Fan Support & Engagement',
    'P19': 'Tianba (天霸) at Peace Elite EWC',
    'P20': 'XYG at EWC 揭幕战',
    'P21': 'WBG at Saudi EWC',
    'P22': 'Korean LoL National Team at Asian Games',
    'P23': 'Team China at Asian Games (YiNuo Narrative)',
    'P24': '和平精英亚运版本国家集训队',
    'P25': 'MLBB Tournament Results (International)',
    'P26': 'Luo Yunxi (罗云熙) as Migu Esports Ambassador',
    'P27': 'vivo/iQOO Official Phones Partnership',
    'P28': 'Yestar (艺星) Medical Aesthetics Partnership',
    'P29': 'Yili (伊利) Asian Games Sponsorship',
    'P30': 'EWC Club Support Program & Partnerships',
    'P32': 'Digital/Tech Products (王室好物)',
    'P33': 'EWC Qiddiya City Venue Promotion',
    'P34': 'Hangzhou Asian Games Esports Ticketing',
    'M1': 'JackeyLove Withdrawal from Asian Games Controversy',
    'M2': 'Jiuwei (九尾) EWC Roster Exclusion Controversy',
    'M3': "Cat's Exclusion from EWC Roster Controversy",
    'M4': 'Nanjing Hero Club Transfer Fee Controversy (Wuwei)',
    'M5': 'KPL Controversies & Roster Debates',
    'M6': 'Uzi Asian Games Roster Discussions',
    'M7': 'Wuwei (无畏) Dream Team Voting & Fan Advocacy',
    'G1': 'Honor of Kings (王者荣耀) at Asian Games',
    'G2': 'Honor of Kings: KPL at EWC',
    'G3': 'Peace Elite (和平精英) at EWC',
    'G4': 'PUBG Mobile at EWC',
    'G5': 'Mobile Legends: Bang Bang (决胜巅峰) at EWC',
    'G6': 'Street Fighter at EWC',
    'G7': 'League of Legends at Asian Games & EWC',
    'G8': 'Dota 2 at Riyadh Masters/EWC',
    'G9': 'Counter-Strike at EWC',
    'Outlier': 'Outlier (Topic -1)',
}

print("Mapping topics to final labels...")

def get_final_codes(topic_id):
    """Get all final topic codes for a topic ID"""
    if topic_id in TOPIC_MAPPING:
        return '; '.join([m[0] for m in TOPIC_MAPPING[topic_id]])
    return 'Unknown'

def get_final_labels(topic_id):
    """Get all final topic labels for a topic ID"""
    if topic_id in TOPIC_MAPPING:
        codes = [m[0] for m in TOPIC_MAPPING[topic_id]]
        return '; '.join([FINAL_LABELS.get(c, c) for c in codes])
    return 'Unknown'

def get_themes(topic_id):
    """Get all themes for a topic ID"""
    if topic_id in TOPIC_MAPPING:
        themes = list(set([m[1] for m in TOPIC_MAPPING[topic_id]]))
        return '; '.join(themes)
    return 'Unknown'

# Add new columns
df['Final_Topic_Code'] = df['Topic'].apply(get_final_codes)
df['Final_Topic_Label'] = df['Topic'].apply(get_final_labels)
df['Legitimacy_Theme'] = df['Topic'].apply(get_themes)

# Save to new file
output_file = 'output_with_labels.xlsx'
print(f"Saving to {output_file}...")
df.to_excel(output_file, index=False)

# Summary
print("")
print("=" * 60)
print("COMPLETE")
print("=" * 60)
print(f"  Output: {output_file}")
print(f"  Rows: {len(df)}")
print(f"  New columns: Final_Topic_Code, Final_Topic_Label, Legitimacy_Theme")
print("")
print("Theme distribution:")
print(df['Legitimacy_Theme'].value_counts().head(10))
