# POLITICAL MONITORING

The current project was elaborated with the aim to 
demonstrate the possibility to monitor the political 
landscape by analysing tweets with specific queries.

A user can retrieve all tweets with the name of a particular 
politician or party and assess the trends in volume and 
sentiment over time.

At this stage the set up includes a pipeline for collecting
tweets with a particular query and segregation between tweets,
users and the hashtags used.

## Use case

To demonstrate its capabilities, the system is retrieving all tweets and
retweets that include the word "Bolsonaro" the president of Brazil.
The choice for this query derives from the fact that the president is
very active in social media, particularly Twitter, which gives a wealth
of data to be analysed.

To enrich this analysis, we also added data from the events the president
participates in as announced in government official channel
https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/agenda-do-presidente-da-republica/

Using both sources of data we can correlate the presidential activities 
with the buzz generated in social media.

### Architecture and pipeline

In order to capture the necessary data the following architecture was 
implemented.

![alt text](imgs/architecture.png?raw=true "Architecture")

### Streaming tweets

The code that captures the stream of tweets lives in a EC2 machine,
connecting to the Twitter API and handling it to AWS Firehose that in
turn delivers it to the s3 bucket twitter-data-stream. The 
twitter-data-stream bucket stores the tweets in json format and are
partitioned into a datetime structure as follows based on
year/month/day/hour as it is standard per firehose.

The step involves transforming the raw json files into tables to be
served for analysis. Here we are using Redshift, which will transform
the raw data into three distinct tables, tweets, users and hashtags.

### Presidential agenda

For the presidential agenda, there is a manual ingestion that is placed in
the s3 bucket: s3://agenda-president/agenda_president.csv

The file is then uploaded into a dedicated tables in redshift

## Data base

![alt text](imgs/data_base.png?raw=true "data base")

## Airflow

The ETL process is orchestrated using airflow. The tweets are ingested
on an hourly basis by 'tweets_dag.py' and the presidential agenda
is ingested daily by 'agenda_dag'.

### tweets_dag

![alt text](imgs/tweets_dag_diagram.png?raw=true "Architecture")

![alt text](imgs/tweets_schedule.png?raw=true "Architecture")

### agenda_dag

![alt text](imgs/agenda_diagram_dag.png?raw=true "Architecture")

![alt text](imgs/agenda_schedule.png?raw=true "Architecture")

## Analysis

Using the structure of the data analysed it is possible to see the trends 
over time

![alt text](imgs/analytics2.png?raw=true "Architecture")

And the effect of presidential events on social media

![alt text](imgs/analytics3.png?raw=true "Architecture")


