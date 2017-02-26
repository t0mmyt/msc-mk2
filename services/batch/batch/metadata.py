from cassandra.cluster import Cluster


class Metadata(object):
    keyspace = 'seismic'
    keyspace_definition = ("CREATE KEYSPACE IF NOT EXISTS seismic WITH replication = {'class': 'SimpleStrategy', "
                           "'replication_factor': 1};")
    station_definition = ("CREATE TABLE IF NOT EXISTS Stations ("
                          "  network text PRIMARY KEY,"
                          "  station text,"
                          "  channel text"
                          ");")

    def __init__(self, hosts):
        assert isinstance(hosts, list), "hosts should be a list"
        cluster = Cluster(hosts)
        session = cluster.connect()
        session.execute(Metadata.keyspace_definition)
        self.c = cluster.connect(Metadata.keyspace)
        self.c.execute(Metadata.station_definition)
