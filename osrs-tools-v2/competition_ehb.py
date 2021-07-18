#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as bs
import bs4
import argparse
import gspread

sanity_group_url = r"https://templeosrs.com/groups/stats.php?id=265"
r = requests.get(sanity_group_url)
soup = bs(r.text, 'html.parser')
td_list = soup.find_all('td')

hexis_comp_url = r"https://templeosrs.com/competitions/standings.php?id=5960&skill=76"
r = requests.get(hexis_comp_url)
soup = bs(r.text, 'html.parser')
participants = soup.find_all(class_="participant-row")

for participant in participants:
	meat = participant.contents[1].contents
	flag_present = len(meat) == 5   # is 5 if there's a country flag, else 4
	name_index = 0
	ehb_index = 2 if flag_present else 1
	update_index = 4 if flag_present else 3

	name = str(meat[name_index].contents[0])
	ehb = float(meat[ehb_index].contents[0])
	last_updated = meat[update_index].contents[0]
	last_updated_text = last_updated.contents[0] if isinstance(last_updated, bs4.Tag) else last_updated

	print(name, ehb, last_updated_text)

# <tr "="" class="participant-row">
#   <td>1.</td>
#   <td style="border-left: 0;">
#       <a class="link-no-style" href="../player/overviewpvm.php?player=Kacy&amp;date=2021-05-31 23:59:00&amp;skill=Ehb&amp;duration=2678340seconds" style="color: var(--main-theme-seventh);">Kacy</a>
#       <img src="../resources/flags/United-States.png" style="margin-top: 3px" title="United-States"/>
#       <td style="color:lawngreen; text-align: center; border-left: 0;">+83.06</td>
#       <td style="text-align: center; border-left: 0;">4,687 -&gt; 4,771</td>
#       <td>
#           <a class="link-no-style" href="../php/add_datapoint.php?player=Kacy&amp;comp=5960">7h ago</a>
#       </td>
#   </td>
# </tr>

if __name__ == '__main__':
	pass
