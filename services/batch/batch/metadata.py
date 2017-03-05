from cassandra.cluster import Cluster


class Metadata(object):
    keyspace = 'seismic'
    keyspace_definition = ("CREATE KEYSPACE IF NOT EXISTS seismic WITH replication = {'class': 'SimpleStrategy', "
                           "'replication_factor': 1};")
    station_definition = ("CREATE TABLE IF NOT EXISTS Stations ("
                          "  network text,"
                          "  station text,"
                          "  channel text,"
                          "  PRIMARY KEY(network, station, channel)"
                          ");")
    observations_definition = ("CREATE TABLE IF NOT EXISTS Observations ("
                               "  network text,"
                               "  station text,"
                               "  channel text,"
                               "  start timestamp,"
                               "  end timestamp,"
                               "  sampling_rate smallint,"
                               "  PRIMARY KEY ((network, station, channel))"
                               ");")

    def __init__(self, hosts):
        # TODO - Exceptions
        assert isinstance(hosts, list), "hosts should be a list"
        self.cluster = Cluster(hosts)

    def create_tables(self):
        session = self.cluster.connect()
        session.execute(Metadata.keyspace_definition)
        c = self.cluster.connect(Metadata.keyspace)
        c.execute(Metadata.station_definition)
        c.execute(Metadata.observations_definition)

    def add_meta(self, network, station, channel, start, end, sampling_rate):
        # TODO - Exceptions
        c = self.cluster.connect(Metadata.keyspace)
        prepared = c.prepare("INSERT INTO Stations (network, station, channel) VALUES(?, ?, ?) IF NOT EXISTS;")
        c.execute(prepared, (network, station, channel))
        prepared = c.prepare("INSERT INTO Observations (network, station, channel, start, end, sampling_rate)"
                             "VALUES(?, ?, ?, ?, ?, ?) IF NOT EXISTS;")
        c.execute(prepared, (network, station, channel, start, end, int(sampling_rate)))
        return True
