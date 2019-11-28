<h1 align="center">UFO Blog Guidelines</h1>
</br>

---
## Application
### Specifics
- Docker :whale:
- MongoDB <img src="https://jaystack.com/wp-content/uploads/2015/12/mongodb-leaf-e1497443272821.png" height="25" align="center"> 
- Python <img src="https://user-images.githubusercontent.com/21998037/69779876-bf02d300-11a9-11ea-98d0-26b1a335059e.png" height="20">
- RDF <img src="https://dinacon.ch/wp-content/uploads/sites/4/2018/05/rdf-icon-with-shadow.png" height="20">
- Folium <img src="https://cdn.iconscout.com/icon/free/png-256/world-map-earth-pin-marker-location-destination-5-22737.png" height="20">

</br>

### Getting started
**Minimum requirements:**</br>
> Docker

> Python3
 - `pip install rdflib`
 - `pip install geotext`
 - `pip install folium`
 - `pip install pymongo`
 
 </br>
 
To be able to successfully run the application all the above requirements need to be met! This guide will rely heavily on the usage of Docker to be able to run the database systems.

To start off, you will first clone the repository by using the command:  
`git clone https://github.com/elit0451/DatabasesBlogEntry.git`.  

When this process is finished, head to the `Application > Resources` folder where you will find a text file containing the download link for the necessary data. Go ahead and download it.
</br>After extracting the downloaded file, your `Resources` folder structure should look like:
```
Application > Resources > Books
Application > Resources > Offline_Catalogue
Application > Resources > cities5000.csv
```

Having these folders will ensure the proper usage of the following docker commands.
</br></br>

Now we are ready to proceed to the next step. Navigate to the folder **“Application”** within your shell and start mongo database container by executing the following command:
> MongoDB :

```docker run --rm -v ${PWD}/mongo_data:/data/db --publish=27017:27017 --name mongodb -d mongo:latest```  
NB:exclamation: For _Windows_ users you would need to make the extra step of creating a volume using  
`docker volume create --name=mongo_data` before spinning the container.

</br>

After this is done the last step is to execute the _“ufoImporter.py”_ file with the command `python ufoImporter.py` or `python3 ufoImporter.py` depending on your installation.

Let the program sit for a bit while you go and enjoy a nice cup of coffee... :coffee: Depending on your hardware this might take up to an hour.
</br>

After the execution of the python script is complete, you can use the mongo shell by executing `docker run -it --link mongodb:mongo --rm mongo sh -c 'exec mongo "$MONGO_PORT_27017_TCP_ADDR:$MONGO_PORT_27017_TCP_PORT/test"'` for reproducing our results.
