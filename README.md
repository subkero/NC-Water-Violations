<h1>
# NC-Water-Violations -- main_app.py
</h1> 

<h2>About </h2>
App to download water violations data from the Drinking Water Watch website, munge data and visualize data on 4 maps. The main app -- main_app.py -- uses 3 helper modules: coords_getters.py, population_getters.py and map_builders.py to handle the heavy lifting of: getting the relevant coordinates of locations associated with water violations; querying the Census API for population data of these locations; and constructing desired map, respectively.
 
For each run of the app a separate map is generated depicting: 1)total count of water violations in each of North Carolina's counties (choropleth map); 2) violation (per person) density in each of North Carolina's counties (choropleth); 3)total count of water violations in each town (bubble map) and 4) violation (per person) density in each of North Carolina's towns (bubble map).

please see article: <https://www.linkedin.com/pulse/beauty-python-how-messy-data-screws-everything-up-keron-subero/>

for a more complete descrition of the development and usage of the map.

<h3> Using the app</h3>
Water Violations data is stored in the Drinking Water Watch database, which can be queried at endpoints of the form: 'https://www.pwss.enr.state.nc.us/NCDWW2/JSP/Violations.jsp?tinwsys_is_number={}&tinwsys_st_code=NC'
Each violation is identified by a violation number. In order to sequentially query violations stored in the database a Start and end violation number must be set through the parameters:
START_WSYS_NUM (which can potentially start from 1) and END_WSYS_NUM=3505 (which at last check ends past 23900).

 
The app is written in python and should run similarly to any other python script by using for instance the "$>python Test.py" command in Terminal on any Mac or Linux machine, with afformentioned dependencies in the same folder.

<h3>How to set up the dev environment</h3>
$> pip install Requirements.txt
<br>
This app also queries the census api which requires a (free) access key.

 <h4>License and author info<h4>
Code written by Keron Subero and falls under General Public License -- GPLv3 <https://www.gnu.org/licenses/gpl-3.0.en.html> (so feel free to modify and use as you like under these libearal guidelines). Any questions please message me on LinkedIn.

