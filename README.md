# Divvy-Bike-Dock-Balancing-Analysis
As people’s usage of traditional commuting plumed since the onset of covid, bike-sharing services such as divvy have become increasingly popular. Demand for bikes are not evenly distributed, this leads to either bike shortage or lack of empty docks. This individual project visualized this challenge and proposed a solution to the problem.

## Data Overview 
|Dataset Sample|Description|Source|
|:---:|:-|:-|
|[**Divvy Trip Data**](https://docs.google.com/spreadsheets/d/14UR2y1TdE1TQRJC87GSyN7z9tdK97oNsLcsJ8gaEAyg/edit#gid=2026743272)|This dataset includes individual Divvy bike sharing trips, including the origin, destination, timestamps, and rider type for each trip.|https://www.divvybikes.com/system-data
|[**Chicago Taxi Trips**](https://docs.google.com/spreadsheets/d/14UR2y1TdE1TQRJC87GSyN7z9tdK97oNsLcsJ8gaEAyg/edit#gid=1019737694)|Taxi trips reported to the City of Chicago in its role as a regulatory agency. File contains taxi rides from one community area to another, with a minimum of 2.0 miles travelled during strandard commuting hours (after 7AM but before 7PM).|https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew|
|[**Chicago Community-Neighborhood**](https://docs.google.com/spreadsheets/d/14UR2y1TdE1TQRJC87GSyN7z9tdK97oNsLcsJ8gaEAyg/edit#gid=231358633)|Table linking Chicago's 77 community areas (by name and number) to its 274 neighborhoods (also by name and number)|https://en.wikipedia.org/wiki/List_of_neighborhoods_in_Chicago|
|[**Chicago Commuter Survey**](https://docs.google.com/spreadsheets/d/14UR2y1TdE1TQRJC87GSyN7z9tdK97oNsLcsJ8gaEAyg/edit#gid=1387586703)|Results from a survey conducted in early 2020 (pre-COVID pandemic) to determine number of commuters and primary method of commuting across Chicago, including respondents from all of Chicago's 54 zip codes and 247 neighborhoods.|https://www.movematcher.com/blog/commute-times-in-chicago/|
|[**Divvy Station Master Data**](https://docs.google.com/spreadsheets/d/14UR2y1TdE1TQRJC87GSyN7z9tdK97oNsLcsJ8gaEAyg/edit#gid=717210174)|Master file of all Divvy stations included in the Chicago-area network, including important station codes, number of docks, status, and addresses. This file links each Divvy station to a Chicago zip code, neighborhood, and community area.|https://data.cityofchicago.org/Transportation/Divvy-Bicycle-Stations-All-Map/bk89-9dk7|

## Project Structure:
![image](https://user-images.githubusercontent.com/62736640/159799005-d70e050d-ad1f-4030-b62e-1a9ba4c7f339.png)

## Data Engineering 
![IMG_7408](https://user-images.githubusercontent.com/62736640/160229594-49238ab9-67fb-40d1-bb05-b4d56c67ad44.PNG)
Remote database was created on RCC through Ubuntu,FileZilla.The database can be accessed through Hue or Pyhive following this [instruction](https://just-market-8d4.notion.site/How-to-create-a-database-on-RCC-Hadoop-and-access-it-using-Python-19e51b5464424e328bdc454b742d6df4).

## Feature Engineering 
### Connecting databases through (Longitude,Latitude)

### Simulate dock parking to track capacity change 

## Graph Analysis 
![image](https://user-images.githubusercontent.com/62736640/160230165-c5aa0d9c-e75c-46b6-9fb0-d0b2cf17fd87.png)

![Graph](https://github.com/Ryan47Liao/Demo/blob/main/graph_viz.GIF)

![image](https://user-images.githubusercontent.com/62736640/160230183-20bcae45-f67e-46b5-b778-4000d5d1be3e.png)

![Capacity Shift](https://github.com/Ryan47Liao/Demo/blob/main/Capacity_Animated.png)
