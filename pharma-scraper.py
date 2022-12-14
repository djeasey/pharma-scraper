import requests
from bs4 import BeautifulSoup
import pandas as pd

# Main Page with Links
url1 = "https://www.erexam.org/emergency-drugs/"
page1 = requests.get(url1)
soup1 = BeautifulSoup(page1.content, "html.parser")
main_page = soup1.find_all("a")

# Create empty dataframe to append results to
df = pd.DataFrame(list(zip([], [], [])), columns =['Drugname', 'Question', 'Answer'])

# Iterate through links on main page
for job_element in main_page[5:]:

    # Scrape each link
    url2 = job_element["href"]
    page2 = requests.get(url2)
    soup2 = BeautifulSoup(page2.content, "html.parser")

    # Drug name is the main title
    drug_name = soup2.find_all("h1")[0].text
    print(drug_name)

    # Skip funky pages
    manual_list = ["ATYPICAL ANTI-PSYCHOTICS","CEPHALOSPORINS","CHOLINORECEPTOR BLOCKING DRUGS"]
    if drug_name in manual_list:
        continue

    # Get the table on the page
    table = soup2.find_all("table")

    # Get the rows of the table
    data = table[0].find_all("tr")

    # Form lists of the data to create a dataframe
    drugname_list = []
    question_list = []
    answer_list = []

    # For each row in the table
    for elem in data:

        # Split the text by new lines
        split_text = elem.text.split("\n")

        # Remove the blank lines
        split_text_no_blanks = [s for s in split_text if s]

        # Join back the answer data
        answer = "\n".join(split_text_no_blanks[1:])

        # First line is the question data
        question = split_text_no_blanks[0]

        # Append data to the lists
        drugname_list.append(drug_name)
        question_list.append(question)
        answer_list.append(answer)
    
    # Turn lists into a dataframe
    df1 = pd.DataFrame(list(zip(drugname_list, question_list, answer_list)), columns =['Drugname', 'Question', 'Answer'])

    # Concatenate to the existing dataframe
    df = pd.concat([df, df1])

# Clean up the questions
df['Question'] = df['Question'].replace(['Structure/Class'], 'Structure/class')
df['Question'] = df['Question'].replace(['Structure'], 'Structure/class')
df['Question'] = df['Question'].replace(["Withdrawal states"], 'Withdrawal syndrome')
df['Question'] = df['Question'].replace(["Adverse events"], 'Adverse effects')
df['Question'] = df['Question'].replace(["Administration"], 'Absorption/administration')
df['Question'] = df['Question'].replace(["Absorption/Administration"], 'Absorption/administration')
df['Question'] = df['Question'].replace(["Indication"], 'Indications')
df['Question'] = df['Question'].replace(["Absorption/admin"], 'Absorption/administration')
df['Question'] = df['Question'].replace(["Metabolism/Excretion"], 'Pharmacokinetics')
df['Question'] = df['Question'].replace(["Absorption/admins"], 'Absorption/administration')

# Only allow some questions (since there are some nested tables)
acceptable_columns = ["Structure/class","Pharmacodynamics","Absorption/administration","Pharmacokinetics","Distribution","Metabolism","Excretion","Indications","Contraindications","Special precautions","Dosing/administration","Toxicology","Withdrawal syndrome","Special notes","Interactions","Adverse effects"]

# Print out the funky drugs that have been skipped
print(df[~df['Question'].isin(acceptable_columns)])
print(manual_list)
print(df[~df['Question'].isin(acceptable_columns)]['Drugname'].unique())

# Filter for good questions
good_df = df[df['Question'].isin(acceptable_columns)]

# Pivot data so that questions are columns
pivoted_df = good_df.pivot(index='Drugname', columns='Question', values='Answer')

# Export to CSV
pivoted_df.to_csv('pivoted_df.csv')

# Troubleshooting where the same question exists multiple times
# print(good_df.groupby(['Question','Drugname']).size() 
#    .sort_values(ascending=False) 
#    .reset_index(name='count') )
