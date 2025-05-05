# Mechanic API

In this project, I have started to build out a Flask API using SQLAlchemy and Marshmallow. It allows users to create customers, mechanics and service tickets. I have used a many to many relationship to connect tickets to mechanics and created the service ticket schema to allow nested data for mechanics and customer information. I created CRUD routes for mechanics and customers and a POST and GET request for service tickets which implements the nested data fetching and exclusions.
