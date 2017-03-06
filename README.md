# Mytinerary
Mytinerary is a Carleton College comps project created by Caleb Braun, Hailey Jones, Tristan Leigh, and Jonah Tuchow. 
The project is based off of the paper Aurigo: An Interactive Tour Planner for Personalized Itineraries by Alexandre Yahi, Antoine Chassang, Louis Raynaud, Hugo Duthil, and Duen Horng (Polo) Chau. 
The original paper can be found [here](http://www.cc.gatech.edu/~dchau/papers/15-iui-aurigo.pdf).

### What is it?
Mytinerary is a fast, interactive, and personalized itinerary builder for walking tours of cities. It recommends a route for a user based on their preferences (i.e. do they want to see more parks?), how far they are willing to stray from the fastest route, and ratings of points of interest to visit based on Yelp reviews.

### How to install
1. Clone this repository
2. Install Django version 1.10 or newer
3. Install PostgreSQL
4. Install Psycopg2 `pip3 install psycopg2`
5. Install Google Maps Python API `pip3 install GoogleMaps`
6. Install twilio `pip3 install twilio`
7. Configure TourItineraryComps/mytinerary/mytinerary/settings.py to interact with the PSQL database
8. Run TourItineraryComps/mytinerary/populate_db.py
9. Run locally using Django's development server, or configure Django with Apache and mod_wsgi 
