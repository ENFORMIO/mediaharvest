# mediaharvest
The basic interest behind this collection of scripts is to find out more about online media activities during time. 

##Idea
The idea of the experiment is: 
* I want to download an article of a specific newspaper and analyze it.
* I want to download all articles of several specific newspapers and analyze it. 
* I want to download all articles of several specific newspapers multiple over the time to analyze changes.

##Steps in the process
Therefore I've put some scripts together to 
* collect: fetch the data from the medias server into a sqlite-db-file
* transfer: insert single sqlite-db-files into a central mysql database
* extract: analyze features downloaded files according 
* inspect: use the data in jupyter notebooks.
