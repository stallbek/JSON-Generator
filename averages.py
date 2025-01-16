import pandas as pd


file_path = './assets/classesInfo.xlsx'
df = pd.read_excel(file_path, sheet_name='Results')


df_cleaned = df.dropna(subset=['Class']).reset_index(drop=True)
df_cleaned = df_cleaned.drop(columns=['Class Ave.1'], errors='ignore')
df_cleaned = df_cleaned.iloc[1:].reset_index(drop=True)

grade_mapping = {
    'A': 4.0, 'A-': 3.7,
    'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7,
    'D+': 1.3, 'D': 1.0, 'D-': 0.7,
    'F': 0.0
}


df_cleaned['Grade Value'] = df_cleaned['Class Ave'].map(grade_mapping)


df_cleaned['Season'] = df_cleaned['TermName'].str[0]
df_cleaned['Year'] = df_cleaned['TermName'].str[1:].astype(int)


df_filtered = df_cleaned[df_cleaned['Season'].isin(['W', 'S', 'F'])]


def calculate_trends(course_data, season, max_years=4):
    trends = {}
    for i in range(1, max_years + 1):
        season_data = course_data[course_data['Season'] == season].sort_values(by='Year', ascending=False).head(i)
        if not season_data.empty:
            trends[f"{season}_Trend_{i}years"] = f"{season_data['Grade Value'].mean():.1f}"
        else:
            trends[f"{season}_Trend_{i}years"] = None
    return trends


def calculate_highest_nyears(course_data, n_years):
    highest_nyears = {}
    max_average = -1
    best_season = None

    for season in ['W', 'S', 'F']:
        season_data = course_data[course_data['Season'] == season].sort_values(by='Year', ascending=False).head(n_years)
        if len(season_data) == n_years:
            avg_nyears = season_data['Grade Value'].mean()
            if avg_nyears > max_average:
                max_average = avg_nyears
                best_season = season

    if best_season:
        highest_nyears[f"the_highest_{n_years}years"] = f"{best_season}, {max_average:.1f}"
    else:
        highest_nyears[f"the_highest_{n_years}years"] = None

    return highest_nyears


summary_list = []
unique_id = 1

for course in df_filtered['Course'].unique():
    course_data = df_filtered[df_filtered['Course'] == course]

    credits = course_data['Credits'].iloc[0] if not course_data['Credits'].isnull().all() else None

    winter_trends = calculate_trends(course_data, 'W', 4)
    summer_trends = calculate_trends(course_data, 'S', 4)
    fall_trends = calculate_trends(course_data, 'F', 4)
    highest_4years = calculate_highest_nyears(course_data, 4)
    highest_3years = calculate_highest_nyears(course_data, 3)
    highest_2years = calculate_highest_nyears(course_data, 2)

    fall_data = course_data[course_data['Season'] == 'F'].sort_values(by='Year', ascending=False).head(3)
    fall_trend_special = None
    if not fall_data.empty:
        fall_trend_special = f"last {len(fall_data)} years: {fall_data['Grade Value'].mean():.1f} (Fall)"


    summary = {
        'id': unique_id,
        'Course': course,
        'Credits': credits,
        **winter_trends,
        **summer_trends,
        **fall_trends,
        **highest_4years,
        **highest_3years,
        **highest_2years,
        'Fall_Trend_3years_special': fall_trend_special
    }

    summary_list.append(summary)
    unique_id += 1


import json
json_output = json.dumps(summary_list, indent=4)


with open('course_summary_trends.json', 'w') as json_file:
    json_file.write(json_output)

print("No errors")
