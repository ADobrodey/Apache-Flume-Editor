import os
from PyQt5.QtWidgets import QFileDialog
from flume.manage_properties import ManageProperties


class FlumeConfig(object):
    def __init__(self, flume_menu):
        self.menu = flume_menu

    def load_config(self):
        # noinspection PyCallByClass
        filename = QFileDialog.getOpenFileName(QFileDialog(), "Open config file", os.getenv('Home'))
        with open(filename[0], "r") as config_file:
            config = self.parse_config(config_file)
            # TODO print(config)
            self.procedure_config(config)

    # noinspection PyMethodMayBeStatic
    def parse_config(self, config_file):
        comment_char = '#'
        option_char = '='
        agents = {}
        for line in config_file:
            if comment_char in line:
                line, comment = line.split(comment_char, 1)
            if option_char in line:
                option, values = line.split(option_char, 1)
                option = option.strip()
                values = values.strip()

                def rpad(length, seq, padding=None):
                    return tuple(seq) + tuple((length - len(seq)) * [padding])

                (agent, component, name, flume_property) = rpad(4, option.split(".", 3))
                if not agent in agents.keys():
                    agents[agent] = {"sources": {}, "channels": {}, "sinks": {}, "connections": {}}

                if not name:
                    for value in values.split():
                        agents[agent][component][value] = {}
                else:

                    if flume_property == 'channel' or flume_property == 'channels':
                        for value in values.split():
                            if value not in agents[agent]["connections"].keys():
                                agents[agent]["connections"][value] = (name,)
                            else:
                                agents[agent]["connections"][value] += (name,)
                                # agents[agent]["connections"][value].extend(name)

                    else:
                        try:
                            agents[agent][component][name][flume_property] = values
                        except KeyError:
                            print("Unknown properties:", agent, component, name, flume_property, values)  # TODO

        return agents

    def procedure_config(self, config):
        items = {"channels": ["channel", 1], "sinks": ["sink", 2],
                 "sources": ["source", 0]}

        for agent in config.keys():
            components = {}
            for component in config[agent].keys():
                if component != "connections":
                    xy = {"sources": [300, 300], "channels": [600, 300], "sinks": [900, 300]}
                    for name in config[agent][component].keys():
                        new_item = self.proceed_component(name, items[component][0], config[agent][component][name],
                                                          xy[component][0], xy[component][1])
                        xy[component][1] += 250
                        components[name] = (new_item, items[component][1])

            for connection in config[agent]["connections"]:
                if not connection in components.keys():
                    continue
                for connector in config[agent]["connections"][connection]:
                    if not connector in components.keys():
                        break
                    if components[connector][1] < components[connection][1]:
                        start_item = components[connector][0]
                        end_item = components[connection][0]
                    else:
                        start_item = components[connection][0]
                        end_item = components[connector][0]

                    self.menu.scene.add_arrow(start_item, end_item)

    def proceed_component(self, name, component, config, x, y):
        new_item = self.menu.scene.insert_item(item_type=component,
                                               x=x, y=y, text=name)
        ManageProperties(new_item.flume_object).properties_chosen(config['type'], False)

        for prop in config:
            if prop in new_item.flume_object.properties.keys():
                new_item.flume_object.properties[prop]['value'] = config[prop]

        return new_item
