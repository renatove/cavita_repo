# This Python file uses the following encoding: utf-8
import sys
import json
import arcpy
from arcgis.features.layer import FeatureLayerCollection
from arcgis.features.layer import FeatureLayer
from PySide6 import QtWidgets
# from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, \
    QLabel, QLineEdit, QHBoxLayout, QTableWidget, \
    QVBoxLayout, QTableWidgetItem, QPushButton, QDialog
from PySide6.QtCore import SIGNAL, QObject
from configparser import ConfigParser
from setting import *


# classi
class Ui_myDialog(QDialog):
    def __init__(self, datarow, parent=None):
        super(Ui_myDialog, self).__init__(parent)
        self.initUI()
        self.setDataRow(datarow)

    def initUI(self):
        self.setWindowTitle("Cavità Selezionata")
        layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        for i in range(0, len(source_item), 2):
            self.gridLayout.addWidget(QLabel(source_item[i]), i, 0)
            self.gridLayout.addWidget(QLineEdit(), i, 1)
            if (i + 1) < len(source_item):
                self.gridLayout.addWidget(QLabel(source_item[i + 1]), i, 2)
                self.gridLayout.addWidget(QLineEdit(), i, 3)
        layout.addLayout(self.gridLayout)
        self.setLayout(layout)

    def setDataRow(self, datarow):
        print(datarow)
        k = 0
        for i in range(0, self.gridLayout.count()):
            widget_item = self.gridLayout.itemAt(i)
            widget = widget_item.widget()
            if i % 2 != 0:
                text = datarow[0][k]
                widget.setText(text)
                k = k + 1
            else:
                text = widget.text()
            print(text)


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.json_file = ""
        self.initUI()

    def initUI(self):
        width = 900
        heigth = 700
        self.setWindowTitle("Nessun file selezionato")
        self.resize(width, heigth)
        layout = QVBoxLayout()

        tableLayout = QHBoxLayout()
        self.tableWidget = QTableWidget()

        self.tableWidget.setColumnCount(len(source_item))
        self.tableWidget.setHorizontalHeaderLabels(source_item)
        tableLayout.addWidget(self.tableWidget)

        QObject.connect(self.tableWidget, SIGNAL('itemSelectionChanged()'), self.print_row)

        buttonsLayout = QHBoxLayout()
        self.buttonOpen = QPushButton("Open GeoJson")
        QObject.connect(self.buttonOpen, SIGNAL('clicked()'), self.OpenGeoJsonFile)
        self.buttonImport = QPushButton("Import Data")
        self.buttonImport.setEnabled(False)
        QObject.connect(self.buttonImport, SIGNAL('clicked()'), self.ImporGeotJsonFile)
        self.buttonSave = QPushButton("Save in GDB")
        self.buttonSave.setEnabled(False)
        QObject.connect(self.buttonSave, SIGNAL('clicked()'), self.SaveGeoJsonFile)
        self.buttonPortal = QPushButton("Send to Portal")
        QObject.connect(self.buttonPortal, SIGNAL('clicked()'), self.SendToPortal)
        self.buttonPortal.setEnabled(True)
        buttonClose = QPushButton("Close")
        QObject.connect(buttonClose, SIGNAL('clicked()'), self.closeForm)

        buttonsLayout.addWidget(self.buttonOpen)
        buttonsLayout.addWidget(self.buttonImport)
        buttonsLayout.addWidget(self.buttonSave)
        buttonsLayout.addWidget(self.buttonPortal)
        buttonsLayout.addWidget(buttonClose)

        layout.addLayout(tableLayout)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

    # funzioni
    def OpenGeoJsonFile(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open", "", "GeoJson (*.json)")
        if file_name[0] != '':
            window.json_file = file_name[0]
            window.setWindowTitle(file_name[0])
            self.buttonImport.setEnabled(True)
            self.buttonOpen.setEnabled(False)
        else:
            window.setWindowTitle("Nessun file selezionato")

    def ImporGeotJsonFile(self):
        escapes = ''.join([chr(char) for char in range(1, 32)])
        if window.json_file != '':
            path_to_file = window.json_file
            f = open(path_to_file, 'r', encoding="utf8", errors="ignore")
            try:
                f.seek(0)
                feat_obj = json.load(f)
                nfeat = 0
                for feat in feat_obj['features']:
                    nfeat = nfeat + 1
                # print("numero punti: %d", nfeat)

                for i in range(nfeat):
                    data_item = []
                    # print("Cavita: %5d " % (i + 1))
                    # geometry
                    geom = feat_obj["features"][i]["geometry"]
                    coord = geom['coordinates']
                    long = coord[0]
                    lati = coord[1]
                    quota = coord[2]
                    # print(geom)
                    # attribute
                    prop = feat_obj["features"][i]["properties"]
                    # print(prop)
                    # attachments
                    attachments = []
                    descrizione = []
                    for a in feat_obj["features"][i]["properties"]["attachments"]:
                        # print(a)
                        attachments.append(a['filename'])
                        descrizione.append(a['descrizione'])
                    # id
                    id = feat_obj["features"][i]["id"]
                    # print(id)
                    # type
                    typ = feat_obj["features"][i]["type"]
                    # print(typ)

                    data_item.append(prop['codice_identificativo_della_cav'])
                    data_item.append(prop['codice_SSI'])
                    data_item.append(prop['regione'])
                    data_item.append(prop['provincia'])
                    data_item.append(prop['comune'])
                    data_item.append(prop['localit_frazionevia'])
                    data_item.append(prop['tipologia_primaria'])
                    data_item.append(prop['tipologia'])
                    data_item.append(prop['denominazione_comunemente_usata'])
                    if prop['note_descrittive'] is not None:
                        note_descr = prop['note_descrittive'].translate(escapes)
                    else:
                        note_descr = ''

                    k = note_descr.find("Bibliografia")
                    if k < 0:
                        note_descrittive = note_descr
                        riferimenti_bibliografici = ""
                    else:
                        note_descrittive = note_descr[0:k]
                        riferimenti_bibliografici = note_descr[k:len(note_descr)]

                    data_item.append(note_descrittive)
                    data_item.append(prop['data_di_prima_compilazione'])
                    data_item.append(prop['data_ultimo_aggiornamento'])
                    data_item.append(prop['created_user'])
                    data_item.append(prop['created_date'])
                    data_item.append(prop['last_edited_user'])
                    data_item.append(prop['last_edited_date'])
                    data_item.append(str(long))
                    data_item.append(str(lati))
                    data_item.append(str(quota))

                    if len(attachments) > 0:
                        if len(attachments[0].strip()):
                            data_item.append(path_images + '/' + attachments[0])
                            data_item.append(descrizione[0])
                    else:
                        data_item.append("")
                        data_item.append("")

                    if len(attachments) > 1:
                        if len(attachments[1].strip()):
                            data_item.append(path_images + '/' + attachments[1])
                            data_item.append(descrizione[1])
                    else:
                        data_item.append("")
                        data_item.append("")

                    data_item.append(riferimenti_bibliografici)

                    count = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(count)
                    for i in range(0, len(data_item)):
                        self.tableWidget.setItem(count, i, QTableWidgetItem(data_item[i]))

                f.close()
                self.buttonSave.setEnabled(True)
            except Exception as err:
                print(err)
                f.close()
        else:
            pass

    def SaveGeoJsonFile(self):
        arcpy.env.workspace = gdb
        # remove old cavita e crea new cavita
        out_sr = arcpy.SpatialReference("WGS 1984")
        if arcpy.Exists(fc):
            arcpy.Delete_management(fc, "")
            print(fc + "--> cancellata ....")

        geom = arcpy.Describe(fc_template).shapeType
        arcpy.CreateFeatureclass_management(gdb, fc, geom, fc_template, spatial_reference=out_sr)
        print(fc + "--> creata ....")

        # elenco campi mappati
        source = []
        for k in mapping_item:
            source.append(mapping_item[k])
        print(source)

        # import dei dati
        campi_data = ['data_di_prima_compilazione', 'data_ultimo_aggiornamento', 'created_date', 'last_edited_date']

        model = self.tableWidget.model()
        columnCount = model.columnCount()
        rowCount = model.rowCount()
        print(rowCount)
        for row in range(model.rowCount()):
            row_data = {}
            for column in range(columnCount):
                index = model.index(row, column)
                text = str(model.data(index))
                row_data[source_item[column]] = text

            # print(row_data)
            # mapping
            row = []
            for k in mapping_item:
                if k in campi_data:
                    row.append(ParseDateTime(row_data[k]))
                else:
                    row.append(row_data[k])
            print(row)

            # insert data
            with arcpy.da.InsertCursor(fc, ['SHAPE@'] + source) as irows:
                _lon = float(row_data['latitudine'])
                _lat = float(row_data['longitudine'])
                esri_json = {
                    "x": _lon,
                    "y": _lat,
                    "spatialReference": {
                        "wkid": 4326}}
                point = arcpy.AsShape(esri_json, True)
                irows.insertRow([point] + [row[i] for i in range(0, len(row))])

        print('done')
        self.buttonPortal.setEnabled(True)

    def SendToPortal(self):
        from arcgis.gis import GIS
        # Lettura file di config
        sys.dont_write_bytecode = True
        cfg = ConfigParser()
        cfg.read('./CONFIG.ini')
        url_gis = cfg.get('PORTAL', 'INDIRIZZO_PORTAL')
        user = cfg.get('PORTAL', 'UTENTE')
        pwd = cfg.get('PORTAL', 'PASSWORD')
        gis = GIS(url_gis, user, pwd)

        #search_result = gis.content.search("Cavità artificiali v3.1C", "Feature Layer")
        search_result = gis.content.search("geodatabase_cavita_test_gdb", "Feature Layer")

        if len(search_result) > 0:
            arcpy.env.workspace = gdb
            if arcpy.Exists(fc):
                cavita_item = search_result[0]
                cavita_fl = cavita_item.layers[0]
                print(cavita_fl)
                with arcpy.da.SearchCursor(fc, final_item) as cursor:

                    # coordinate della cavita
                    for row in cursor:
                        for pnt in row[0]:
                            lonp = pnt.X
                            latp = pnt.Y

                        record_dict = {
                            "attributes":
                                {
                                    "codice_identificatico_catasto_s" : row[1],
                                    "denominazione_comunemente_usata" : row[2],
                                    "data_di_prima_compilazione" : row[3],
                                    "data_ultimo_aggiornamento" : row[4],
                                    "regione" : row[5],
                                    "provincia" : row[6],
                                    "comune" : row[7],
                                    "localit_frazionevia" : row[8],
                                    "latitudine_dd" : row[9],
                                    "longitudine_dd" : row[10],
                                    "tipologia_primaria" : row[11],
                                    "tipologia" : row[12],
                                    "note_generali" : row[13],
                                    "riferimenti_bibliografici" : row[14],
                                    "created_date" : row[15],
                                    "created_user" : row[16],
                                    "last_edited_date" : row[17],
                                    "last_edited_user" : row[18],
                                    "quota_altimetrica" : row[19]
                                },
                            "geometry": {"x": lonp, "y": latp, "spatialReference": {"wkid": 4326}}
                        }
                        new_record = cavita_fl.edit_features(adds=[record_dict])
                        rec = new_record['addResults']
                        rec_dict = rec[0]
                        idobj = rec_dict['objectId']
                        print("insert record id: " + str(idobj))

                        # add attach
                        if isNotBlank(row[20]):
                            print("insert attach --> " + row[20])
                            cavita_fl.attachments.add(idobj, row[20])
                        if isNotBlank(row[22]):
                            print("insert attach --> " + row[22])
                            cavita_fl.attachments.add(idobj, row[22])

                    # stampa il numero di elementi inseriti
                    print(cavita_fl.query(return_count_only=True))

            else:
                print("Errore: la feature class  " + fc + " non esiste!")
                return

        # if len(search_result) > 0:
        #     cavita_item = search_result[0]
        #     print(cavita_item)
        #
        #     # access the item's feature layers
        #     cavita_layer = cavita_item.layers[0]
        #     print(cavita_layer)
        #     print(cavita_layer.properties.capabilities)

            # stampa dei nome campi
            # for f in cavita_layer.properties.fields:
            #     print(f['name'])

            # query_result1 = cavita_layer.query(where='objectid<10', out_fields='codice_identificatico_catasto_s')
            # print(len(query_result1.features))
            # if len(query_result1.features) > 0:
            #     for f in query_result1.features:
            #         print(f.attributes['codice_identificatico_catasto_s'])
                    # list_attach = cavita_layer.attachments.get_list(oid=f.attributes['objectid'])
                    # for a in list_attach:
                    #     print(a['name'])

            # cavita_fset = cavita_layer.query()
            # print(cavita_fset.sdf)

        # else:
        #     print("Feature Layer non trovato ...")

    def print_row(self):
        print("Stampa row")
        rows = {index.row() for index in self.tableWidget.selectionModel().selectedIndexes()}

        output = []
        for row in rows:
            row_data = []
            for column in range(self.tableWidget.model().columnCount()):
                index = self.tableWidget.model().index(row, column)
                row_data.append(index.data())
            output.append(row_data)
        print(output)

        dialog = Ui_myDialog(output)
        dialog.show()
        dialog.exec()

    def closeForm(self):
        exit(0)


# variabili globali
path_images = ''
fc = ''
fc_template = ''
gdb = ''


def ParseDateTime(txt):
    import datetime
    format1 = '%Y-%m-%dT%H:%M:%S'
    dt = datetime.datetime.strptime(txt, format1)
    return dt

def isBlank (myString):
    return not (myString and myString.strip())

def isNotBlank (myString):
    return bool(myString and myString.strip())

if __name__ == "__main__":
    # Lettura file di config

    cfg = ConfigParser()
    cfg.read('./CONFIG.ini')
    url_gis = cfg.get('PORTAL', 'INDIRIZZO_PORTAL')
    user = cfg.get('PORTAL', 'UTENTE')
    pwd = cfg.get('PORTAL', 'PASSWORD')
    path_images = cfg.get('DATI', 'PATH')
    fc = cfg.get('FEATURE CLASS', 'FC_CAVITA')
    fc_template = cfg.get('FEATURE CLASS', 'FC_TEMPLATE')
    gdb = cfg.get('GEODATABASE', 'GDB')

    # start applicazione
    app = QApplication([])
    window = Widget()
    window.show()
    app.exec()
