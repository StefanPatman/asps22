# Fogify Topology Generator

Σκοπός της εργασίας είναι η μοντελοποίηση και προσομοίωση fog παραμετροποιήσιμων υπηρεσιών παραγόμενων από το Εther, με χρήση του Fogify. Ουσιαστικά σκοπός της εργασίας είναι η δημιουργία μιας γεννήτριας τοπολογιών για το Fogify, χρησιμοποιώντας το Ether ένα εργαλείο Python για τη δημιουργία τοπολογιών. Έπειτα η δημιουργία μιας αντιπροσοπευτικής Edge εφαρμογής για την παρουσίαση της υλοποίησης μας και την διεκπεραίωση πειραμάτων.

Read more: [report-draft.odt](report-draft.odt)

## Application

Η εφαρμογή μας προσομοιώνει το Fog σύστημα για την λήψη και επεξεργασία θερμοκρασιών σε εργοστάσια. Η τοπολογία μας αποτελείται από εργοστάσια, καθένα εκ’ των οποίων έχει παραμετροποήσιμο αριθμό πατωμάτων και μηχανημάτων-θερμομέτρων σε αυτά. Οι συσκεύες, generators, σε κάθε πάτωμα του εργοστασίου παράγουν δεδομένα τα οποία συλλέγει ο aggregator του πατώματος. Τέλος κάθε εργοστάσιο έχει τον δικό του processor, όπου συλέγονται τα δεδομένα και μπορούν να εμφανιστούν στην μορφή λίστας. Τα εργοστάσια συνδέονται σε κοινό internet πράγμα πυ επιτρέπει στο κθένα όποτε θέλει να έχει πρόσβαση στα δεδομένα του άλλου.

Build the docker images:
`make all`

Manually run the app using docker-compose:
`docker-compose -f examples/unfogified.yml up`

To check the server output, visit:
http://0.0.0.0:5003/data?id=1


## Topology Generator

Install requirements:
```
pip install -r requirements.txt
```

Generate a new fogified yaml for a simple case:
```
python src/topology/main.py examples/simple.yml > examples/simple-out.yml
```

## Using Fogify

First build the application docker images and generate a topology.

Then start Fogify and connect to the Jupyter interface.

Drag and drop the following files:
```
examples/asps-example.ipynb
examples/simple-out.yml
```

Deploy the topology using Jupyter.

Find the processor API page from the logs:
```
docker service logs fogify_processor_0_item
```

Connect to the page and query the specified id, eg:
http://172.18.0.3:5003/data?id=0

Undeploy using Jupyter.
