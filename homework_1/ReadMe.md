# Answer 1 (What is the tag for 'Image ID to file' after running docker --help build) 

Command: docker --help build
ANSWER: --iidfile string

# Answer 2 ( How many modules/packages are installed after running a docker with an image of Python 3.9? running pip list)

Run Command: pip list

ANSWER:
Package    Version
---------- -------
pip        22.0.4
setuptools 58.1.0
wheel      0.38.4


# Preparation - Done --> But could prepare it as pipeline

# Answer 3 - How many trips were made (ordered and completed) on 2019-01-05
SELECT count(*) 
FROM yellow_taxi_trips2 
WHERE date(lpep_pickup_datetime)='2019-01-15'
AND date(lpep_dropoff_datetime)='2019-01-15';

ANSWER = 20530

# Answer 4 - Which was the day with the largest trip distance eg. as in longest trip (tip: use pick up time for calculation)
SELECT date(lpep_pickup_datetime), max(trip_distance)
FROM yellow_taxi_trips2 
GROUP BY 1
ORDER BY 2 DESC;

ANSWER = 2019-01-15

# Answer 5 - In 2019-01 how many trips had 2 and 3 passengers
SELECT passenger_count, COUNT(*)
FROM yellow_taxi_trips2 
WHERE date(lpep_pickup_datetime)='2019-01-01'
GROUP BY 1
HAVING (passenger_count=2 OR passenger_count=3)

ANSWER = 2: 1282, 3: 254

# Answer 6 - For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest #tip? We want the name of the zone, not the id.
WITH astoria_zones AS (
	SELECT * 
	FROM green_taxi_zones zo
	WHERE "Zone" LIKE ('%Astoria%')
)
SELECT 
MAX(tip_amount) AS max_tip, 
az."Zone" AS PickUpZone,
gz."Zone" AS DropOffZone
FROM yellow_taxi_trips2 tr
INNER JOIN astoria_zones az
ON tr."PULocationID" = az."LocationID"
INNER JOIN green_taxi_zones gz
ON tr."DOLocationID"= gz."LocationID"
GROUP BY 2,3

Answer = "Long Island City/Queens Plaza"

