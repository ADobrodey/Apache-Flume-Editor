import os
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox, QLineEdit, QGridLayout


class ManageProperties(QDialog):
    def __init__(self, flume_object, parent=None):
        super(ManageProperties, self).__init__(parent)
        self.cb_component_type = QComboBox()
        self.new_properties = {}
        self.flume_object = flume_object
        if not flume_object.managed:
            self.get_properties()
        else:
            self.manage_properties()

    # noinspection PyUnresolvedReferences
    def manage_properties(self):
        self.update()
        self.setWindowTitle('Properties:')
        layout = QGridLayout()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setDefault(True)

        for idx, prop in enumerate(sorted(self.flume_object.properties.keys())):
            label = QLabel(prop + ':')
            editor = QLineEdit(self.flume_object.properties[prop]["value"])
            if prop == "type":
                editor.setReadOnly(True)
            if self.flume_object.properties[prop]["required"]:
                label.setText(prop + ":*")
                pass  # label.setFont(QFont) TODO
            editor.setToolTip(self.flume_object.properties[prop]["description"])
            editor.setToolTipDuration(-1)

            self.new_properties[prop] = editor

            label.setBuddy(self.new_properties[prop])
            layout.addWidget(label, idx, 0)
            layout.addWidget(self.new_properties[prop], idx, 1)

        layout.addWidget(button_box)
        self.setLayout(layout)

        button_box.accepted.connect(self.accept_prop)
        button_box.rejected.connect(self.reject)

    def accept_prop(self):
        for prop in self.new_properties.keys():
            self.flume_object.properties[prop]["value"] = self.new_properties[prop].text()

        super().accept()

    # noinspection PyUnresolvedReferences
    def get_properties(self):
        self.setWindowTitle('Component type')

        layout = QVBoxLayout()
        label = QLabel()
        label.setText('Component type:')

        # combo_box.setEditable(True)
        # print(self.flume_object.component)
        for f in os.listdir('properties/' + self.flume_object.component):
            self.cb_component_type.addItem(f[:f.find(".")])

        # self.cb_component_type.addItems('avro thrift'.split())

        button_box1 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box1.button(QDialogButtonBox.Ok).setDefault(True)

        layout.addWidget(label)
        layout.addWidget(self.cb_component_type)
        layout.addWidget(button_box1)
        self.setLayout(layout)
        self.resize(200, 100)

        button_box1.accepted.connect(self.properties_chosen)
        button_box1.rejected.connect(self.reject)

    def properties_chosen(self, component_type=None, child=True):
        if not component_type:
            component_type = self.cb_component_type.currentText()
        self.flume_object.load_default_properties(component_type)
        self.flume_object.managed = True
        super().accept()
        if child:
            ManageProperties(self.flume_object).exec_()
