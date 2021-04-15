# Ebec-Paris-Saclay

Our tool is designed to meet all objectives with resilience while managing to give the user the best possible experience.

## Installation 
```bash
pip install -r requirements.txt
``` 
## Launch the web app
```bash
python user_interface/app.py
``` 
Then open your navigator on localhost.

## Example of use 
![Click here to see the interface](./Capture2.JPG)
![Click here to see the results](./Capture.JPG)

## Technical explanations 

Our algorithm is based on Openstreetmap's API : Overpass.


Given a point's coordinates, the first thing is to find the city and the street where the point is located. To do so, we do a [Binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) around the given point and we increase the initial precision value that is editable in the config.yaml file.
Once that we have found the street, we can obtain the street's list of nodes via Overpass, and then find the crossing streets. Given that, we build road sections and find the one that minimizes the distance with the initial point by calcultaing cross products. Eventually, we print the optimum road section using Folium library.

For the second objective, the query function of Overpass returns the nodes in the wanted order, so we get it.

For the third objective, we have created a merge function that merges the two optimum road sections for the two given points and we also visualize it. 

For each query on our tool, the result is printed on screen and stored in cache system to faster the process for next queries. We also print a sentence describing the localisation in natural language.

Our Web App is based on a personnal template and aims to give the user on the one hand, a nice interface to visualize the results and on the other hand an easy way to enter the wanted coordinates by hand or uploading a .csv file.

## Contributors 

Arnaud Petit, Simon Tronchi, Matthieu Annequin and Hicham Bouanani

## License
[MIT](https://choosealicense.com/licenses/mit/)
