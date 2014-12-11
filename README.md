PROM - Predicting Revenue of Movies
====

Prediction of the success of the movie depends on various factors. In this project we studied this problem using a social network-based approach. 

Using a dataset of movies spread over 20 years of Hollywood cinema, we uncover the collaboration network for each of the movies. We seek to analyze and compute influence of each of the contributors of the movies – actors, directors, scriptwriters etc., towards the success of the movie. Using these influence scores of the collaborators, we then predict the box office revenue of the movies.

We are analysing various algorithms like HITS, Modified Shapley approach etc., that can be used to compute the influence score of the collaborators.

1. extractMovieLink.py
- to get the movie links from the films listed by year page in wikipedia.
2. extractMovieData.py
- to extract the movie infobox from wikipedia
3. getOscarData.py
- to extract academy awards info
4. insertToDB.py
- to clean and consolidate our data.

