# Fogify Topology Generator

Σκοπός της εργασίας είναι η υλοποίηση μιας γεννήτριας τοπολογιών για το Fogify, χρησιμοποιώντας το Ether, ένα εργαλείο Python για δημιουργία των τοπολογιών. Για την παρουσίαση της υλοποίησης μας και την διεκπεραίωση πειραμάτων κατασκευάσαμε μια multiservice Edge εφαρμογή μετρήσεων θερμοκρασίας σε εργοστασιακό περιβάλλον. Χρησιμοποιήσαμε την γεννήτρια τοπολογιών και να ρυθμίσουμε και να δοκιμάσουμε διαφορετικά σενάρια προσομοίωσης.

Read more: [report.pdf](report.pdf)

## Εφαρμογή

Η εφαρμογή μας προσομοιώνει το Fog σύστημα για την λήψη και επεξεργασία θερμοκρασιών σε εργοστάσια. Η τοπολογία μας αποτελείται από εργοστάσια, καθένα εκ’ των οποίων έχει παραμετροποήσιμο αριθμό πατωμάτων και μηχανημάτων-θερμομέτρων σε αυτά. Οι συσκεύες, generators, σε κάθε πάτωμα του εργοστασίου παράγουν δεδομένα τα οποία συλλέγει ο aggregator του πατώματος. Τέλος κάθε εργοστάσιο έχει τον δικό του processor, όπου συλέγονται τα δεδομένα και μπορούν να εμφανιστούν στην μορφή λίστας. Τα εργοστάσια συνδέονται σε κοινό internet πράγμα πυ επιτρέπει στο κθένα όποτε θέλει να έχει πρόσβαση στα δεδομένα του άλλου.

## Οδηγίες για το τρέξιμο της εφαρμογής

Δεδομένου ότι έχει γίνει clone ο κώδικας της εργασίας και έχουν εγκατασταθεί σωστά τα Fogify και Ether:

Αρχικά πρέπει να γίνει build των docker images:
```
$ cd asps22
$ make all
```
Έπειτα ελευθερώνουμε το swarm:
```
$ docker swarm leave –force
```
Βρίσκουμε την ip μας:
```
$ ifconfig
```
Και θέτουμε την ip μας σαν manager του swarm:
```
$ docker swarm init --advertise-addr [ip]
```
Φτιάχνουμε την τοπολογία μέσω του ether τρέχοντας το αρχείο fogify_example.yml με την παρακάτω εντολή
```
$ python3 src/topology/main.py examples/fogify_example.yml > examples/fogified/fogify_example.out.yml
```
Μας εμφανίζεται στην οθόνη η τοπολογία σε εικόνα και κλείνοντάς την δημιουργείται το αντίστοιχο αρχείο `fogify_example.out.yml`.

Σε μια άλλη κονσόλα μπαίνουμε στον φάκελο του fogify-demo και ανοίγουμε τον προσομοιωτή τοπολογιών του fogify εκτελώντας:
```
$ docker-compose -p fogemulator up
```
Ανοίγουμε το jupiter στο link: http://127.0.0.1:8888/lab
Μετά πρέπει να ανέβουν στο Jupyter του Fogify τα αρχεία:
- examples/run.ipynb
- examples/fogified/fogify_example.out.yml

Το deployment γίνεται από Jupyter με προσαρμογή της παραμέτρου της εντολής:
```
fogify = FogifySDK("http://controller:5000", \ 	"fogify_example.out.yml")
```
Όταν εκτελέσουμε το deploy ελέγχουμε αν έχουν ανέβει όλα τα services (replicas 1/1) με την εντολή
```
$ docker service list
```
Αφού γίνει κάθε τοπολογία deploy συνήθως χρειάζονται δύο λεπτά για να φτάσει σε κατάσταση ισορροπίας το σύστημα. Κάθε πακέτο που φτάνει στον server περιέχει τον μέσο όρο θερμοκρασιών 10 μετρήσεων ενός σένσορα (window), καθώς και κάποια διαγνωστικά. O server κρατάει στην μνήμη τα τελευταία 10 πακέτα (history) για κάθε σένσορα. Επιλέχθηκε μικρό ώστε να φτάνουμε ταχύτερα σε κατάσταση ισορροπίας στο endpoint.

Τα endpoints του processor προωθούνται στο localhost και εκεί μπορούμε να δούμε τα αποτελέσματα, οπότε τα διαγνωστικά που θέλουμε για κάθε πείραμα θα είναι διαθέσιμα στη url:
http://127.0.0.1:5005/diagnose/all

Για να τρέξουμε την επόμενη τοπολογία τρέχουμε την εντολή undeploy() του jupiter και επαναλαμβάνουμε την διαδικασία


## ΒΙΒΛΙΟΓΡΑΦΙΑ

[1]  Fogify: A Fog Computing Emulation Framework. Symeonides, M., Georgiou, Z., Trihinas, D., Pallis, G., & Dikaiakos, M. In Proceedings of the 5th ACM/IEEE Symposium on Edge Computing, of SEC ’20, New York, NY, USA, 2020. Association for Computing Machinery.

[2] Synthesizing Plausible Infrastructure Configurations for Evaluating Edge Computing Systems: Rausch, T., Lachner, C., Frangoudis, P. A., Raith, P., & Dustdar, S. (2020). In 3rd USENIX Workshop on Hot Topics in Edge Computing (HotEdge 20). USENIX Association.

GitHub links for dependencies:
 -	Fogify: https://github.com/UCY-LINC-LAB/fogify
 -	Ether:  https://github.com/edgerun/ether
