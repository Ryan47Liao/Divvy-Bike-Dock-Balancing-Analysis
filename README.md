# Divvy-Bike-Dock-Balancing-Analysis
Help Divvy, a Chicago based bike-sharing company, solve their bike rebalancing challenges. 

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
### Connecting databases through (Longitude,Latitude), using [Google Geo-Encoder](https://developers.google.com/maps/documentation/geocoding/start)
Our goal was to connect originally disconnected databases, divvy trip and taxi,bus trip through community. However, community doesn't have an native foreign key to connect to stations, nor does it has geo-data such as coordinates. Therefore, we had to use Google's geo-encoder api to 'convert' string names into coordinates so community can be MAPed to stations. 
Another advantage of connecting stations with neighbourhood (or community), is that I can then group by community instead of station in future analysis, reducing dimension from 2000+ to less than 100. 

### Simulate dock parking to track capacity change 
To visualize the dock capacity for each station at a specific time, I would love to have data that has each station as the column, and each row as the time stamp, so that the capacity change can be kept track of. 
However, there exist no such data, but instead, the complete travel history was provided. Using this travel history, a simulation is able to be recreated, thus keep track of the capacity throughout the day.
![image](https://user-images.githubusercontent.com/62736640/160230502-36630ee4-4203-42ee-9531-3d22f3304734.png)


## Graph Analysis 
#### Let’s start and take a look at this Graph of user travel history throughout the day;
    What you are looking at is an animation of graphs, consisting of 24 snapshots of travel history at each hour of the day.
    
    Each orange dot represents a station, if a user traveled from station A to station B at the time of the snapshot, a line
    will be connecting the dots.  The more people travel during the time, the bolder the line will be. And if a user travels 
    from station C and ends up coming back to station C or its neighborhood, you will see a circle, 
    connecting back to the dot itself.
    
    The graph is generated by treating each station as a Node, 
    and the aggregated travel history within one hour as a weighted edge. Visualized by the thickness of the edge. 

![Graph](https://github.com/Ryan47Liao/Demo/blob/main/graph_viz.GIF)

    The key takeaway would be people are traveling from the skirt of city toward the city center in the morning,
    and travel within the city center until night falls. 
    
    If you take a step back and only focus on the big picture, you can see most lines intersects in the center of the graph,
    which happens to be the city center. This shows that people are actively traveling around the center. 
    In the morning from 3-6, there are long lines connecting skirt areas and city centers. 
    This shows people are traveling from skirt areas into the city center. 

![image](https://user-images.githubusercontent.com/62736640/160230165-c5aa0d9c-e75c-46b6-9fb0-d0b2cf17fd87.png)  
       
    By calculating the degree centrality of all neighbour hoods as nodes, the pattern is even more clearer. 
    The small dots are stations and the big dots are neighbours, color coded by its centrality. 
    The darker the dot, the higher the centrality, meaning more people travel to these nodes than others. 
    
    By understanding how people travel within the city of Chicago, we establish the context to understand our challenges: 
    that people are swarming into the center of the city, causing imbalance in bike supplies at each station. 
    So next, let’s explore how each station looks like in terms of capacity change.

## Dock Capacity Visualization and Analysis
#### This is a visualization of capacity change of all stations across the week. 
    Like before, each dot is a visual representation of each station. All the dots are color coded by the relative capacity change. 
    The warmer the color, it means more people are docking at the station than leaving, the colder the color, 
    it means more people are leaving the station leaving it empty. 
    The animated scatter plot shows a snapshot of all stations on each weekday. 


![Capacity Shift](https://github.com/Ryan47Liao/Demo/blob/main/Capacity_Animated.png)

    On weekdays, people leave the outer skirt area and travel into the city center. Leaving the city center highly crowded. 
    People from the near skirt coastal area travel to the city center, but on weekends people tend to visit the coastal area more often. 
    
    Although most colors change throughout the days, the outer skirt of chicago remains blue. 
    Indicating people are leaving these areas rather than coming. On the other hand, the central Chicago are constantly in warm colors, 
    indicating people are docking at these stations throughout the week. 
    The very central coast area however, is a bit interesting. It changes from blue to red as the weekday shifts from workday into weekends. 

![image](https://user-images.githubusercontent.com/62736640/160230183-20bcae45-f67e-46b5-b778-4000d5d1be3e.png)

    In this line chart, it's also obvious how people's travel habits are similiar in workdays, different from in weekends.

    In this visualization, we have verified our conjectures from previous network graph, 
    next we are going to dive into each dock’s change of capacity over the day. 
    
    
#### Sample Capacity trend breakdown
    If you could focus on the right upper corner where the arrows are shooting out, we have our same geo graph, 
    except this time, we color coded them based on natural clusters, or stations share similar capacity trends. 
    
    The orange cluster represents the inner skirt, while purple and red clusters are typical city center areas. 
    
    For each capacity trend, we have relative capacity change on the y-axis and timestamp on the x-axis. 
    High capacity trend indicates people are docking at the station, while below zero capacity change represents people’s leave. 
    
    Although geographically approximated, these clusters were actually only based on their capacity change
    as you can see in the trend graphs that they are all very similar to each other. 
    
    Stations in the inner skirt areas are the ones suffering from empty docks, 
    whereas stations in the city center are the stations swarmed with bikes that have no dock to park. 
![image](https://user-images.githubusercontent.com/62736640/160230843-45c04a82-51a1-4182-b2e9-b9cd6264ac54.png)

    Observing the cluster 5 graph on the top left corner, you can see that there is a sharp decline in the afternoon, 
    and the overall capacity change is below zero. 
    The sharp decrease corresponds to a sharp increase in cluster 4 during the afternoon. 
    Representing people are leaving the inner skirt areas and docking their bikes at the city center. 
    Some stations’ capacity change goes up by 50%, and stays around 20% by the end of the day. 
    Similarly, stations in cluster 5 tend to stay negative even by the end of the day. 
    This means that people ride bikes from cluster 5 and leave it at cluster 4, each day, causing the imbalance among clusters exaggerated each day. 


## Final Take-aways
Currently, there are already a lot of stations in the city center area. But a capacity increase of 50% still indicates high risks of overloaded stations with more bikes than docks. While adding more docks in the city center would reduce the risk, the fact that people ride the bike into the center and don’t ride it back is the key problem leading to our dilemma. We could find ways to encourage people to ride them back, or have staff maneuvers the bikes and redistribute them in places in need. 

