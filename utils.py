import xml.etree.ElementTree as ET


class GpxFile:

    def __init__(self, file, ns=None):
        if ns is None:
            ns = 'http://www.topografix.com/GPX/1/1'
        self. ns = ns
        tree = ET.parse(file)
        root = tree.getroot()
        print root

        self.time = root.find('{%s}metadata/{%s}time' % (ns, ns)).text
        self.name = root.find('{%s}trk/{%s}name' % (ns, ns)).text

        self.points = []

        for pt in root.find('.//{%s}trkseg' % (ns)):
            point = {
                    'lat': pt.attrib['lat'],
                    'lng': pt.attrib['lon'],
                    'ele': pt.find('{%s}ele' % (ns)).text,
                    'time': pt.find('{%s}time' % (ns)).text
                    }
            self.points.append(point)

    def __repr__(self):
        return '<GpxFile>(%s, %s)' % (self.name, self.time)
