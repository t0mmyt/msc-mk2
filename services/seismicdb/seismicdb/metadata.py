from crate.client import connect
from datetime import datetime
from iso8601 import parse_date
from logging import debug


class MetadataError(Exception):
    pass


class Metadata(object):
    def __init__(self, endpoints):
        if not isinstance(endpoints, list):
            endpoints = [endpoints]
        self.connection = connect(servers=endpoints)

    def create_tables(self):
        return True
        c = self.connection.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS seismic.Metadata("
                  "uuid string PRIMARY KEY,"
                  "network STRING,"
                  "station STRING,"
                  "channel STRING,"
                  "start_time TIMESTAMP,"
                  "end_time TIMESTAMP,"
                  "sampling_rate int)")

    def put(self, uuid, network, station, channel, start, end, sampling_rate):
        start = datetime.fromtimestamp(start / 1000).replace(tzinfo=None).isoformat()
        end = datetime.fromtimestamp(end / 1000).replace(tzinfo=None).isoformat()
        c = self.connection.cursor()
        c.execute("SELECT COUNT(*) AS count FROM seismic.Metadata "
                  " WHERE network = ?"
                  " AND station = ?"
                  " AND channel = ?"
                  " AND start_time = ?"
                  " AND end_time = ?",
                  (network, station, channel, start, end))
        res = c.fetchone()
        if int(res[0]) > 0:
            raise MetadataError("Data already exists for {}".format(','.join((network, station, channel, start, end))))
        c.execute("INSERT INTO seismic.Metadata "
                  "(uuid, network, station, channel, start_time, end_time, sampling_rate)"
                  "VALUES(?, ?, ?, ?, ?, ?, ?)",
                  (uuid, network, station, channel, start, end, sampling_rate))

    def list(self, network, station, channel, start, end, sampling_rate=None):
        start = parse_date(start).replace(tzinfo=None)
        end = parse_date(end).replace(tzinfo=None)
        c = self.connection.cursor()
        c.execute("SELECT uuid, start_time, end_time, sampling_rate"
                  " FROM seismic.Metadata"
                  " WHERE network = ?"
                  " AND station = ?"
                  " AND channel = ?"
                  " AND (start_time <= ? AND end_time >= ?"
                  " OR start_time >= ? AND end_time <= ?"
                  " OR start_time <= ? AND end_time >= ?)",
                  (network, station, channel, start, start, start, end, end, end))
        return c.fetchall()
